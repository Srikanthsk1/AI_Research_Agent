# AI Research Agent

An evidence-oriented research application that turns a research question into a cited Markdown report and PDF. LangGraph coordinates planning, Tavily search through MCP, webpage extraction, summarization, Qdrant memory, evidence synthesis, and report generation.

For the complete WSL/Linux setup and run steps for both the API and the standalone frontend, see [RUNNING_GUIDE.md](RUNNING_GUIDE.md).

## Prerequisites

- Python 3.10 or newer
- Node.js with npm/npx available on PATH (the Tavily MCP client starts its server with npx)
- An LLM provider API key supported by LiteLLM
- A Tavily API key

## Quick start

### 1. Open a terminal in the repository root

Run the following commands from the directory containing pyproject.toml and .env.example.

### 2. Create and activate a virtual environment

**Windows PowerShell**

    python -m venv .venv
    .venv\Scripts\Activate.ps1

If PowerShell blocks activation, use the virtual environment's interpreter directly with .venv\Scripts\python.exe.

**macOS or Linux**

    python3 -m venv .venv
    source .venv/bin/activate

### 3. Install the application

    python -m pip install --upgrade pip
    python -m pip install -e .

This installs the project using pyproject.toml and makes the ai-research-agent command available in the active environment. requirements.txt is also provided for environments that install dependencies from a requirements file.

### 4. Configure API credentials

Create a local .env file from the example.

**Windows PowerShell**

    Copy-Item .env.example .env

**macOS or Linux**

    cp .env.example .env

Edit .env and set at least:

- LLM_MODEL, for example anthropic/claude-sonnet-4-6
- The API key for that model provider (ANTHROPIC_API_KEY for the example above)
- TAVILY_API_KEY

Keep .env private and do not commit it.

### 5. Start the API

From the repository root, start the local API with:

    python main.py

The API listens on `http://127.0.0.1:8000` by default. You can also run `python -m ai_research_agent` or `ai-research-agent` after installation. Use `API_HOST` and `API_PORT` in `.env` to configure the bind address and port. Set `API_KEY` to require bearer authentication. For a browser app hosted on another origin, set `CORS_ORIGINS` to a comma-separated list of exact origins (for example, `http://localhost:5501`). Cross-origin access is disabled when this setting is empty.

### Use the standalone frontend

The small HTML/CSS/JavaScript client is in `frontend/`. Set `CORS_ORIGINS=http://localhost:5501` in `.env` and restart the API after changing it. In a second terminal, serve the frontend from the repository root:

```bash
python -m http.server 5501 --directory frontend
```

Open `http://localhost:5501`. The page submits to `/research/jobs`, polls for completion, and displays the report. The browser form includes an optional API key field for local development; do not embed a private API key in a public frontend.

Submit a research request:

```bash
curl -X POST http://127.0.0.1:8000/research -H "Content-Type: application/json" -d '{"query":"How are humanoid robots being used in manufacturing?"}'
```

Research requests also accept `research_depth` (`basic`, `intermediate`, or `deep`), `output_format` (`markdown`, `report`, or `json`), `max_sources` (1–100), and `include_citations` (boolean). For example:

```bash
curl -X POST http://127.0.0.1:8000/research -H "Content-Type: application/json" -d '{"query":"How are humanoid robots being used in manufacturing?","research_depth":"intermediate","output_format":"json","max_sources":6,"include_citations":true}'
```

`max_sources` is additionally capped by the server's `MAX_SEARCH_RESULTS` setting. JSON output is returned as a structured object in `report` and does not include a PDF URL; Markdown and report output include a PDF.

If `API_KEY` is set, include `-H "Authorization: Bearer YOUR_API_KEY"`. The synchronous endpoint returns the Markdown report, a run ID, the evidence count, and an absolute `pdf_url`.

For long-running integrations, submit an asynchronous job instead:

```bash
curl -X POST http://127.0.0.1:8000/research/jobs -H "Content-Type: application/json" -d '{"query":"How are humanoid robots being used in manufacturing?"}'
```

The `202 Accepted` response contains a `run_id` and `status_url`. Poll that URL with `GET` until `status` is `completed` or `failed`; on completion, the response includes the research result and its PDF URL. Job status is held in process memory, so a server restart clears polling state. `GET /` provides API discovery links, `GET /healthz` provides a basic health check, and `/docs` shows the interactive API schema. Binding to a non-local host requires `API_KEY`.

## What happens when it runs

1. The planner asks the configured language model for a structured research plan.
2. The executor runs the plan's Tavily search tasks through the MCP server.
3. Search output is filtered into candidate URLs; Crawl4AI fetches pages and the model summarizes them.
4. Relevant previous evidence is retrieved with dense semantic and sparse BM25 search, fused with reciprocal rank fusion in local Qdrant memory.
5. The reasoning step synthesizes evidence and builds numbered references.
6. New evidence is stored in memory, and the report is generated as Markdown.
7. ReportLab writes the PDF.

## Output and local data

Paths are relative to the current working directory (normally the repository root):

- PDF reports: reports/<run-id>.pdf (also available from the API)
- Qdrant memory: qdrant_db/
- Logs: logs/research_agent.log

These directories may contain research content and source URLs. Protect them according to the sensitivity of the data you investigate.

Hybrid memory uses a separate `research_memory_hybrid` collection. If your `.env` still sets `QDRANT_COLLECTION=research_memory`, change it to `research_memory_hybrid`. Existing dense-only points are not copied; ingest the source evidence again so Qdrant stores both vector types. FastEmbed may download the BM25 model assets the first time the application starts.

## Configuration

| Variable | Purpose | Example or default |
| --- | --- | --- |
| LLM_MODEL | LiteLLM model identifier | anthropic/claude-sonnet-4-6 |
| ANTHROPIC_API_KEY | Provider key when using the example model | Set in .env |
| TAVILY_API_KEY | Tavily search key | Set in .env |
| LOG_LEVEL | Console and file logging verbosity | INFO |
| MAX_PARALLEL_EXTRACTIONS | Maximum concurrent page extractions | 5 |
| MAX_SEARCH_RESULTS | Search result and page processing limit | 10 |
| API_HOST | API bind address; non-local binding requires API_KEY | 127.0.0.1 |
| API_PORT | API listening port | 8000 |
| API_KEY | Optional bearer token for research and PDF endpoints | Unset |
| CORS_ORIGINS | Comma-separated allowed browser origins | Unset (disabled) |
| QDRANT_PATH | Local Qdrant storage directory | ./qdrant_db |
| QDRANT_COLLECTION | Hybrid Qdrant collection used for research memory | research_memory_hybrid |
| QDRANT_SPARSE_MODEL | FastEmbed sparse retrieval model | Qdrant/bm25 |

## Manual utility scripts

After installation, run the included utilities as Python modules from the repository root. For example:

    python -m ai_research_agent.scripts.check_url_processor
    python -m ai_research_agent.scripts.check_mcp
    python -m ai_research_agent.scripts.crawl_example

The MCP and crawl examples require working credentials and internet access.

## Project structure

| Location | Responsibility |
| --- | --- |
| src/ai_research_agent/graph/ | LangGraph workflow, state, and node adapters |
| src/ai_research_agent/planner/ | Research plan schemas, prompts, and validation |
| src/ai_research_agent/executor/ | Planned task execution and URL processing |
| src/ai_research_agent/mcp_client/ | Tavily MCP and crawl clients |
| src/ai_research_agent/extractor/ | Webpage extraction |
| src/ai_research_agent/research/ | Evidence collection and extraction orchestration |
| src/ai_research_agent/memory/ | Embeddings, Qdrant persistence, and retrieval |
| src/ai_research_agent/reasoning/ | Evidence synthesis and citation checks |
| src/ai_research_agent/report/ | Markdown report and PDF generation |
| src/ai_research_agent/scripts/ | Manual integration and utility scripts |
| src/ai_research_agent/legacy/ | Older implementation retained for reference; not used by the main workflow |

## Security and limitations

Research queries are sent to Tavily. Prompts and extracted page text are sent to the configured LLM provider. Review their data handling terms before researching confidential material. Web content is untrusted input, and generated claims should be checked against cited sources before relying on or sharing a report.

The application currently uses a sample query, executes search tasks sequentially, and supports a limited subset of Markdown in PDF output. Citation indices are checked against supplied evidence, but sources are not independently verified.

## License

No LICENSE file is currently included. Add one before distributing this project under a specific license.
