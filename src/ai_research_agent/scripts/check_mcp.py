import asyncio

from ai_research_agent.mcp_client.client import MCPClient


async def main():
    """Run a small Tavily MCP search as an integration check."""

    client = MCPClient()

    result = await client.search(
        query="Latest AI Agent frameworks",
        max_results=3,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
