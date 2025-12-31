# see uv-docker-example for more details
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim as builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOAD=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=uv.lock,target=uv.lock,z \
	--mount=type=bind,source=pyproject.toml,target=pyproject.toml,z \
	uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --frozen --no-dev

## the version needs to match the version used in the builder stage
FROM python:3.13-slim-bookworm

#COPY --from=builder --chown=app:app /app /app
COPY --from=builder /app /app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "main.py"]
