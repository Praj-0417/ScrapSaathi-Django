#!/usr/bin/env bash
# ==============================================================================
# collect_diagnostics.sh - ScrapSaathi Operational System Diagnostics
# Gathers system resource utilization, listening ports, process states, and logs.
# Produces a clean, timestamped diagnostic report for incident troubleshooting.
# ==============================================================================

set -o pipefail

REPORT_DIR="${REPORT_DIR:-./diagnostics}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="${REPORT_DIR}/diagnostics_${TIMESTAMP}.log"

mkdir -p "${REPORT_DIR}"

log_section() {
    echo "" | tee -a "${REPORT_FILE}"
    echo "==========================================================" | tee -a "${REPORT_FILE}"
    echo "  $1" | tee -a "${REPORT_FILE}"
    echo "==========================================================" | tee -a "${REPORT_FILE}"
}

echo "Generating ScrapSaathi System Diagnostic Report..."
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S %Z')" | tee "${REPORT_FILE}"
echo "Hostname:  $(hostname 2>/dev/null || echo 'Unknown')" | tee -a "${REPORT_FILE}"
echo "OS Info:   $(uname -a 2>/dev/null || echo 'Unknown')" | tee -a "${REPORT_FILE}"

# 1. Process Status
log_section "1. APPLICATION & PYTHON PROCESSES (ps / pgrep)"
if command -v pgrep &>/dev/null; then
    echo "Python processes running:" | tee -a "${REPORT_FILE}"
    ps -ef | grep -E "python|gunicorn|manage.py" | grep -v grep | tee -a "${REPORT_FILE}" || echo "No active python processes found." | tee -a "${REPORT_FILE}"
else
    echo "pgrep/ps not available in current shell environment." | tee -a "${REPORT_FILE}"
fi

# 2. Port & Network Activity
log_section "2. NETWORK & LISTENING SOCKETS (ss / netstat / lsof)"
if command -v ss &>/dev/null; then
    echo "Listening TCP sockets:" | tee -a "${REPORT_FILE}"
    ss -tulpn | grep -E ":8000|:5432|:9090|:3000|:3001" | tee -a "${REPORT_FILE}" || ss -tulpn | head -n 15 | tee -a "${REPORT_FILE}"
elif command -v netstat &>/dev/null; then
    (netstat -tuln 2>/dev/null || netstat -an 2>/dev/null) | head -n 20 | tee -a "${REPORT_FILE}"
else
    echo "ss/netstat not available." | tee -a "${REPORT_FILE}"
fi

# 3. Memory & Resource Consumption
log_section "3. MEMORY UTILIZATION (free -m)"
if command -v free &>/dev/null; then
    free -m | tee -a "${REPORT_FILE}"
else
    echo "free command not available." | tee -a "${REPORT_FILE}"
fi

# 4. Storage & Disk Capacity
log_section "4. DISK STORAGE & VOLUME USAGE (df -h)"
if command -v df &>/dev/null; then
    df -h . | tee -a "${REPORT_FILE}"
else
    echo "df command not available." | tee -a "${REPORT_FILE}"
fi

# 5. Database Connection Test
log_section "5. DATABASE CONNECTIVITY & RECORD STATS"
if [ -f "backend/manage.py" ]; then
    echo "Querying Django DB stats via Python:" | tee -a "${REPORT_FILE}"
    PY_BIN="python"
    if [ -f ".venv/bin/python" ]; then
        PY_BIN=".venv/bin/python"
    elif [ -f ".venv/Scripts/python.exe" ]; then
        PY_BIN=".venv/Scripts/python.exe"
    fi
    "${PY_BIN}" backend/manage.py shell -c "
from users.models import User
from pickups.models import PickupRequest
from rates.models import ScrapItem
print(f'Users count:    {User.objects.count()}')
print(f'Pickups count:  {PickupRequest.objects.count()}')
print(f'Scrap Items:    {ScrapItem.objects.count()}')
" 2>&1 | tee -a "${REPORT_FILE}" || echo "Could not query Django database stats." | tee -a "${REPORT_FILE}"
fi

# 6. Recent Logs
log_section "6. RECENT APPLICATION LOG SNIPPET"
if [ -f "backend/scrapsaathi.log" ]; then
    tail -n 30 "backend/scrapsaathi.log" | tee -a "${REPORT_FILE}"
else
    echo "No local scrapsaathi.log file found. Standard output logs are captured by container/systemd." | tee -a "${REPORT_FILE}"
fi

log_section "REPORT GENERATION COMPLETE"
echo "Diagnostic artifact written to: ${REPORT_FILE}"
