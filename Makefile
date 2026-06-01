SHELL := /usr/bin/env bash
COMPOSE ?= podman compose
.DEFAULT_GOAL := help

.PHONY: help up infra-up dev-up dev-down down prod-build prod-up prod-recreate prod-down prod-logs prod-ps restart logs ps macos-server-install macos-server-status api api-sync format lint type test api-check migrate migrate-up api-format api-lint api-type api-test

help:
	@printf "Usage:\n"
	@printf "  make help\n"
	@printf "  make dev-up\n"
	@printf "  make dev-down\n"
	@printf "  make prod-up\n"
	@printf "  make prod-build\n"
	@printf "  make prod-recreate\n"
	@printf "  make prod-down\n"
	@printf "  make prod-logs\n"
	@printf "  make prod-ps\n"
	@printf "  make api-check\n"
	@printf "\n"
	@printf "Set COMPOSE=\"docker compose\" to force Docker instead of Podman.\n\n"

up:
	@echo "Using development stack on port 8010. Production runs from ../ai-gateway-prod on port 8000."
	./scripts/dev-up.sh

infra-up:
	@echo "Using development infra ports: Postgres 5433, Redis 6380, Qdrant 6335."
	cd infra && test -f .env.dev || cp .env.dev.example .env.dev
	cd infra && $(COMPOSE) -p ai-gateway-dev -f compose.dev.yaml --env-file .env.dev up -d postgres redis qdrant

dev-up:
	./scripts/dev-up.sh

dev-down:
	./scripts/dev-down.sh

down:
	./scripts/dev-down.sh

prod-build:
	cd infra && $(COMPOSE) -f compose.yaml build --no-cache ai-gateway

prod-up:
	./scripts/up.sh

prod-recreate: prod-down prod-up

prod-down:
	./scripts/down.sh

prod-logs:
	./scripts/logs.sh

prod-ps:
	cd infra && $(COMPOSE) -f compose.yaml ps

restart:
	cd infra && $(COMPOSE) -p ai-gateway-dev -f compose.dev.yaml --env-file .env.dev restart

logs:
	cd infra && $(COMPOSE) -p ai-gateway-dev -f compose.dev.yaml --env-file .env.dev logs -f

ps:
	cd infra && $(COMPOSE) -p ai-gateway-dev -f compose.dev.yaml --env-file .env.dev ps

macos-server-install:
	./scripts/macos/install-launchagents.sh

macos-server-status:
	./scripts/macos/launchagents-status.sh

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
