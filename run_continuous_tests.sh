#!/usr/bin/env bash
set -euo pipefail

# Select Python interpreter
if [ -n "${PYTHON_BIN:-}" ]; then
    :
elif [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

echo "Using Python: $PYTHON_BIN"

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt

export FLASK_SECRET_KEY="${FLASK_SECRET_KEY:-ci-secret-key}"
export BASE_URL="${BASE_URL:-http://127.0.0.1:5000}"

echo "USERNAME present: $([ -n "${USERNAME:-}" ] && echo yes || echo no)"
echo "PASSWORD present: $([ -n "${PASSWORD:-}" ] && echo yes || echo no)"

"$PYTHON_BIN" app.py >/tmp/qa-portfolio.log 2>&1 &
APP_PID=$!

cleanup() {
    kill "$APP_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "Waiting for API..."

for i in {1..20}; do
    if curl -sf "$BASE_URL/ping" >/dev/null; then
        echo "API is ready."
        break
    fi
    sleep 1
done

"$PYTHON_BIN" -m pytest \
    -v \
    -s \
    -m cont_test \
    tests/api/test_cases/