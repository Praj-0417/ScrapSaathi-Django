#!/usr/bin/env bash
# ==============================================================================
# health_check.sh - ScrapSaathi Operational Health Evaluator
# Verifies Django API availability, HTTP response codes, latency, and DB readiness.
# Returns: 0 on success, 1 on health failure, 2 on unreachable service.
# ==============================================================================

set -o pipefail

# Configuration
TARGET_HOST="${TARGET_HOST:-127.0.0.1}"
TARGET_PORT="${TARGET_PORT:-8000}"
TIMEOUT_SEC="${TIMEOUT_SEC:-5}"
HEALTH_URL="http://${TARGET_HOST}:${TARGET_PORT}/health"
API_HEALTH_URL="http://${TARGET_HOST}:${TARGET_PORT}/api/v1/health"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()  { echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"; }

check_curl() {
    if ! command -v curl &> /dev/null; then
        log_error "curl command not found. Please install curl."
        exit 1
    fi
}

check_endpoint() {
    local url="$1"
    local name="$2"
    log_info "Probing ${name} (${url}) with ${TIMEOUT_SEC}s timeout..."

    local response
    local http_code
    local total_time

    response=$(curl -s -S --max-time "${TIMEOUT_SEC}" -w "\n%{http_code}\n%{time_total}" "${url}" 2>&1)
    local curl_exit=$?

    if [ ${curl_exit} -ne 0 ]; then
        log_error "Failed to reach ${name} (curl exit code: ${curl_exit}). Service might be down."
        return 2
    fi

    # Parse response
    local body
    local code
    local duration
    duration=$(echo "${response}" | tail -n 1)
    code=$(echo "${response}" | tail -n 2 | head -n 1)
    body=$(echo "${response}" | sed '$d' | sed '$d')

    if [ "${code}" -eq 200 ]; then
        log_ok "${name} is HEALTHY (HTTP ${code}, latency: ${duration}s)"
        return 0
    else
        log_error "${name} returned UNEXPECTED status code: ${code}. Response: ${body}"
        return 1
    fi
}

main() {
    echo "=========================================================="
    echo "         SCRAPSAATHI HEALTH CHECK EVALUATION              "
    echo "=========================================================="
    check_curl

    local exit_code=0
    check_endpoint "${HEALTH_URL}" "Global Health" || exit_code=$?
    if [ ${exit_code} -ne 0 ]; then
        exit ${exit_code}
    fi

    check_endpoint "${API_HEALTH_URL}" "API v1 Health" || exit_code=$?
    if [ ${exit_code} -ne 0 ]; then
        exit ${exit_code}
    fi

    echo "=========================================================="
    log_ok "All ScrapSaathi health probes passed successfully."
    echo "=========================================================="
    exit 0
}

main "$@"
