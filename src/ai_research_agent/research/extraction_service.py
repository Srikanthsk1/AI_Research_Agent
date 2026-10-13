import asyncio

from ai_research_agent.executor.result_processor import (
    ResultProcessor,
)

from ai_research_agent.extractor.crawl4ai_extractor import (
    Crawl4AIExtractor,
)
from ai_research_agent.extractor.url_safety import is_public_http_url

from ai_research_agent.summarizer.service import (
    SummarizerService,
)

from ai_research_agent.research.evidence import (
    Evidence,
)

from ai_research_agent.utils.logger import (
    logger,
)


class ExtractionService:
    """Extract and summarize pages discovered by the search executor."""

    def __init__(self):
        """Initialize webpage extraction, summarization, and collection."""
        self.extractor = Crawl4AIExtractor()

        self.summarizer = SummarizerService()

    async def process_url(
        self,
        url: str,
        semaphore: asyncio.Semaphore,
    ):
        """Extract and summarize one URL under the concurrency limit."""

        async with semaphore:

            logger.info(f"Extracting: {url}")

            try:
                if not await is_public_http_url(url):
                    logger.warning(f"Skipping non-public or invalid URL: {url}")
                    return None

                content = await self.extractor.extract(url)

                if not content:

                    logger.warning(f"No content extracted from {url}")

                    return None

                if len(content.strip()) < 300:

                    logger.warning(f"Skipping short page: {url}")

                    return None

                logger.info(f"Extracted {len(content)} characters")

                summary = await self.summarizer.summarize(content)

                logger.info(f"Summary size: {len(summary)}")

                return Evidence(
                    source_url=url,
                    content=summary,
                )

            except Exception as e:

                logger.exception(f"Failed to extract {url}: {e}")

                return None

    async def extract(
        self,
        task_results: dict,
        max_urls: int = 10,
        concurrency: int = 5,
    ):
        """Process search results and return URLs plus fresh evidence."""

        logger.info("Processing search results...")

        urls = []

        for result in task_results.values():

            try:

                text = result.content[0].text

                extracted_urls = ResultProcessor.extract_urls(text)

                urls.extend(extracted_urls)

            except Exception as e:

                logger.warning(f"Failed to process search result: {e}")

        urls = list(dict.fromkeys(urls))

        logger.info(f"Found {len(urls)} clean URLs")

        logger.info(f"Starting parallel extraction for top {max_urls} URLs")

        semaphore = asyncio.Semaphore(concurrency)

        tasks = [
            self.process_url(
                url,
                semaphore,
            )
            for url in urls[:max_urls]
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        fresh_evidences = []

        for result in results:

            if isinstance(
                result,
                Evidence,
            ):

                fresh_evidences.append(result)

        logger.success("Parallel extraction completed.")

        logger.info(f"Collected {len(fresh_evidences)} evidence documents")

        return (
            urls,
            fresh_evidences,
        )
