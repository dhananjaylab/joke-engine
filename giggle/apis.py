from decouple import config
from decouple import config
import openai

openai.api_key = config("CHATGPT_API_KEY")

# Refined system instruction for better, consistent output
SYSTEM_INSTRUCTION = (
    "You are a witty comedian. When given a subject, generate a short, punchy joke (max 4 lines). "
    "Do not use introductions like 'Here is a joke'. Go straight to the punchline."
)

def get_giggle_result(query):
    try:
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            n=1,
            temperature=0.7,
            max_tokens=200,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": f"Tell me a joke about: {query}"},
            ],
        )
        return result.choices[0].message.content

    except openai.error.RateLimitError as e:
        print(f"OpenAI RateLimitError: {e}")
        return 1
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return 1

