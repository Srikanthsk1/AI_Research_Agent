from crawl4ai import AsyncWebCrawler

from ai_research_agent.utils.logger import logger


class Crawl4AIExtractor:
    """Extract readable Markdown from webpages with Crawl4AI."""

    async def extract(
        self,
        url: str,
    ) -> str:
        """Fetch and return page content, or an empty string on failure."""

        logger.info(f"Downloading page: {url}")

        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
            content = result.markdown or ""

        except Exception as e:

            logger.exception(f"Failed fetching or extracting {url}: {e}")

            return ""

        if not content:

            logger.warning(f"No readable content found: {url}")

            return ""

        logger.info(f"Extracted {len(content)} characters")

        return content
