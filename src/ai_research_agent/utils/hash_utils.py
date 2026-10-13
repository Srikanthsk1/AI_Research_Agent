import hashlib


def generate_hash(
    text: str,
) -> str:
    """Return the SHA-256 hex digest for a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
