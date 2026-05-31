# Architecture

AI Gateway Mac Local Server is a local-first OpenAI-compatible gateway for
running model traffic through FastAPI before forwarding requests to Ollama.

## Request Flow

```text
Client
  -> FastAPI Gateway
  -> Ollama OpenAI-compatible API
  -> Local model, for example qwen3.5:9b
```

## Main Components

- `apps/model-gateway`: FastAPI service exposed to client applications.
- `apps/model-gateway/src/api`: HTTP route modules.
- `apps/model-gateway/src/clients`: external service clients.
- `apps/model-gateway/src/services`: business logic and orchestration.
- `apps/model-gateway/src/repositories`: database access.
- `apps/model-gateway/src/db`: SQLAlchemy setup and models.
- `infra`: local PostgreSQL, Redis, and Qdrant services.

## OpenAI Compatibility

The gateway supports the OpenAI SDK by exposing:

- `GET /v1/models`
- `POST /v1/chat/completions`
- `POST /v1/chat/completions` with `stream=true`

Use:

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-local",
    base_url="http://localhost:8000/v1",
)
```

## Persistence

PostgreSQL stores future API key records and usage logs.

Current usage log fields:

- endpoint
- model
- tokens_input
- tokens_output
- created_at

Token accounting is intentionally prepared but not fully implemented yet.

## Future Work

- PostgreSQL-backed API key validation
- Token accounting
- Redis-backed caching/rate limiting
- Qdrant-backed RAG workflows
- More OpenAI-compatible endpoints, including embeddings and image generation
