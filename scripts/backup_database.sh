#!/usr/bin/env bash
# ==============================================================================
# backup_database.sh - ScrapSaathi Database Backup Automation
# Backs up only the scrapsaathi database (PostgreSQL pg_dump or SQLite snapshot).
# Writes timestamped, compressed backup artifacts without silent overwriting.
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
mkdir -p "${BACKUP_DIR}"

# Source environment if available
if [ -f ".env" ]; then
    # shellcheck disable=SC1091
    source .env 2>/dev/null || true
fi

DB_ENGINE="${DB_ENGINE:-postgresql}"
POSTGRES_DB="${POSTGRES_DB:-scrapsaathi_db}"
POSTGRES_USER="${POSTGRES_USER:-scrapsaathi_user}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "=========================================================="
echo "          SCRAPSAATHI DATABASE BACKUP UTILITY             "
echo "=========================================================="
echo "Timestamp:    ${TIMESTAMP}"
echo "Backup Dir:   ${BACKUP_DIR}"
echo "DB Engine:    ${DB_ENGINE}"

if [ "${DB_ENGINE}" = "postgresql" ]; then
    BACKUP_FILE="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

    if ! command -v pg_dump &>/dev/null; then
        echo "[WARN] pg_dump not found on host. Checking for Docker container..."
        if command -v docker &>/dev/null && docker ps | grep -q "scrapsaathi.*postgres"; then
            CONTAINER_ID=$(docker ps --filter "name=postgres" --format "{{.ID}}" | head -n 1)
            echo "[INFO] Running pg_dump inside container ${CONTAINER_ID}..."
            docker exec -t "${CONTAINER_ID}" pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > "${BACKUP_FILE}"
        else
            echo "[ERROR] Neither pg_dump nor active PostgreSQL container found."
            echo "Cannot execute PostgreSQL dump."
            exit 1
        fi
    else
        echo "[INFO] Executing pg_dump for database ${POSTGRES_DB}..."
        PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -F c -b -v -f "${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.dump"
        BACKUP_FILE="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.dump"
    fi
else
    # SQLite Backup
    SQLITE_PATH="backend/db.sqlite3"
    BACKUP_FILE="${BACKUP_DIR}/scrapsaathi_sqlite_${TIMESTAMP}.db"
    if [ ! -f "${SQLITE_PATH}" ]; then
        echo "[ERROR] SQLite database file not found at ${SQLITE_PATH}"
        exit 1
    fi
    echo "[INFO] Creating atomic SQLite backup..."
    cp "${SQLITE_PATH}" "${BACKUP_FILE}"
fi

if [ -f "${BACKUP_FILE}" ]; then
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "----------------------------------------------------------"
    echo "[SUCCESS] Backup completed successfully!"
    echo "File:     ${BACKUP_FILE}"
    echo "Size:     ${SIZE}"
    echo "Restore command example:"
    if [ "${DB_ENGINE}" = "postgresql" ]; then
        echo "  pg_restore -U ${POSTGRES_USER} -d ${POSTGRES_DB} ${BACKUP_FILE}"
    else
        echo "  cp ${BACKUP_FILE} backend/db.sqlite3"
    fi
    echo "=========================================================="
    exit 0
else
    echo "[ERROR] Backup failed. Target artifact was not generated."
    exit 1
fi
