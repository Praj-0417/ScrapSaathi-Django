#!/usr/bin/env bash
# ==============================================================================
# start_dev.sh - Isolated Local Development Server Starter
# Checks port availability, validates environment, runs migrations, and launches DRF.
# Never terminates or affects existing monolith or microservice processes.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${PROJECT_ROOT}/.venv"

PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================================="
echo "      STARTING SCRAPSAATHI DJANGO DEV ENVIRONMENT         "
echo "=========================================================="

# 1. Check Python / Virtualenv
PYTHON_BIN="python"
if [ -f "${VENV_DIR}/bin/python" ]; then
    PYTHON_BIN="${VENV_DIR}/bin/python"
elif [ -f "${VENV_DIR}/Scripts/python.exe" ]; then
    PYTHON_BIN="${VENV_DIR}/Scripts/python.exe"
fi

echo -e "${BLUE}[INFO]${NC} Using Python interpreter: ${PYTHON_BIN}"
"${PYTHON_BIN}" -c "import django" || {
    echo -e "${RED}[ERROR]${NC} Django is not available in the selected Python environment."
    echo "Please activate .venv or run: pip install -r backend/requirements.txt"
    exit 1
}

# 2. Check Port Availability safely
if command -v ss &>/dev/null; then
    if ss -tulpn | grep -q ":${PORT} "; then
        echo -e "${RED}[ERROR]${NC} Port ${PORT} is already in use by another process."
        echo "Safety safeguard: Will not terminate existing process. Please stop the conflicting service or select a different port."
        exit 1
    fi
elif command -v netstat &>/dev/null; then
    if netstat -tuln | grep -q ":${PORT} "; then
        echo -e "${RED}[ERROR]${NC} Port ${PORT} is already in use."
        exit 1
    fi
fi

# 3. Environment configuration check
if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    echo -e "${YELLOW}[WARN]${NC} No .env file found in scrapsaathi-django. Creating from .env.example..."
    cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
fi

# 4. Run Migrations
echo -e "${BLUE}[INFO]${NC} Applying database migrations..."
"${PYTHON_BIN}" "${BACKEND_DIR}/manage.py" migrate --noinput

# 5. Start Development Server
echo -e "${GREEN}[SUCCESS]${NC} Prerequisites verified. Launching Django dev server at http://${HOST}:${PORT}/"
echo -e "${BLUE}[INFO]${NC} Press Ctrl+C to terminate."

exec "${PYTHON_BIN}" "${BACKEND_DIR}/manage.py" runserver "${HOST}:${PORT}"
