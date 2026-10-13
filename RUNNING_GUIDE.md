# Running the AI Research Agent

This guide starts the Python API and the separate HTML/CSS/JavaScript frontend in WSL/Linux. The API runs on port `8000`; the frontend runs on port `5501`.

## 1. Open the project directory

In your WSL terminal:

```bash
cd "/mnt/c/Users/SRIKANTH_SK/Downloads/Reasearch Agent/ai-research-agent"
```

The project supports Python 3.10 through 3.13. `.python-version` selects Python 3.10.

## 2. Install the Python dependencies

The project dependencies are declared in `pyproject.toml`, so use `uv sync` instead of adding `requirements.txt` again:

```bash
uv sync
```

`uv sync` creates or updates the project virtual environment. To run Python commands through it, use `uv run` as shown below.

The research workflow also starts the Tavily MCP server with `npx`, so make sure Node.js and npm are installed:

```bash
node --version
npm --version
```

## 3. Configure API credentials and CORS

Create `.env` only if it does not already exist. This preserves any credentials you have already configured:

```bash
cp -n .env.example .env
```

Edit `.env` and set a supported model and its provider key, plus your Tavily key. For the example model, configure:

```dotenv
LLM_MODEL=anthropic/claude-sonnet-4-6
ANTHROPIC_API_KEY=your_real_anthropic_key
TAVILY_API_KEY=your_real_tavily_key
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=http://localhost:5501
```

Use the provider key that matches your `LLM_MODEL`. Keep `.env` private and never put provider credentials in the frontend. If you set `API_KEY`, the frontend's Connection settings can send it for local development. The API requires an API key when bound to a non-local host.

## 4. Start the backend API

In the first terminal, from the project root:

```bash
uv run python main.py
```

Keep this terminal running. On first startup, local vector memory and embedding components may initialize or download model assets.

In another terminal, confirm the API is responding:

```bash
curl http://127.0.0.1:8000/healthz
```

Expected response:

```json
{"status":"ok"}
```

Interactive API docs are at `http://127.0.0.1:8000/docs`.

## 5. Start the frontend

Open a second terminal at the project root and run:

```bash
python3 -m http.server 5501 --directory frontend
```

Keep this terminal running and open `http://localhost:5501` in your browser. The page's API URL defaults to `http://127.0.0.1:8000`; change it under **Connection settings** if your API uses another host or port.

The frontend submits to `POST /research/jobs`, polls the returned status URL, displays Markdown or JSON output, and offers a PDF download when the selected output format creates one. Research can take several minutes.

## 6. Submit a request from the terminal (optional)

The frontend provides the same request options. You can submit directly to the synchronous API with `curl`:

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query":"How are humanoid robots being used in manufacturing?","research_depth":"intermediate","output_format":"report","max_sources":6,"include_citations":true}'
```

Available settings:

- `research_depth`: `basic`, `intermediate`, or `deep`
- `output_format`: `markdown`, `report`, or `json`
- `max_sources`: 1–100; capped by the server's `MAX_SEARCH_RESULTS`
- `include_citations`: `true` or `false`

If `API_KEY` is configured, add this header to API requests:

```bash
-H "Authorization: Bearer YOUR_API_KEY"
```

JSON output is returned as an object and has no PDF. Markdown and report outputs include a PDF URL.

## 7. Where outputs are saved

- Generated PDFs: `reports/<run-id>.pdf`
- Local Qdrant memory: the directory configured by `QDRANT_PATH` (default `qdrant_db/`)
- Logs: `logs/research_agent.log`

Asynchronous job status is stored in process memory. Restarting the API clears the status records, although already-created PDF files remain on disk.

## Troubleshooting

### Browser says it cannot connect or reports a CORS error

Check that both servers are running. Set `CORS_ORIGINS=http://localhost:5501` in `.env`, then restart the API. The browser origin must match the configured origin exactly; `localhost` and `127.0.0.1` are different origins.

### API returns 401

If `API_KEY` is set in `.env`, enter the same key in the frontend's **Connection settings**. For terminal requests, send the Bearer authorization header.

### Research job fails

Check the backend terminal and `logs/research_agent.log`. Confirm the model provider key and `TAVILY_API_KEY` are valid, and that Node.js/npm are available for `npx`.

### `uv lock` reports a Python-version conflict

The project currently declares `requires-python = ">=3.10,<3.14"` because dependency resolution for Python 3.14 conflicted with the pinned NumPy and Qdrant/FastEmbed dependencies. Confirm your environment uses Python 3.10–3.13, then run `uv lock` again.
