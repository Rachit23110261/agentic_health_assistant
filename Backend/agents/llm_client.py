
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI, APIError
import traceback

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1"

client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_API_URL
)


async def chat_with_llm(messages, tools=None, tool_choice="auto", model="llama3-70b-8192"):
    try:
        print("Sending messages to LLM:")
        for m in messages:
            if "content" in m:
                print(f"  - {m['role']}: {m['content'][:80]}...")

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
        )

        print("LLM response received.")
        return response

    except APIError as api_err:
        print("API Error:", api_err)
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"API error: {str(api_err)}"
                }
            }]
        }

    except Exception as e:
        print("LLM call failed:", e)
        traceback.print_exc()
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"LLM error: {str(e)}"
                }
            }]
        }
