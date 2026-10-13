from crawl4ai import AsyncWebCrawler


class CrawlClient:
    """Fetch a webpage as Markdown using Crawl4AI."""

    async def crawl(self, url: str) -> str:
        """Return the rendered Markdown content for a URL."""

        async with AsyncWebCrawler() as crawler:

            result = await crawler.arun(url=url)

            return result.markdown or ""
