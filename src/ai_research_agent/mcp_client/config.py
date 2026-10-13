from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


@dataclass
class MCPServerConfig:
    """Command and arguments required to start an MCP server."""

    name: str

    command: str

    args: list[str]
