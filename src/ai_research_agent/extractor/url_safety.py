import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit


async def is_public_http_url(url: str) -> bool:
    """Reject non-HTTP URLs and hosts resolving to non-public IP addresses."""
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return False

    if (
        parsed.scheme not in {"http", "https"}
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 80, 443}
    ):
        return False

    hostname = hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith((".localhost", ".local")):
        return False

    try:
        address = ipaddress.ip_address(hostname)
        return address.is_global
    except ValueError:
        pass

    try:
        records = await asyncio.to_thread(
            socket.getaddrinfo,
            hostname,
            port or (443 if parsed.scheme == "https" else 80),
            0,
            socket.SOCK_STREAM,
        )
    except (OSError, socket.gaierror):
        return False

    addresses = {record[4][0] for record in records}
    if not addresses:
        return False

    try:
        return all(ipaddress.ip_address(address).is_global for address in addresses)
    except ValueError:
        return False
