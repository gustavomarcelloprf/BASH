#!/bin/sh
set -e

# If using PostgreSQL, wait until the database accepts connections
if echo "${DATABASE_URL:-}" | grep -q "postgresql"; then
    echo "Waiting for database to be ready..."
    python - <<'PYEOF'
import time, sys, os
from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]
for attempt in range(30):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready.")
        sys.exit(0)
    except Exception as exc:
        print(f"Attempt {attempt + 1}/30 — DB not ready: {exc}")
        time.sleep(3)

print("ERROR: Database did not become ready after 90 seconds.")
sys.exit(1)
PYEOF
fi

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
