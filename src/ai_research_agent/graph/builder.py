from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from ai_research_agent.graph.state import (
    ResearchState,
)

from ai_research_agent.graph.nodes.planner_node import (
    planner_node,
)

from ai_research_agent.graph.nodes.executor_node import (
    executor_node,
)

from ai_research_agent.graph.nodes.extraction_node import (
    extraction_node,
)

from ai_research_agent.graph.nodes.memory_node import (
    memory_node,
)

from ai_research_agent.graph.nodes.reasoning_node import (
    reasoning_node,
)

from ai_research_agent.graph.nodes.memory_storage_node import (
    memory_storage_node,
)

from ai_research_agent.graph.nodes.report_node import (
    report_node,
)

from ai_research_agent.graph.nodes.pdf_node import (
    pdf_node,
)


def build_graph():
    """Create and compile the sequential research workflow."""

    graph = StateGraph(ResearchState)

    graph.add_node(
        "planner",
        planner_node,
    )

    graph.add_node(
        "executor",
        executor_node,
    )

    graph.add_node(
        "extraction",
        extraction_node,
    )

    graph.add_node(
        "memory",
        memory_node,
    )

    graph.add_node(
        "reasoning",
        reasoning_node,
    )

    graph.add_node(
        "memory_storage",
        memory_storage_node,
    )

    graph.add_node(
        "report",
        report_node,
    )

    graph.add_node(
        "pdf",
        pdf_node,
    )

    graph.add_edge(
        START,
        "planner",
    )

    graph.add_edge(
        "planner",
        "executor",
    )

    graph.add_edge(
        "executor",
        "extraction",
    )

    graph.add_edge(
        "extraction",
        "memory",
    )

    graph.add_edge(
        "memory",
        "reasoning",
    )

    graph.add_edge(
        "reasoning",
        "memory_storage",
    )

    graph.add_edge(
        "memory_storage",
        "report",
    )

    graph.add_edge(
        "report",
        "pdf",
    )

    graph.add_edge(
        "pdf",
        END,
    )

    return graph.compile()
