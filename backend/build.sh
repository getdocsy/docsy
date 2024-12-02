#!/usr/bin/env bash
set -o errexit

poetry install
poetry run python src/manage.py collectstatic --no-input
poetry run python src/manage.py migrate