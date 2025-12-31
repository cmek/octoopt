# see uv-docker-example for more details
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim as builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_NO_DEV=1

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=uv.lock,target=uv.lock \
	--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
	uv sync --locked --no-install-project 
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --locked

## the version needs to match the version used in the builder stage
FROM python:3.13-slim-bookworm

RUN groupadd --system --gid 31337 app \
 && useradd --system --gid 31337 --uid 31337 --create-home app

#COPY --from=builder --chown=app:app /app /app
COPY --from=builder --chown=app:app /app /app

USER app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "main.py"]
