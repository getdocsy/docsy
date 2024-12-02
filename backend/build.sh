#!/usr/bin/env bash
set -o errexit

pip install uv
uv sync --frozen
uv run python src/manage.py collectstatic --no-input
uv run python src/manage.py migrate