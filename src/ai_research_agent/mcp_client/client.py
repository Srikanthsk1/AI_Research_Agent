import os

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()


class MCPClient:
    """Create short-lived stdio sessions for Tavily MCP tool calls."""

    def __init__(self):
        """Read Tavily credentials and prepare server launch settings."""
        self.server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "tavily-mcp",
            ],
            env={
                "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
            },
        )

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        """Start the MCP server, invoke a tool, and return its result."""

        async with stdio_client(self.server_params) as (
            read_stream,
            write_stream,
        ), ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments,
            )

            return result

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ):
        """Run Tavily search with a query and result limit."""
        return await self.call_tool(
            tool_name="tavily_search",
            arguments={
                "query": query,
                "max_results": max_results,
            },
        )
