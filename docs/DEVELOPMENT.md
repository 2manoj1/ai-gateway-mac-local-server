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

cp infra/.env.example infra/.env
cp apps/model-gateway/.env.example apps/model-gateway/.env

make up
make api-sync
make migrate-up
make api
```

## Pull a Model

```bash
ollama pull qwen3.5:9b
```

## Quality Gate

```bash
make api-check
```

## Useful Commands

```bash
make up
make down
make logs
make api
make migrate-up
make format
make lint
make type
make test
```
