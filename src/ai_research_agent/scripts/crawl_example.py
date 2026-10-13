import asyncio

from ai_research_agent.mcp_client.crawl_client import CrawlClient


async def main():
    """Print a short sample crawl result."""

    crawler = CrawlClient()

    result = await crawler.crawl("https://langchain.com")

    print(result[:2000])


if __name__ == "__main__":
    asyncio.run(main())
