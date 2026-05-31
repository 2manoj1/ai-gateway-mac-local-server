# LangChain Agent Smoke App

Small external FastAPI service for testing the production AI gateway from a
separate microservice process.

## Setup

```bash
cd apps/langchain-agent
cp .env.example .env
uv sync
```

Set `PRODUCTION_GATEWAY_API_KEY` to a client API key for the production gateway.

## Run

```bash
PYTHONPATH=src uv run uvicorn langchain_agent.main:app --host 127.0.0.1 --port 8001
```

## Test

Raw HTTPX call to the production completion API:

```bash
curl -sS http://127.0.0.1:8001/httpx/direct-message \
  -H "Content-Type: application/json" \
  -d '{"message":"/no_think Reply with exactly: httpx-prod-ok","model":"qwen3.5:9b"}'
```

LangChain `create_agent` call using an HTTPX-backed chat model:

```bash
curl -sS http://127.0.0.1:8001/langchain/agent/direct-message \
  -H "Content-Type: application/json" \
  -d '{"message":"/no_think Reply with exactly: langchain-prod-ok","model":"qwen3.5:9b"}'
```
