import os

from ai_research_agent.planner.schemas import (
    ResearchPlan,
)

from ai_research_agent.executor.dispatcher import (
    TaskDispatcher,
)

from ai_research_agent.utils.logger import (
    logger,
)


class ExecutorService:
    """Execute research-plan tasks and collect their results."""

    def __init__(self):
        """Initialize the tool dispatcher."""
        self.dispatcher = TaskDispatcher()

    async def execute(
        self,
        research_plan: ResearchPlan,
    ):
        """Execute plan tasks and collect successful tool responses."""
        """Run each task and return completed IDs with tool results."""
        logger.info("Starting task execution")

        completed_tasks = []

        task_results = {}

        for task in research_plan.tasks:

            logger.info(f"Executing Task {task.task_id}: {task.title}")

            try:
                if task.tool_name != "tavily_search":
                    raise ValueError(f"Unsupported tool: {task.tool_name}")

                arguments = task.tool_arguments.model_dump()
                configured_limit = min(
                    20,
                    max(1, int(os.getenv("MAX_SEARCH_RESULTS", "10"))),
                )
                arguments["max_results"] = min(
                    arguments["max_results"],
                    configured_limit,
                )
                result = await self.dispatcher.client.call_tool(
                    tool_name=task.tool_name,
                    arguments=arguments,
                )

                completed_tasks.append(task.task_id)

                task_results[task.task_id] = result

                logger.success(f"Task {task.task_id} completed successfully")

            except Exception as e:

                logger.exception(f"Task {task.task_id} failed: {e}")

        logger.success("Executor finished all tasks")

        return (
            completed_tasks,
            task_results,
        )
