COMPOSE ?= podman compose

.PHONY: up down restart logs ps api api-sync format lint type test api-check migrate migrate-up api-format api-lint api-type api-test

up:
	cd infra && $(COMPOSE) up -d

down:
	cd infra && $(COMPOSE) down

restart:
	cd infra && $(COMPOSE) restart

logs:
	cd infra && $(COMPOSE) logs -f

ps:
	cd infra && $(COMPOSE) ps

api:
	cd apps/model-gateway && uv run uvicorn src.main:app --reload

api-sync:
	cd apps/model-gateway && uv sync

format:
	cd apps/model-gateway && uv run ruff format src tests alembic

lint:
	cd apps/model-gateway && uv run ruff check src tests alembic

type:
	cd apps/model-gateway && uv run mypy

test:
	cd apps/model-gateway && uv run pytest

api-check:
	cd apps/model-gateway && uv run ruff format --check src tests alembic
	cd apps/model-gateway && uv run ruff check src tests alembic
	cd apps/model-gateway && uv run mypy
	cd apps/model-gateway && uv run pytest

migrate:
	cd apps/model-gateway && uv run alembic revision --autogenerate -m "$${MESSAGE:-migration}"

migrate-up:
	cd apps/model-gateway && uv run alembic upgrade head

api-format: format

api-lint: lint

api-type: type

api-test: test
