# AI Gateway Mac Local Server

OpenAI-compatible local AI gateway for routing application traffic through a
FastAPI service before forwarding requests to Ollama or future model providers.

The project is designed as a reusable model gateway for other apps in a home
lab or local development environment.

## Features

- OpenAI SDK-compatible endpoints:
  - `GET /v1/models`
  - `POST /v1/chat/completions`
  - `POST /v1/chat/completions` with `stream=true`
- Ollama backend using the OpenAI-compatible client.
- Python 3.14, FastAPI, uv, Ruff, mypy, and pytest.
- PostgreSQL-backed API keys and usage logs.
- Redis and Qdrant clients initialized for future caching, rate limiting, and RAG.
- Alembic migrations.
- Structured JSON logging with request IDs.
- GitHub Actions CI, Dependabot, issue templates, and PR template.

## Architecture

```text
Client application
  -> FastAPI model gateway
  -> Ollama OpenAI-compatible API
  -> Local model, for example qwen3.5:9b
```

## Repository Structure

```text
ai-gateway-mac-local-server/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   │   └── ci.yml
│   ├── dependabot.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── apps/
│   └── model-gateway/
│       ├── alembic/
│       ├── src/
│       │   ├── api/
│       │   ├── clients/
│       │   ├── core/
│       │   ├── db/
│       │   ├── dependencies/
│       │   ├── middleware/
│       │   ├── repositories/
│       │   ├── schemas/
│       │   ├── services/
│       │   └── utils/
│       ├── tests/
│       ├── Dockerfile
│       ├── .env.example
│       ├── .python-version
│       ├── pyproject.toml
│       └── uv.lock
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── OPEN_SOURCE_RELEASE.md
├── infra/
│   ├── compose.yaml
│   └── .env.example
├── scripts/
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
└── SECURITY.md
```

`apps/model-gateway` is the FastAPI service. Its internal `src/api` directory
contains HTTP route modules.

## Requirements

- Python 3.14
- uv
- Podman Compose or Docker Compose
- Ollama
- Local model, for example `qwen3.5:9b`

## Quick Start

Clone and configure:

```bash
git clone https://github.com/2manoj1/ai-gateway-mac-local-server.git
cd ai-gateway-mac-local-server

cp infra/.env.example infra/.env
cp apps/model-gateway/.env.example apps/model-gateway/.env
```

Start the full server stack with PostgreSQL, Redis, Qdrant, and the gateway
container:

```bash
make up
```

The gateway container runs migrations automatically when `RUN_MIGRATIONS=1` in
`infra/.env`.

For local API development, start only infrastructure, install API dependencies,
and run migrations:

```bash
make infra-up
make api-sync
make migrate-up
```

Pull the model and start the gateway:

```bash
ollama pull qwen3.5:9b
make api
```

Use Docker Compose instead of Podman Compose:

```bash
make COMPOSE="docker compose" up
```

## OpenAI SDK Usage

```python
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_CLIENT_API_KEY>",
    base_url="http://localhost:8000/v1",
)

models = client.models.list()

response = client.chat.completions.create(
    model="qwen3.5:9b",
    messages=[
        {"role": "user", "content": "hello"},
    ],
)

print(response.choices[0].message.content)
```

Streaming:

```python
stream = client.chat.completions.create(
    model="qwen3.5:9b",
    messages=[
        {"role": "user", "content": "hello"},
    ],
    stream=True,
)

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Environment

Gateway environment variables live in `apps/model-gateway/.env`.

```env
ADMIN_SECRET=sk-admin-secret-change-me
DATABASE_URL=postgresql+psycopg://aigateway:change-me-later@localhost:5432/aigateway
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
OLLAMA_BASE_URL=http://localhost:11434/v1
DEFAULT_MODEL=qwen3.5:9b
APP_NAME=Gateway API
ENVIRONMENT=local
```

Infrastructure environment variables live in `infra/.env`.

For Compose, Ollama runs on the host machine by default, so
`OLLAMA_BASE_URL=http://host.containers.internal:11434/v1` is used in
`infra/.env.example`.

## API Key Administration

Use the bootstrap admin secret from `apps/model-gateway/.env` to manage API keys:

```bash
curl -X POST http://localhost:8000/admin/api-keys \
  -H "X-Admin-Secret: <ADMIN_SECRET>" \
  -H "Content-Type: application/json" \
  -d '{"name":"local-app"}'
```

The response includes a plaintext `key` once. Store it securely. The database
stores only a SHA-256 hash.

Use that key with OpenAI-compatible clients:

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-local-generated-value",
    base_url="http://localhost:8000/v1",
)
```

Admin routes:

- `POST /admin/api-keys`
- `GET /admin/api-keys`
- `DELETE /admin/api-keys/{api_key_id}`

## Commands

```bash
make up          # Start PostgreSQL, Redis, Qdrant, and the gateway container
make infra-up    # Start only PostgreSQL, Redis, and Qdrant for local API dev
make down        # Stop the Compose stack
make logs        # Follow Compose stack logs
make ps          # Show Compose stack status
make api         # Run the FastAPI gateway locally with uvicorn
make migrate-up  # Apply database migrations
make format      # Format Python and Alembic files
make lint        # Run Ruff
make type        # Run mypy
make test        # Run pytest
make api-check   # Run the full quality gate
```

## Mac Server Mode

For a MacBook acting as the local AI server, install user LaunchAgents:

```bash
make macos-server-install
make macos-server-status
```

This keeps three user services active after login:

- `com.manoj.ai-gateway-stack`: starts the Compose stack and reconciles it every
  5 minutes.
- `com.manoj.ai-gateway-tunnel`: runs the Cloudflare Tunnel to the gateway.
- `com.manoj.caffeinate`: prevents system sleep while the Mac is plugged in and
  serving traffic.

LaunchAgent logs are written to `~/Library/Logs/ai-gateway`.

## Open Source Setup

This repository includes:

- MIT license
- Contribution guide
- Security policy
- Code of conduct
- Changelog
- GitHub issue templates
- Pull request template
- GitHub Actions CI
- Dependabot configuration

Release hygiene notes live in
[docs/OPEN_SOURCE_RELEASE.md](docs/OPEN_SOURCE_RELEASE.md).

## GitHub Repository

This project is published at:

<https://github.com/2manoj1/ai-gateway-mac-local-server>

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development](docs/DEVELOPMENT.md)
- [Open source release checklist](docs/OPEN_SOURCE_RELEASE.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)

## License

MIT
