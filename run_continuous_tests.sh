#!/bin/bash
set -euo pipefail

if [ -n "${PYTHON_BIN:-}" ]; then
  PYTHON_BIN="$PYTHON_BIN"
elif [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  PYTHON_BIN="python"
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt

export FLASK_SECRET_KEY="ci-secret-key"
export API_USERNAME="admin"
export API_PASSWORD="password"
export BASE_URL="http://127.0.0.1:5000"

"$PYTHON_BIN" app.py > /tmp/qa-portfolio.log 2>&1 &
APP_PID=$!

cleanup() {
  if kill -0 "$APP_PID" 2>/dev/null; then
    kill "$APP_PID"
    wait "$APP_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

for i in $(seq 1 20); do
  if curl -sf http://127.0.0.1:5000/ping >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

"$PYTHON_BIN" -m pytest -v -s -m cont_test tests/api/test_cases/test_health.py tests/api/test_cases/test_auth.py tests/api/test_cases/test_contacts.py
