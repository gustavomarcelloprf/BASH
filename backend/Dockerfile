FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim AS runtime

RUN useradd --create-home appuser
WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

USER appuser

EXPOSE 8000

CMD ["/bin/sh", "-c", "echo '=== START ===' && echo 'PORT='$PORT && echo 'DATABASE_URL set='$([ -n \"$DATABASE_URL\" ] && echo yes || echo NO) && echo 'SECRET_KEY set='$([ -n \"$SECRET_KEY\" ] && echo yes || echo NO) && echo '=== Running alembic ===' && alembic upgrade head && echo '=== Alembic OK, starting uvicorn ===' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
