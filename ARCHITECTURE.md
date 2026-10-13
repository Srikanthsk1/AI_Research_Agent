# Architecture

## Overview

The application is packaged as src/ai_research_agent and exposes a FastAPI service. LangGraph orchestrates each research request; workflow nodes read and update a shared ResearchState. Integrations are isolated behind service modules for search, extraction, memory, reasoning, and report generation.

## Runtime flow

    User query
        -> Planner (LLM completion and schema validation)
        -> Executor (Tavily MCP searches)
        -> Extraction (URL filtering, Crawl4AI fetch, LLM summaries)
        -> Memory retrieval (dense Sentence Transformers and sparse BM25 in Qdrant)
        -> Reasoning (evidence synthesis and citation checks)
        -> Memory storage (chunking, hashing, embeddings)
        -> Report generation (Markdown)
        -> PDF rendering (ReportLab)

The workflow definition is in src/ai_research_agent/graph/builder.py. State fields are described in src/ai_research_agent/graph/state.py; node adapters are in src/ai_research_agent/graph/nodes/.

## Package map

| Package | Responsibility |
| --- | --- |
| planner | Build and validate structured research plans |
| executor | Dispatch plan tasks and process search output |
| mcp_client | Start the Tavily MCP server and call its tools |
| extractor | Fetch webpage content using Crawl4AI |
| research | Extract URLs, summarize pages, and represent evidence |
| memory | Embed, store, deduplicate, and retrieve evidence chunks |
| reasoning | Synthesize evidence and validate citation indices |
| report | Generate Markdown and render a PDF |
| llm | Shared LiteLLM client and legacy report service |
| scripts | Manual integration and utility commands |

## Data and persistence

- Qdrant persists vectors in qdrant_db/ relative to the process working directory.
- PDF reports are written to reports/<run-id>.pdf and returned through the API.
- Log files are written to logs/research_agent.log.
- API credentials are loaded from the root .env file when the application starts from the repository directory.

These paths are local-development defaults, not configurable storage abstractions. The vector data and generated outputs are not part of the Python package.

## Entry points

- python main.py starts the local API from a source checkout.
- python -m ai_research_agent starts the API from the installed package.
- ai-research-agent starts the API through the console command provided by pyproject.toml.

Install the package in editable mode during development with:

    python -m pip install -e .

## Boundaries and limitations

Search tasks run sequentially. Page extraction uses bounded asynchronous concurrency. Source selection, extraction success, memory relevance, and model-generated summaries affect report quality. Citation-number checking ensures an index refers to supplied evidence, but does not independently verify that a source supports each claim.
