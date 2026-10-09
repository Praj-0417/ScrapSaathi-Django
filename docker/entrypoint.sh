#!/usr/bin/env bash
set -e

# Wait for PostgreSQL readiness if configured
if [ "${DB_ENGINE}" = "postgresql" ]; then
    echo "Waiting for PostgreSQL database at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
    until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"; do
        sleep 1
    done
    echo "PostgreSQL is reachable and accepting connections."
fi

# Run database migrations automatically
echo "Applying database migrations..."
python /app/backend/manage.py migrate --noinput

exec "$@"
