FROM python:3.13-alpine

# gitpython requires git binary
RUN apk fix && \
    apk --no-cache --update add git

# Install Vale separately
RUN wget https://github.com/errata-ai/vale/releases/download/v3.9.1/vale_3.9.1_Linux_64-bit.tar.gz && \
    tar -xvzf vale_3.9.1_Linux_64-bit.tar.gz && \
    mv vale /usr/local/bin && \
    rm vale_3.9.1_Linux_64-bit.tar.gz

RUN git config --global user.name "getdocsy[Bot]" # TODO remove hardcoded bot name and make it depend on environment
RUN git config --global user.email "171265091+getdocsy[bot]@users.noreply.github.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

COPY src/ /app/src

EXPOSE 8000
