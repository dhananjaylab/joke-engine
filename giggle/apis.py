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


def generate_meme_image(joke_text):
    """Generate a cartoonish meme image URL for the provided joke text.

    Returns an image URL or None on failure.
    """
    try:
        # Prompt should avoid including text in the image; we want illustration only
        prompt = f"A funny, cartoonish digital art depiction of: {joke_text}. No text in the image. Bright colors, simple characters."
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return response['data'][0].get('url')
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None


def heckle_evaluation(user_joke):
    """Rate and roast the user's joke. Returns the assistant's reply."""
    system = (
        "You are a grumpy comedy club owner. The user will tell you a joke. Rate it out of 10, then roast the user in a funny but not abusive way."
    )
    try:
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            n=1,
            temperature=0.8,
            max_tokens=200,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"User joke: {user_joke}"},
            ],
        )
        return result.choices[0].message.content.strip()
    except Exception as e:
        print(f"Heckle failed: {e}")
        return "Sorry, I'm having trouble heckling right now."


def explain_joke_text(joke_text):
    """Return a dry, over-analytical explanation of why a joke is (or isn't) funny."""
    system = (
        "Explain the humor in the following joke in a strictly scientific, dry, and over-analytical tone. Be precise and literal."
    )
    try:
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            n=1,
            temperature=0.2,
            max_tokens=250,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Joke: {joke_text}"},
            ],
        )
        return result.choices[0].message.content.strip()
    except Exception as e:
        print(f"Explain failed: {e}")
        return "I couldn't generate an explanation right now."
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return 1

