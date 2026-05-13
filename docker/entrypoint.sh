#!/usr/bin/env bash
set -e

# Wait for Postgres if DATABASE_URL points to it
if [[ "${DATABASE_URL:-}" == postgres* ]]; then
    echo "[entrypoint] Aguardando Postgres..."
    python - <<'PY'
import os, time, urllib.parse, socket
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
host, port = url.hostname, url.port or 5432
for i in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"[entrypoint] Postgres OK em {host}:{port}")
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit(f"Postgres indisponível em {host}:{port}")
PY
fi

echo "[entrypoint] Aplicando migrações..."
python manage.py migrate --noinput

echo "[entrypoint] Coletando estáticos..."
python manage.py collectstatic --noinput || true

exec "$@"

