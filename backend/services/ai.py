import json
from openai import AsyncOpenAI
from core.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)

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
    return result.choices[0].message.content.strip()


async def stream_joke(query: str, style: str = "witty"):
    """Async generator yielding SSE-formatted token chunks."""
    instruction = PERSONAS.get(style, PERSONAS["witty"])
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
            yield f"data: {delta.replace(chr(10), ' ')}\n\n"
    yield "data: [DONE]\n\n"


async def heckle(user_joke: str) -> str:
    """Use Groq LLM for faster, funnier roasts."""
    # Use Groq if available, fallback to OpenAI
    active_client = groq_client if groq_client else client
    model = "groq/compound-mini" if groq_client else "gpt-4o-mini"
    
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
    return result.choices[0].message.content.strip()


async def explain(joke_text: str) -> str:
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
    return result.choices[0].message.content.strip()


async def score_joke(joke_text: str) -> dict | None:
    """Rate joke 1-10 on 3 dimensions. Returns dict or None."""
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
        return json.loads(result.choices[0].message.content)
    except Exception as e:
        print(f"Score failed: {e}")
        return None


async def generate_audio(text: str) -> bytes:
    response = await client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
        response_format="mp3",
    )
    return response.content


async def embed_text(text: str) -> list[float]:
    """Generate text embedding for semantic dedup (Phase 6)."""
    result = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return result.data[0].embedding
