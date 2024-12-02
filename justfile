set dotenv-load
set dotenv-required
set working-directory := 'backend'

# Default recipe to display all available commands
default:
    @just --list

# Run Django development server
serve *args:
    uv run python src/manage.py runserver {{args}}

# Make and run migrations
migrate:
    uv run python src/manage.py makemigrations
    uv run python src/manage.py migrate

ngrok:
    ngrok http --domain reasonably-firm-cricket.ngrok-free.app 8000

# Bump version: increment minor version, create and push git tag
bump_version:
    #!/usr/bin/env sh
    CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    MAJOR=$(echo $CURRENT_TAG | cut -d. -f1)
    MINOR=$(echo $CURRENT_TAG | cut -d. -f2)
    PATCH=$(echo $CURRENT_TAG | cut -d. -f3)
    NEW_PATCH=$((PATCH + 1))
    NEW_TAG="${MAJOR}.${MINOR}.${NEW_PATCH}"
    git push --quiet
    git tag $NEW_TAG
    git push origin $NEW_TAG
    echo "Bumped version from $CURRENT_TAG to $NEW_TAG"
