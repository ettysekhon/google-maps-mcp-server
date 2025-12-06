FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "google_maps_mcp_server.api:app", "--host", "0.0.0.0", "--port", "8080"]
