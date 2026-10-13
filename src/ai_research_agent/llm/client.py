import os

from dotenv import load_dotenv
from litellm import acompletion

load_dotenv()


class LLMClient:
    """Provide asynchronous completions through LiteLLM."""

    def __init__(self):
        """Read the configured model name from the environment."""
        self.model = os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-6")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Send system and user prompts and return the response text."""
        response = await acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content
