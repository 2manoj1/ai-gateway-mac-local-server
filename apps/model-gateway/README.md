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

Set `ADMIN_SECRET` in `.env` for protecting administrative routes.

## Migrate

```bash
uv run alembic upgrade head
```

## Admin API Keys

Use the admin secret to create PostgreSQL-backed client keys:

```bash
curl -X POST http://localhost:8000/admin/api-keys \
  -H "X-Admin-Secret: <ADMIN_SECRET>" \
  -H "Content-Type: application/json" \
  -d '{"name":"local-app"}'
```

Only the key hash is stored. The plaintext key is returned once.

## Run

```bash
uv run uvicorn src.main:app --reload
```

## Run With Compose

From the repository root:

```bash
cp infra/.env.example infra/.env
make up
```

The Compose stack builds this service from `apps/model-gateway/Dockerfile` and
publishes it on `http://localhost:8000`. Use
`OLLAMA_BASE_URL=http://host.containers.internal:11434/v1` in `infra/.env` when
Ollama is running directly on the host.

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
    api_key="<YOUR_CLIENT_API_KEY>",
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
