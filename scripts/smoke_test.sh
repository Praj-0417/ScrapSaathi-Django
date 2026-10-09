#!/usr/bin/env bash
# ==============================================================================
# smoke_test.sh - ScrapSaathi End-to-End API Smoke Test
# Exercises core REST endpoints to verify routing, serializers, and DB queries.
# ==============================================================================

set -o pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
FAILED_TESTS=0
TOTAL_TESTS=0

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

test_endpoint() {
    local method="$1"
    local endpoint="$2"
    local expected_code="$3"
    local data="$4"
    local description="$5"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}[TEST ${TOTAL_TESTS}]${NC} ${description} (${method} ${endpoint})..."

    local curl_args=(-s -o /tmp/smoke_out.txt -w "%{http_code}" -X "${method}")
    if [ -n "${data}" ]; then
        curl_args+=(-H "Content-Type: application/json" -d "${data}")
    fi

    local status
    status=$(curl "${curl_args[@]}" "${BASE_URL}${endpoint}")

    if [ "${status}" -eq "${expected_code}" ]; then
        echo -e "       ${GREEN}PASS${NC} - HTTP ${status} matches expected ${expected_code}"
    else
        echo -e "       ${RED}FAIL${NC} - Received HTTP ${status}, expected ${expected_code}"
        echo "       Response snippet: $(head -c 200 /tmp/smoke_out.txt 2>/dev/null || echo 'None')"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo "=========================================================="
echo "          SCRAPSAATHI SMOKE TEST SUITE                    "
echo "Target Base URL: ${BASE_URL}"
echo "=========================================================="

# 1. Global health check
test_endpoint "GET" "/health" 200 "" "Global Health Probe"

# 2. Canonical API v1 health
test_endpoint "GET" "/api/v1/health" 200 "" "API v1 Health Probe"

# 3. Canonical API alias health
test_endpoint "GET" "/api/health" 200 "" "API Canonical Alias Probe"

# 4. Prometheus metrics exposition
test_endpoint "GET" "/metrics" 200 "" "Prometheus Metrics Exporter"

# 5. Public scrap rates board
test_endpoint "GET" "/api/v1/rates?city=delhi-ncr" 200 "" "Rates Catalog by City (Delhi NCR)"

# 6. Serviceability evaluation
test_endpoint "GET" "/api/v1/geocode/serviceable?lat=28.6315&lon=77.2167" 200 "" "Serviceability Verification (Connaught Place)"

# 7. Unserviceable boundary check
test_endpoint "GET" "/api/v1/geocode/serviceable?lat=34.1526&lon=77.5771" 200 "" "Serviceability Out of Bounds (Leh Ladakh)"

# 8. Geocode directory lookup
test_endpoint "GET" "/api/v1/geocode/search?q=Connaught" 200 "" "Geocode Locality Search"

# 9. OTP send registration probe
TEST_EMAIL="smoke_test_$(date +%s)@example.com"
test_endpoint "POST" "/api/v1/auth/otp/send-registration" 200 "{\"email\":\"${TEST_EMAIL}\"}" "OTP Send Challenge"

# 10. Registration rejects without OTP challenge token
test_endpoint "POST" "/api/v1/auth/register" 400 "{\"email\":\"${TEST_EMAIL}\",\"password\":\"Test1234!\",\"name\":\"Smoke Tester\",\"phone\":\"9876543210\"}" "Registration OTP Enforcement"

echo "=========================================================="
echo "TEST RESULTS: Total: ${TOTAL_TESTS} | Passed: $((TOTAL_TESTS - FAILED_TESTS)) | Failed: ${FAILED_TESTS}"
echo "=========================================================="

rm -f /tmp/smoke_out.txt

if [ "${FAILED_TESTS}" -eq 0 ]; then
    echo -e "${GREEN}SMOKE TEST SUITE PASSED COMPREHENSIVELY!${NC}"
    exit 0
else
    echo -e "${RED}SMOKE TEST SUITE FAILED WITH ${FAILED_TESTS} FAILURES!${NC}"
    exit 1
fi
