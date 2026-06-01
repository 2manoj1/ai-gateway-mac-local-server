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
curl -X POST http://localhost:8010/admin/api-keys \
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
cp infra/.env.dev.example infra/.env.dev
make dev-up
```

The Compose stack builds this service from `apps/model-gateway/Dockerfile` and
publishes it on `http://localhost:8010`. Use
`OLLAMA_BASE_URL=http://host.containers.internal:11434/v1` in `infra/.env.dev` when
Ollama is running directly on the host.

Production uses `infra/compose.yaml` and `infra/.env`, publishes only the gateway
on `127.0.0.1:8000`, and keeps PostgreSQL, Redis, and Qdrant private on the
Compose network. Cloudflare Tunnel should target `http://127.0.0.1:8000`.

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

Use the gateway as a normal OpenAI-compatible `base_url`.

```python
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_CLIENT_API_KEY>",
    base_url="http://localhost:8010/v1",
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

For production through Cloudflare Tunnel, use your tunnel hostname:

```python
client = OpenAI(
    api_key="<YOUR_CLIENT_API_KEY>",
    base_url="https://<your-cloudflare-hostname>/v1",
)
```

Supported OpenAI-compatible routes:

- `GET /v1/models`
- `GET /v1/models/{model}`
- `POST /v1/chat/completions`
- `POST /v1/completions`
- `POST /v1/embeddings`
- `POST /v1/responses`
- `POST /v1/images/generations`

The gateway preserves provider-specific request fields. OpenAI/Ollama fields such
as `tools`, `tool_choice`, `response_format`, `stream_options`, `seed`,
`max_completion_tokens`, and Ollama-specific options pass through to the upstream.
OpenRouter-style fields such as `provider`, `models`, and `plugins` are forwarded
in the upstream request body instead of being dropped.

Recommended local models for the M1 Pro home-lab setup:

- `qwen3.5:9b`: default model for chat, tool calls, and agent workflows.
- `gemma4:e4b`: alternate daily assistant model and vision-capable fallback.
- `llama3.2`: small fast model for lightweight summarization/classification.
- `nomic-embed-text`: embedding model for RAG and memory/search.

Use `qwen3.5:9b` as `DEFAULT_MODEL` and pass `model="nomic-embed-text"` explicitly
for embeddings.

Tool call example:

```python
response = client.chat.completions.create(
    model="qwen3.5:9b",
    messages=[
        {
            "role": "user",
            "content": "What is the weather in Chennai? Use the tool.",
        }
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        }
    ],
    tool_choice={"type": "function", "function": {"name": "get_weather"}},
)

print(response.choices[0].message.tool_calls)
```

LangChain example:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="<YOUR_CLIENT_API_KEY>",
    base_url="http://localhost:8010/v1",
    model="qwen3.5:9b",
    max_completion_tokens=512,
    timeout=180,
)
```

Embeddings and image generation require Ollama models that support those
capabilities. If the selected upstream model does not support an endpoint, the
gateway returns an OpenAI-style error with the upstream status code and message.
