FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system mercadovoz && adduser --system --ingroup mercadovoz mercadovoz

COPY pyproject.toml ./
COPY engine ./engine
COPY apps/__init__.py ./apps/__init__.py
COPY apps/api ./apps/api
RUN python -m pip install --upgrade pip && python -m pip install ".[api]"

USER mercadovoz
EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
