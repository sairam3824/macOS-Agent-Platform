#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== macOS Agent Platform Setup ==="

# Python 3.14 is too new — pydantic-core/PyO3 only support up to 3.13.
# Prefer python3.12 > python3.13 > python3.11 in that order.
find_python() {
  for cmd in python3.12 python3.13 python3.11; do
    if command -v "$cmd" &>/dev/null; then
      echo "$cmd"
      return
    fi
  done
  # Last resort: check if python3 is 3.11-3.13
  if command -v python3 &>/dev/null; then
    VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    case "$VER" in
      3.11|3.12|3.13) echo "python3"; return ;;
    esac
  fi
  echo ""
}

PYTHON=$(find_python)

if [ -z "$PYTHON" ]; then
  CURRENT=$(python3 --version 2>/dev/null || echo "not found")
  echo ""
  echo "ERROR: Python 3.11–3.13 required. You have: $CURRENT"
  echo ""
  echo "Install Python 3.12 via Homebrew:"
  echo "  brew install python@3.12"
  echo ""
  echo "Then re-run this script."
  exit 1
fi

echo "Python: $($PYTHON --version)"

if ! command -v ollama &>/dev/null; then
  echo "WARNING: Ollama not found. Install: brew install ollama"
else
  echo "Ollama: $(ollama --version 2>/dev/null | head -1 || echo found)"
fi

if command -v tesseract &>/dev/null; then
  echo "Tesseract: $(tesseract --version 2>&1 | head -1)"
else
  echo "INFO: Tesseract optional. Install: brew install tesseract"
fi

# Remove stale venv
if [ -d ".venv" ]; then
  echo "Removing old virtual environment..."
  rm -rf .venv
fi

echo "Creating virtual environment with $($PYTHON --version)..."
"$PYTHON" -m venv .venv
source .venv/bin/activate

echo "Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel -q

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env — edit it to configure"
fi

mkdir -p data/logs

if [ -d "frontend" ]; then
  echo "Installing frontend dependencies..."
  cd frontend
  if command -v npm &>/dev/null; then
    npm install --silent
    echo "Building frontend..."
    npm run build
  else
    echo "WARNING: npm not found. Install: brew install node"
  fi
  cd ..
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Start the agent:       ./scripts/start.sh"
echo "Voice shortcut daemon: python3 scripts/voice_trigger.py  (separate terminal)"
echo ""
echo "Optional local Whisper (offline voice, ~150MB download):"
echo "  source .venv/bin/activate && pip install -r requirements-voice.txt"
