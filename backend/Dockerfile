FROM python:3.12-slim AS builder

WORKDIR /build

# Build-time deps for packages that compile C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim AS runtime

# Runtime system libraries required by weasyprint (Cairo/Pango stack)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    shared-mime-info \
    fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser
WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY start.sh .

RUN chmod +x start.sh

USER appuser

EXPOSE 8000

CMD ["/bin/sh", "start.sh"]
