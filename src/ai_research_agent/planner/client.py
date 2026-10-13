import os

from dotenv import load_dotenv
from litellm import acompletion


load_dotenv()


async def generate(messages):
    """Return a completion for the supplied chat messages."""

    response = await acompletion(
        model=os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-6"),
        messages=messages,
    )

    return response.choices[0].message.content
