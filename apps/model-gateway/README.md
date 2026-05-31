# Model Gateway

FastAPI AI gateway backed by local Ollama.

Part of
[AI Gateway Mac Local Server](https://github.com/2manoj1/ai-gateway-mac-local-server).

## Requirements

- Python 3.14
- PostgreSQL
- Redis
- Qdrant
- uv
- Ollama listening on `http://localhost:11434`

## Setup

```bash
uv sync
cp .env.example .env
```

Set `API_KEY` in `.env`.

## Migrate

```bash
uv run alembic upgrade head
```

## Admin API Keys

Use the bootstrap env key to create PostgreSQL-backed client keys:

```bash
curl -X POST http://localhost:8000/admin/api-keys \
  -H "Authorization: Bearer sk-local" \
  -H "Content-Type: application/json" \
  -d '{"name":"local-app"}'
```

Only the key hash is stored. The plaintext key is returned once.

## Run

```bash
uv run uvicorn src.main:app --reload
```

## Check

```bash
uv run ruff format --check src tests
uv run ruff check src tests
uv run mypy
uv run pytest
```

From the repository root, use:

```bash
make api-check
```

## OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-local",
    base_url="http://localhost:8000/v1",
)

models = client.models.list()
response = client.chat.completions.create(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "hello"}],
)

stream = client.chat.completions.create(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "hello"}],
    stream=True,
)
```
