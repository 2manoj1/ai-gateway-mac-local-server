# Contributing

Thanks for helping improve AI Gateway Mac Local Server.

## Development Setup

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

## Quality Checks

Run the full local gate before opening a pull request:

```bash
make api-check
```

This runs:

- Ruff format check
- Ruff lint
- mypy strict type checking
- pytest

## Pull Request Guidelines

- Keep pull requests focused.
- Add or update tests for behavior changes.
- Update documentation when routes, environment variables, or setup steps change.
- Do not commit secrets, local `.env` files, database volumes, or generated caches.

## Commit Style

Use short, direct commit messages:

```text
Add OpenAI-compatible chat route
Fix usage log migration
Document local setup
```
