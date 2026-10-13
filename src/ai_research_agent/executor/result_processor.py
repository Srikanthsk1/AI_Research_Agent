import re
from urllib.parse import urlsplit


class ResultProcessor:
    """Extract, filter, and rank candidate URLs from search output."""

    URL_PATTERN = re.compile(r"https?://[^\s<>\"]+")

    SKIP_EXTENSIONS = (
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".svg",
        ".ico",
        ".pdf",
        ".zip",
        ".css",
        ".js",
        ".woff",
        ".woff2",
        ".ttf",
        ".xml",
    )

    SKIP_DOMAINS = (
        "youtube.com",
        "youtu.be",
        "twitter.com",
        "x.com",
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "tiktok.com",
        "pinterest.com",
        "wiktionary.org",
        "tinyurl.com",
        "bit.ly",
        "goo.gl",
    )

    PRIORITY_KEYWORDS = (
        "docs",
        "documentation",
        "github",
        "blog",
        "guide",
        "tutorial",
        "learn",
        "research",
        "article",
    )

    @classmethod
    def extract_urls(
        cls,
        text: str,
    ) -> list[str]:
        """Return unique, cleaned URLs ordered by source preference."""
        urls = cls.URL_PATTERN.findall(text)

        cleaned_urls = []

        for url in urls:

            url = cls.clean_url(url)

            if not url.startswith(
                (
                    "http://",
                    "https://",
                )
            ):
                continue

            if cls.should_skip(url):
                continue

            cleaned_urls.append(url)

        # Remove duplicates
        cleaned_urls = list(dict.fromkeys(cleaned_urls))

        # Rank URLs
        cleaned_urls.sort(
            key=cls.rank_url,
            reverse=True,
        )

        return cleaned_urls

    @staticmethod
    def clean_url(
        url: str,
    ) -> str:
        """Remove trailing punctuation, citation markers, and fragments."""
        url = url.strip()

        url = url.rstrip(").,;:]>}\"'")

        url = re.sub(
            r"\[\d+\]$",
            "",
            url,
        )

        # Remove fragments
        url = url.split("#")[0]

        return url

    @classmethod
    def should_skip(
        cls,
        url: str,
    ) -> bool:
        """Return whether a URL points to a skipped domain or asset."""
        try:
            parsed = urlsplit(url)
            hostname = (parsed.hostname or "").lower().rstrip(".")
        except ValueError:
            return True

        if parsed.scheme not in {"http", "https"} or not hostname:
            return True

        # Skip social media and low-value domains
        for domain in cls.SKIP_DOMAINS:

            if hostname == domain or hostname.endswith(f".{domain}"):
                return True

        # Skip Next.js image proxy URLs
        if "/_next/image" in parsed.path.lower():
            return True

        # Skip common static assets
        return parsed.path.lower().endswith(cls.SKIP_EXTENSIONS)

    @classmethod
    def rank_url(
        cls,
        url: str,
    ) -> int:
        """Score a URL using lightweight source and path heuristics."""
        score = 0

        lower = url.lower()

        for keyword in cls.PRIORITY_KEYWORDS:

            if keyword in lower:
                score += 5

        if "github.com" in lower:
            score += 10

        if "docs." in lower:
            score += 8

        if "/docs/" in lower:
            score += 8

        if "medium.com" in lower:
            score += 4

        if "nature.com" in lower:
            score += 15

        if "arxiv.org" in lower:
            score += 15

        if "ieee.org" in lower:
            score += 15

        if ".gov" in lower:
            score += 15

        if ".edu" in lower:
            score += 15

        return score
