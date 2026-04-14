from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.ai import stream_joke

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/joke")
async def joke_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            query = str(data.get("query", "")).strip()[:100]
            style = str(data.get("style", "witty"))

            if not query:
                await websocket.send_json({"type": "error", "message": "Empty query"})
                continue

            tokens: list[str] = []
            async for chunk in stream_joke(query, style):
                token = chunk.replace("data: ", "").strip()
                if token == "[DONE]":
                    await websocket.send_json({"type": "done", "full": "".join(tokens)})
                    break
                tokens.append(token)
                await websocket.send_json({"type": "token", "text": token})
    except WebSocketDisconnect:
        pass
