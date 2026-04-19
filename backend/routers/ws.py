from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.database import AsyncSessionLocal
from core.logging import get_logger
from services.ai import stream_joke
from services.joke_store import save_joke

router = APIRouter(prefix="/ws", tags=["websocket"])
log = get_logger("routers.ws")


@router.websocket("/joke")
async def joke_ws(websocket: WebSocket):
    await websocket.accept()
    await log.info("ws_connected", "WebSocket client connected")

    try:
        while True:
            data = await websocket.receive_json()
            query = str(data.get("query", "")).strip()[:100]
            style = str(data.get("style", "witty"))
            session_key = str(data.get("session_key", "")) or None

            if not query:
                await websocket.send_json({"type": "error", "message": "Empty query"})
                continue

            await log.info(
                "ws_joke_start",
                f"WS joke stream started: query={query!r} style={style}",
                details={"query": query, "style": style},
                session_key=session_key,
            )

            tokens: list[str] = []
            try:
                async for chunk in stream_joke(query, style):
                    token = chunk.replace("data: ", "").strip()
                    if token == "[DONE]":
                        full_text = "".join(tokens)
                        await websocket.send_json({"type": "done", "full": full_text})

                        # Persist to Neon DB
                        if full_text:
                            async with AsyncSessionLocal() as db:
                                joke = await save_joke(
                                    db,
                                    query=f"{query} [{style}]",
                                    response=full_text,
                                    source="ai_websocket",
                                    session_key=session_key,
                                    enqueue_scoring=True,
                                )
                            await log.info(
                                "ws_joke_saved",
                                f"WS joke saved: id={joke.id}",
                                joke_id=joke.id,
                                session_key=session_key,
                                details={"query": query, "style": style},
                            )
                        break
                    tokens.append(token)
                    await websocket.send_json({"type": "token", "text": token})

            except Exception as exc:
                await log.error(
                    "ws_joke_error",
                    f"WS joke stream error for query={query!r}",
                    session_key=session_key,
                    exc=exc,
                )
                await websocket.send_json({"type": "error", "message": "Stream failed"})

    except WebSocketDisconnect:
        await log.info("ws_disconnected", "WebSocket client disconnected")
