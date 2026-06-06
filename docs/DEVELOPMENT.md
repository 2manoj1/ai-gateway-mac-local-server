# Development

Repository: <https://github.com/2manoj1/ai-gateway-mac-local-server>

## Requirements

- Python 3.14
- uv
- Podman or Docker with Compose support
- Ollama

## First Run

```bash
git clone https://github.com/2manoj1/ai-gateway-mac-local-server.git
cd ai-gateway-mac-local-server

cp infra/.env.dev.example infra/.env.dev
cp apps/model-gateway/.env.example apps/model-gateway/.env

make dev-up
```

`make dev-up` starts the development Compose stack: PostgreSQL, Redis, Qdrant,
and the containerized gateway on local port `8010`. Production runs from the
separate `ai-gateway-prod` folder on port `8000`.

Dev and production should not share env files or ports:

- Dev: `infra/.env.dev`, `infra/compose.dev.yaml`, gateway
  `http://127.0.0.1:8010`.
- Prod: `infra/.env`, `infra/compose.yaml`, gateway
  `http://127.0.0.1:8000`.

The production startup scripts support both Podman and Docker. If you do not set `COMPOSE`, the script will prefer Podman when it is installed and fall back to Docker.

`make prod-up` now rebuilds and recreates the production gateway container, ensuring the latest local code is used.

Production commands:

```bash
make prod-build     # build the gateway image
make prod-up        # start or restart production with latest code
make prod-recreate  # stop and start production cleanly
make prod-down      # stop production
make prod-logs      # follow production logs
make prod-ps        # inspect production status
```

To force Docker explicitly:

```bash
make COMPOSE="docker compose" prod-up
```

Cloudflare Tunnel should target only the production gateway:

```text
http://127.0.0.1:8000
```

PostgreSQL, Redis, and Qdrant are internal production services and should not be
exposed through Cloudflare.

For local API development with uvicorn:

```bash
make infra-up
make api-sync
make migrate-up
make api
```

## Create a Client API Key

```bash
curl -X POST http://localhost:8010/admin/api-keys \
  -H "X-Admin-Secret: <ADMIN_SECRET>" \
  -H "Content-Type: application/json" \
  -d '{"name":"local-app"}'
```

## Pull a Model

```bash
ollama pull qwen3.5:9b
```

## Stream Through the LangGraph Agent

Create a client API key first, then call the direct-message agent endpoint:

```bash
curl -N http://localhost:8010/api/v1/agent/direct-message \
  -H "Authorization: Bearer <CLIENT_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"message":"/no_think Say hello in one short sentence.","model":"qwen3.5:9b"}'
```

To test the exact HTTP boundary that another microservice would call, use the
completion-API variant. The LangGraph node calls this gateway's
`/v1/chat/completions` endpoint over HTTP and streams the response back:

```bash
curl -N http://localhost:8010/api/v1/agent/direct-message/completions-api \
  -H "Authorization: Bearer <CLIENT_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"message":"/no_think Reply with exactly: agent-ok","model":"qwen3.5:9b"}'
```

## Quality Gate

```bash
make api-check
```

## Useful Commands

```bash
make up
make dev-up
make infra-up
make down
make logs
make ps
make macos-ollama-install-official
make macos-ollama-tune
make macos-server-install
make macos-server-status
make api
make migrate-up
make format
make lint
make type
make test
```

## Mac Server Mode

This repository includes user LaunchAgent setup for running a MacBook as the
local AI gateway server.

Install or refresh the LaunchAgents:

```bash
make macos-ollama-install-official
make macos-ollama-tune
make macos-server-install
```

Check their status:

```bash
make macos-server-status
make ps
```

Installed LaunchAgents:

- `com.manoj.ai-gateway-stack` starts the Compose stack at login and every
  5 minutes afterward.
- `com.manoj.ai-gateway-tunnel` keeps the Cloudflare Tunnel running.
- `com.manoj.caffeinate` keeps the Mac awake while it is serving traffic.

The installer reuses the existing tunnel id from
`~/Library/LaunchAgents/com.manoj.ai-gateway-tunnel.plist`. On a new Mac, set
`CLOUDFLARED_TUNNEL_ID` before running the installer.

Logs live in:

```text
~/Library/Logs/ai-gateway/
```
