from ai_research_agent.llm.client import LLMClient

from ai_research_agent.summarizer.prompt import SUMMARIZER_SYSTEM_PROMPT


class SummarizerService:
    """Summarize extracted webpage content with the configured LLM."""

    def __init__(self):
        """Create an LLM client for summarization requests."""
        self.client = LLMClient()

    async def summarize(
        self,
        content: str,
    ) -> str:
        """Return a concise summary while preserving factual details."""
        prompt = f"""
Summarize the following content.

CONTENT:

{content}
"""

        response = await self.client.generate(
            system_prompt=SUMMARIZER_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        return response
