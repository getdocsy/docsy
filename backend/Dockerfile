FROM python:3.13
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# gitpython requires git binary
RUN apt-get update && apt-get install -y git

# Install Vale separately
# TODO: remove hardcoded version and CPU architecture
RUN wget -q https://github.com/errata-ai/vale/releases/download/v3.9.1/vale_3.9.1_Linux_arm64.tar.gz && \
    tar -xzf vale_3.9.1_Linux_arm64.tar.gz && \
    mv vale /usr/local/bin && \
    rm vale_3.9.1_Linux_arm64.tar.gz

RUN git config --global user.name "getdocsy[Bot]" # TODO remove hardcoded bot name and make it depend on environment
RUN git config --global user.email "171265091+getdocsy[bot]@users.noreply.github.com"

# Show Python output immediately https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED=1

# Silence warnings about hard links https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the project into the image
COPY src/ /app/src
COPY pyproject.toml uv.lock ./

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

RUN uv run python src/manage.py collectstatic --no-input

EXPOSE 8000
