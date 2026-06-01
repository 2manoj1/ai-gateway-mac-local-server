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
- `GET /v1/models/{model}`
- `POST /v1/chat/completions`
- `POST /v1/chat/completions` with `stream=true`
- `POST /v1/completions`
- `POST /v1/embeddings`
- `POST /v1/responses`
- `POST /v1/images/generations`

Use:

```python
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_CLIENT_API_KEY>",
    base_url="http://localhost:8010/v1",
)
```

Production exposes the gateway on `127.0.0.1:8000` for Cloudflare Tunnel. Public
clients should use the tunnel hostname, for example
`https://<your-cloudflare-hostname>/v1`.

PostgreSQL, Redis, and Qdrant stay private on the Compose network in production.

## Persistence

PostgreSQL stores API key records and usage logs.

The bootstrap `ADMIN_SECRET` from the environment is used for admin access.
Client traffic should use PostgreSQL-backed keys created through:

- `POST /admin/api-keys`
- `GET /admin/api-keys`
- `DELETE /admin/api-keys/{api_key_id}`

Current usage log fields:

- api_key_id
- endpoint
- model
- tokens_input
- tokens_output
- created_at

Token accounting is intentionally prepared but not fully implemented yet.

## Future Work

- Token accounting
- Redis-backed caching/rate limiting
- Qdrant-backed RAG workflows
