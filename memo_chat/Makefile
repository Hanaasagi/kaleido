SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -ex -c

.DEFAULT_GOAL := help

db:
	docker-compose up -d

run: db
	uv run memo-chat

test:
	uv run python tests/test_rrf.py

check:
	uvx ruff check

fix:
	uvx ruff check --fix

format:
	uvx ruff format
