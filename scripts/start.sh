#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "ERROR: Virtual environment not found. Run ./scripts/setup.sh first."
  exit 1
fi

# Start Ollama in background if not already running
if ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
  echo "Starting Ollama..."
  ollama serve &>/dev/null &
  OLLAMA_PID=$!
  sleep 2
  echo "Ollama started (PID $OLLAMA_PID)"
else
  echo "Ollama already running"
fi

# Pull default model if not present
DEFAULT_MODEL="${OLLAMA_DEFAULT_MODEL:-gemma3:4b}"
if ollama list 2>/dev/null | grep -q "$DEFAULT_MODEL"; then
  echo "Model $DEFAULT_MODEL is ready"
else
  echo "Pulling $DEFAULT_MODEL (this may take a few minutes)..."
  ollama pull "$DEFAULT_MODEL"
fi

echo ""
echo "Starting macOS Agent backend..."
echo "API:   http://127.0.0.1:8000"
echo "Docs:  http://127.0.0.1:8000/docs"
echo ""
echo "Voice shortcut daemon (run in a separate terminal):"
echo "  python3 scripts/voice_trigger.py"
echo "  Then press Cmd+Shift+V to start/stop voice recording"
echo ""

exec python3 -m uvicorn backend.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --log-level info
