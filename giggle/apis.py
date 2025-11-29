from decouple import config
import openai
import random

openai.api_key = config("CHATGPT_API_KEY")

# Personas for different comedian styles
PERSONAS = {
    "dad": "You are a cheesy dad comedian. Make lighthearted puns and wholesome punchlines.",
    "sarcastic": "You are a very sarcastic comic with dry, witty one-liners.",
    "roast": "You are an insult comic. Roast the subject, but keep it within tasteful bounds.",
    "haiku": "You are a poet who writes funny haikus about the subject (3 lines).",
    "witty": "You are a clever stand-up comedian who writes concise, punchy jokes.",
}

# Small set of random modifiers to keep repeated queries fresh
MODIFIERS = [
    "Include a vegetable in the punchline.",
    "Make a reference to 90s pop culture.",
    "Keep it very short.",
    "End with a rhetorical question.",
]


def get_giggle_result(query, style="witty"):
    instruction = PERSONAS.get(style, PERSONAS["witty"])

    # Add a random modifier for variety on witty style
    random_modifier = ""
    if style == "witty":
        random_modifier = random.choice(MODIFIERS)

    user_prompt = f"Topic: {query}. {random_modifier}".strip()

    try:
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            n=1,
            temperature=0.65,
            max_tokens=200,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": user_prompt},
            ],
        )
        return result.choices[0].message.content.strip()

    except openai.error.RateLimitError as e:
        print(f"OpenAI RateLimitError: {e}")
        return 1
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return 1

