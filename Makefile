.PHONY: install test lint typecheck check fmt clean

install:
	UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv sync --all-groups

test:
	UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run pytest

lint:
	UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run ruff check .

typecheck:
	UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run mypy spy_trader

check: lint typecheck test

fmt:
	UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run ruff check --fix .
	UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run ruff format .

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build .uv-cache
	find . -type d -name __pycache__ -exec rm -rf {} +
