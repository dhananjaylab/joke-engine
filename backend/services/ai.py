import json
import time
from openai import AsyncOpenAI
from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)
log = get_logger("services.ai")

# Groq client for Reverse Heckler
groq_client = None
if settings.groq_api_key:
    groq_client = AsyncOpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

PERSONAS: dict[str, str] = {
    "witty": "You are a clever stand-up comedian. Write concise, punchy jokes.",
    "dad": "You are a cheesy dad comedian. Make lighthearted puns and wholesome punchlines.",
    "sarcastic": "You are a very sarcastic comic with dry, witty one-liners.",
    "roast": "You are an insult comic. Roast the subject, keep it within tasteful bounds.",
    "haiku": "You are a poet who writes funny haikus about the subject (3 lines, 5-7-5).",
    "brainrot": (
        "Write extremely unhinged, absurdist Gen-Z internet humor. "
        "Use brainrot language: skibidi, sigma, rizz, no cap, lowkey, bussin, Ohio, NPC, slay, based. "
        "Keep it chaotic, short, and funny. Maximum 2 sentences."
    ),
    "nocontext": (
        "Respond with ONLY the punchline or the single most absurd sentence about the topic. "
        "No setup. No explanation. Maximum 15 words. Confusing out of context."
    ),
    "emoji": (
        "Respond using ONLY emojis — no words or punctuation. "
        "Use 5 to 10 emojis to express a funny thought about the topic."
    ),
}


async def get_joke(query: str, style: str = "witty") -> str:
    """Single-shot joke generation. Returns full text."""
    instruction = PERSONAS.get(style, PERSONAS["witty"])
    start = time.perf_counter()
    await log.info(
        "ai_joke_start",
        f"Generating joke: query={query!r} style={style}",
        details={"query": query, "style": style, "model": "gpt-4o-mini"},
    )
    try:
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            n=1,
            temperature=0.65,
            max_tokens=200,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": f"Topic: {query}"},
            ],
        )
        text = result.choices[0].message.content.strip()
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "ai_joke_complete",
            f"Joke generated in {duration_ms}ms",
            details={
                "query": query,
                "style": style,
                "tokens_used": result.usage.total_tokens if result.usage else None,
                "preview": text[:80],
            },
            duration_ms=duration_ms,
        )
        return text
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "ai_joke_failed",
            f"OpenAI joke generation failed for query={query!r}",
            details={"query": query, "style": style},
            duration_ms=duration_ms,
            exc=exc,
        )
        raise


async def stream_joke(query: str, style: str = "witty"):
    """Async generator yielding SSE-formatted token chunks."""
    instruction = PERSONAS.get(style, PERSONAS["witty"])
    start = time.perf_counter()
    token_count = 0

    await log.info(
        "ai_stream_start",
        f"Starting SSE stream: query={query!r} style={style}",
        details={"query": query, "style": style},
    )
    try:
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            stream=True,
            temperature=0.65,
            max_tokens=200,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": f"Topic: {query}"},
            ],
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                token_count += 1
                yield f"data: {delta.replace(chr(10), ' ')}\n\n"
        yield "data: [DONE]\n\n"

        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "ai_stream_complete",
            f"SSE stream finished in {duration_ms}ms ({token_count} chunks)",
            details={"query": query, "style": style, "chunks": token_count},
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "ai_stream_failed",
            f"SSE stream failed for query={query!r}",
            details={"query": query, "style": style},
            duration_ms=duration_ms,
            exc=exc,
        )
        raise


async def heckle(user_joke: str) -> str:
    """Use Groq LLM for faster, funnier roasts."""
    active_client = groq_client if groq_client else client
    model = "llama-3.3-70b-versatile" if groq_client else "gpt-4o-mini"
    provider = "groq" if groq_client else "openai"
    start = time.perf_counter()

    await log.info(
        "ai_heckle_start",
        f"Heckle request via {provider}",
        details={"provider": provider, "model": model, "joke_preview": user_joke[:80]},
    )
    try:
        result = await active_client.chat.completions.create(
            model=model,
            temperature=0.8,
            max_tokens=200,
            messages=[
                {"role": "system", "content":
                    "You are a grumpy comedy club owner. Rate the joke out of 10, "
                    "then roast the user in a funny but not abusive way."},
                {"role": "user", "content": f"User joke: {user_joke}"},
            ],
        )
        text = result.choices[0].message.content.strip()
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "ai_heckle_complete",
            f"Heckle generated in {duration_ms}ms via {provider}",
            details={"provider": provider, "duration_ms": duration_ms},
            duration_ms=duration_ms,
        )
        return text
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "ai_heckle_failed",
            "Heckle generation failed",
            details={"provider": provider},
            duration_ms=duration_ms,
            exc=exc,
        )
        raise


async def explain(joke_text: str) -> str:
    start = time.perf_counter()
    await log.info("ai_explain_start", "Explain request", details={"preview": joke_text[:80]})
    try:
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=250,
            messages=[
                {"role": "system", "content":
                    "Explain the humor in the following joke in a strictly scientific, "
                    "dry, and over-analytical tone. Be precise and literal."},
                {"role": "user", "content": f"Joke: {joke_text}"},
            ],
        )
        text = result.choices[0].message.content.strip()
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "ai_explain_complete",
            f"Explanation generated in {duration_ms}ms",
            duration_ms=duration_ms,
        )
        return text
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error("ai_explain_failed", "Explain generation failed", duration_ms=duration_ms, exc=exc)
        raise


async def score_joke(joke_text: str) -> dict | None:
    """Rate joke 1-10 on 3 dimensions. Returns dict or None."""
    start = time.perf_counter()
    await log.debug("ai_score_start", "Scoring joke", details={"preview": joke_text[:80]})
    try:
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=60,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content":
                    'Rate the following joke 1-10 on three dimensions. '
                    'Return ONLY valid JSON: {"originality": N, "timing": N, "cleverness": N}'},
                {"role": "user", "content": f"Joke: {joke_text}"},
            ],
        )
        scores = json.loads(result.choices[0].message.content)
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "ai_score_complete",
            f"Joke scored in {duration_ms}ms: {scores}",
            details={"scores": scores},
            duration_ms=duration_ms,
        )
        return scores
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "ai_score_failed",
            "Joke scoring failed",
            duration_ms=duration_ms,
            exc=exc,
        )
        return None


async def generate_audio(text: str) -> bytes:
    start = time.perf_counter()
    await log.info("ai_tts_start", "TTS audio generation started", details={"text_length": len(text)})
    try:
        response = await client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text,
            response_format="mp3",
        )
        audio_bytes = response.content
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "ai_tts_complete",
            f"TTS audio generated in {duration_ms}ms ({len(audio_bytes)} bytes)",
            details={"bytes": len(audio_bytes), "text_length": len(text)},
            duration_ms=duration_ms,
        )
        return audio_bytes
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error("ai_tts_failed", "TTS audio generation failed", duration_ms=duration_ms, exc=exc)
        raise


async def embed_text(text: str) -> list[float]:
    """Generate text embedding for semantic dedup (Phase 6)."""
    start = time.perf_counter()
    try:
        result = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.debug(
            "ai_embed_complete",
            f"Embedding generated in {duration_ms}ms",
            duration_ms=duration_ms,
        )
        return result.data[0].embedding
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error("ai_embed_failed", "Embedding generation failed", duration_ms=duration_ms, exc=exc)
        raise
