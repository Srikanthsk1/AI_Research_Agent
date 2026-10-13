from ai_research_agent.planner.schemas import ResearchTask

from ai_research_agent.mcp_client.client import MCPClient


class TaskDispatcher:
    """Route a planned task to its named MCP tool."""

    def __init__(self):
        """Create the MCP client used for tool dispatch."""
        self.client = MCPClient()

    async def dispatch(
        self,
        task: ResearchTask,
    ):
        """Call the MCP tool declared by a research task."""
        if task.tool_name != "tavily_search":
            raise ValueError(f"Unsupported MCP tool: {task.tool_name}")

        return await self.client.call_tool(
            tool_name=task.tool_name,
            arguments=task.tool_arguments.model_dump(),
        )
