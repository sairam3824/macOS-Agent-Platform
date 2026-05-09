# macOS Agent Platform

A local-first macOS desktop agent. Runs AI entirely on your machine using Ollama (Gemma, Llama, Mistral, etc.) with optional cloud fallback via OpenAI or Anthropic.

## Features

- **Local-first**: Gemma 3 4B runs on your Mac via Ollama — no cloud required
- **macOS automation**: Opens apps, reads files, inspects Finder, drafts emails via AppleScript
- **Screenshot & OCR**: Captures screen, extracts text from images
- **Global shortcut**: `Cmd+Shift+Space` sends selected text to the agent
- **Permission system**: Risk-leveled approval flow before any side-effectful action
- **Web UI**: Dashboard, chat console, action logs, settings — served locally at `localhost:8000`
- **Dry-run mode**: Simulate all actions without executing them

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS |
| Backend | Python FastAPI + uvicorn |
| Local LLM | Ollama (Gemma 3 4B default) |
| Storage | SQLite via SQLAlchemy async |
| macOS automation | AppleScript via `osascript` subprocess |
| Secrets | macOS Keychain via `keyring` |
| OCR | Tesseract + pytesseract |
| Global shortcut | pynput |

## Quick Start

### Prerequisites

```bash
# Install Ollama
brew install ollama

# Install Tesseract (optional, for OCR)
brew install tesseract

# Node.js (for building the frontend)
brew install node
```

### Setup

```bash
cd /path/to/Agent
./scripts/setup.sh
```

This will:
1. Create a Python virtual environment
2. Install all Python dependencies
3. Build the React frontend
4. Copy `.env.example` → `.env`

### Run

```bash
./scripts/start.sh
```

Opens `http://localhost:8000` automatically. Complete the onboarding flow to pick your model and optionally add cloud API keys.

### Development mode (hot reload)

```bash
./scripts/dev.sh
```

Backend reloads on file changes. Frontend served at `http://localhost:5173`.

### Global Shortcut Daemon (optional)

```bash
python3 scripts/shortcut_trigger.py
```

Then select any text and press `Cmd+Shift+Space` to instantly analyze it.

## Architecture

```
Agent/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings (env-driven)
│   ├── database.py             # SQLite models
│   ├── agent/
│   │   ├── orchestrator.py     # Agentic loop (LLM → tool → result)
│   │   ├── tools.py            # Tool definitions for LLM
│   │   └── permissions.py      # Approval tracking
│   ├── automation/
│   │   ├── applescript.py      # AppleScript runner
│   │   ├── actions.py          # Action registry + dispatcher
│   │   ├── mail.py             # Mail.app integration
│   │   ├── finder.py           # Finder + file search
│   │   └── browser.py          # Chrome/Safari control
│   ├── services/
│   │   ├── llm_router.py       # Ollama / OpenAI / Anthropic routing
│   │   ├── ollama_service.py   # Ollama HTTP client
│   │   ├── screenshot.py       # Screen capture
│   │   ├── ocr_service.py      # Tesseract OCR
│   │   └── keychain_service.py # macOS Keychain API keys
│   └── routes/                 # FastAPI routers
├── frontend/
│   └── src/
│       ├── pages/              # Onboarding, Dashboard, Chat, Settings, Logs, Permissions
│       ├── components/         # ChatMessage, ModelSelector, PermissionModal, FileDropzone
│       ├── store/              # Zustand global state
│       └── api/client.ts       # Type-safe API layer
├── scripts/
│   ├── setup.sh               # One-time setup
│   ├── start.sh               # Production start
│   ├── dev.sh                 # Hot-reload dev mode
│   └── shortcut_trigger.py    # Global Cmd+Shift+Space daemon
└── data/                      # SQLite DB + logs (auto-created)
```

## macOS Permissions Required

| Permission | Where to grant | Used for |
|---|---|---|
| Screen Recording | System Settings → Privacy → Screen Recording | Screenshots |
| Accessibility | System Settings → Privacy → Accessibility | UI automation |
| Automation | Auto-prompted on first use | AppleScript (Mail, Finder, apps) |

## Example Commands

Type these in the Chat console:

- `Summarize the selected text`
- `Take a screenshot and describe what's happening`
- `Open my latest downloaded PDF`
- `Check recent emails and tell me which are urgent`
- `Search for files containing "invoice" in Downloads`
- `What app am I currently using?`
- `Open Google Docs in the browser`
- `Draft a reply to the latest email from John`
- `Extract all text from this image` (attach an image first)

## Configuration

Edit `.env` to configure:

```bash
OLLAMA_DEFAULT_MODEL=gemma3:4b   # Change to gemma3:12b for better quality
MODEL_ROUTING=local_first         # local_first | cloud_first | local_only
REQUIRE_CONFIRMATION_FOR_ACTIONS=true
DRY_RUN_MODE=false
SAFE_MODE=false
```

## Phase 2 Roadmap

- [ ] Multi-agent planning (sequential task decomposition)
- [ ] Browser automation (Playwright)
- [ ] Vision-capable local models (LLaVA, BakLLaVA)
- [ ] Spreadsheet understanding (Numbers, Excel)
- [ ] Calendar integration
- [ ] Voice trigger (Whisper)
- [ ] Menu bar app (rumps)
- [ ] Long-term memory (vector store)
- [ ] Plugin marketplace

## Privacy

All data stays on your machine. Logs are stored in `./data/`. API keys are stored in the macOS Keychain, never in plaintext files. The agent only makes network requests when using a cloud model you've explicitly configured.
