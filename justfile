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
    git push origin $NEW_TAG --quiet
    echo "Bumped version from $CURRENT_TAG to $NEW_TAG"

    # Update the version in the Nix file
    sed -i "" "s/docsyWebVersion = \".*\"/docsyWebVersion = \"${NEW_TAG}\"/" "${NIXCONFIG_REPO_PATH}/services/app-getdocsy-com.nix"
    (cd "${NIXCONFIG_REPO_PATH}" && \
        git add services/app-getdocsy-com.nix && \
        git commit -m "bump docsy version" --quiet && \
        git push --quiet)
    echo "Bumped version in Nix config repo to $NEW_TAG"

deploy_on_blausieb:
    #!/usr/bin/env sh

    # Wait until the docker image is built
    RUN_ID=$(gh run list --commit $(git rev-parse HEAD) --json databaseId | jq -r '.[0].databaseId')
    gh run watch $RUN_ID --exit-status

    # Then deploy
    ssh blausieb "cd /etc/nixos && sudo -E git pull --quiet && just switch"

