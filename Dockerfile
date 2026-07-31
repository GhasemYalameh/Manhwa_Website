FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#  uv use python file system
ENV UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends  \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

# --no-dev for production
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project 

COPY . .
