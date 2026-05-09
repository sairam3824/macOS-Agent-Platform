Act as a senior staff engineer building a **local-first macOS desktop agent platform**. Design and implement a production-minded application that combines:

* local LLM execution via Ollama
* optional cloud APIs via OpenAI and Anthropic
* a browser-based local control panel
* macOS automation
* screenshot/image understanding
* selected-text workflows
* email/file/app control
* strict permissions and safety approvals

Do not build a toy demo. Build a modular, extensible foundation for a real product.

Priorities:

1. privacy-first local execution
2. safe action execution
3. clean UX
4. maintainable architecture
5. strong macOS integration
6. real MVP functionality

Begin with architecture and implementation plan, then generate the project in a staged way.


Build a **production-grade macOS desktop automation agent** with a modern web app UI and local-first architecture.

## Core Goal

I want an application for **macOS** that acts like an intelligent desktop agent. It should let me start a local server, open a web application, choose a local model, optionally add cloud API keys, and then use the agent to understand my screen, process selected content, read images, and control my MacBook apps like Docs, Excel, Mail, Finder, browser, etc.

The app should be **local-first**, use **local models by default**, and support optional APIs like **OpenAI** and **Anthropic**.

---

## Main Product Requirements

### 1. Startup Experience

When I start the server for the first time:

* Open a web application in the browser automatically
* Show a clean onboarding/setup flow
* Let me select a **local model provider**, primarily **Ollama**
* Detect installed Ollama models if possible
* Let me choose a default local model
* Let me optionally add API keys for:

  * OpenAI
  * Anthropic
* Store API keys securely in macOS Keychain or another secure encrypted local storage
* Let me continue fully without cloud API keys

### 2. Local Model First

The agent should prefer:

* **Ollama** for local LLMs
* Optional fallback or advanced routing to OpenAI / Anthropic if configured
* Support model routing rules like:

  * use local model for normal tasks
  * use cloud model only if user explicitly allows or for specific advanced tasks

### 3. Agent Abilities

The agent should handle:

* user-selected text or files through a shortcut
* screenshots and image understanding
* OCR / screen parsing
* file understanding
* action execution on macOS apps

Examples of what I want:

* I select text and trigger shortcut → agent analyzes and gives output
* I provide an image → agent scans it and extracts meaning / text / structured data
* Agent can open apps like:

  * Mail
  * Finder
  * Notes
  * Google Docs in browser
  * Excel / Numbers / spreadsheets
  * PDFs
  * browser tabs
* Agent can read latest mails if permissions are granted
* Agent can summarize recent emails
* Agent can open files and navigate them
* Agent can inspect screen content and decide next action
* Agent can perform multi-step workflows safely

### 4. macOS Control

I want the app to behave like a real desktop agent for macOS.

Include support for:

* AppleScript
* Shortcuts integration
* Accessibility permissions
* Screen capture permissions
* Controlled UI automation
* Keyboard/mouse automation only when needed
* Opening and interacting with apps/windows/tabs/files

Actions should include:

* open app
* open file
* search Finder
* open latest downloads
* read clipboard
* use selected text
* take screenshot
* inspect visible screen
* draft email
* read recent email metadata
* summarize inbox
* open spreadsheet / doc / pdf
* extract data from images and documents

### 5. Triggering the Agent

I want multiple trigger modes:

* a global keyboard shortcut
* menu bar app
* web app input box
* right-click / services / share sheet if possible
* selected text trigger
* image/file trigger

Example flows:

1. Start server
2. Open web app
3. Choose local model
4. Set optional API keys
5. Use shortcut on selected content
6. Agent processes the content and either:

   * returns an answer
   * asks for permission
   * performs an action on the Mac

### 6. Safety and Permission Model

This is very important.

Build a clear permission system:

* Ask before sensitive actions
* Require confirmation for destructive operations
* Show planned actions before executing if high risk
* Let user approve app control permissions
* Let user toggle automation scope per app
* Keep logs of actions locally
* Include “dry-run” mode for testing
* Include “safe mode” where agent can analyze but not act

High-risk examples needing confirmation:

* sending emails
* deleting files
* moving files
* editing important documents
* bulk actions
* browser purchases / payments / auth flows

### 7. Web Application Requirements

Build a polished web app frontend for local use.

Pages:

* onboarding / first-run setup
* dashboard
* model settings
* integrations / API keys
* permissions / safety
* action history / logs
* live chat / command console
* file / image dropzone
* agent status page

UI features:

* modern clean interface
* responsive layout
* dark mode
* model selector
* agent state indicator
* current task panel
* tool execution trace
* permission approval modal
* logs with timestamps
* settings page for shortcuts and providers

### 8. Shortcut-Based Workflows

Support workflows like:

* “Analyze selected text”
* “Summarize selected email”
* “Extract text from screenshot”
* “Open latest downloaded PDF and summarize it”
* “Read this spreadsheet and explain it”
* “Check latest mails and summarize urgent ones”
* “Look at current screen and tell me what is happening”
* “Take screenshot and extract table from it”

### 9. Image and Screen Understanding

Include:

* screenshot capture
* OCR
* image parsing
* optional vision-capable cloud models if configured
* local image understanding pipeline where possible

The agent should be able to:

* read screenshots
* extract text from scanned images
* understand UI screenshots
* inspect tables from images
* read receipts/documents/screenshots

### 10. Mail Handling

The agent should be able to:

* open Mail app
* inspect latest mails with permission
* summarize unread emails
* identify urgent ones
* draft replies but not send without confirmation
* optionally support Gmail web workflows if desktop Mail integration is hard

### 11. Architecture Expectations

Use a maintainable architecture.

Preferred stack:

* **Frontend:** Next.js or React
* **Backend:** Python FastAPI or Node.js
* **Desktop bridge / macOS automation:** Python + AppleScript / Swift helper / JXA / Shortcuts integration
* **Local model integration:** Ollama
* **Storage:** SQLite for local logs/settings
* **Secure secrets:** Keychain or encrypted local storage

Recommended architecture:

* frontend web app
* local backend API server
* agent orchestration layer
* tools/actions layer
* model routing layer
* macOS automation bridge
* permission/safety manager
* job queue / task runner
* OCR / image pipeline
* logging/telemetry layer (local only)

### 12. Implementation Quality

Please do not make this a toy project.

I want:

* clear folder structure
* real implementation
* modular code
* typed interfaces
* proper error handling
* permission prompts
* setup instructions
* example workflows
* README
* env example
* scripts for local startup
* comments where needed
* production-minded architecture

### 13. Deliverables I Want From You

Generate the project with:

1. Full folder structure
2. All core source files
3. Setup instructions
4. README
5. `.env.example`
6. Ollama integration
7. API key settings flow
8. macOS automation layer
9. web UI for onboarding + dashboard
10. shortcut integration design
11. permission system
12. sample tools/actions
13. logging system
14. example commands/prompts
15. development roadmap for missing advanced features

### 14. Important Product Behavior

The agent should always:

* default to local execution
* work even with no cloud API keys
* be privacy-first
* ask permission before risky actions
* show action trace
* support selected text, screenshots, images, files, and app control

### 15. Example User Commands

Support commands like:

* “Summarize the selected text”
* “Read this screenshot”
* “Open my latest downloaded PDF”
* “Check latest mails and summarize them”
* “Open the spreadsheet and explain the important numbers”
* “Look at my current screen and tell me what to do next”
* “Draft a reply to the latest mail”
* “Scan this image and extract all text”
* “Open Finder and locate the most recent file”
* “Open Google Docs and create a notes document”

### 16. Development Plan

Please first provide:

* the best architecture
* the module breakdown
* how macOS permissions should work
* how shortcuts should connect to the local agent
* how Ollama and optional cloud providers should be wired
* what should be MVP vs phase 2

Then generate the codebase step by step.

### 17. MVP Scope

For the first working MVP, prioritize:

* local server
* onboarding web app
* Ollama model selection
* optional API key config
* global shortcut / trigger mechanism
* selected text capture
* screenshot upload/analyze
* basic OCR
* opening apps/files
* email summary capability
* action approval flow
* logs/history
* clean local-first architecture

### 18. Advanced Phase 2

After MVP, design for:

* multi-agent planning
* browser automation
* better vision
* spreadsheet understanding
* autonomous workflows
* voice trigger
* menu bar assistant
* plugin/tool marketplace
* calendar/mail/doc integrations
* long-running memory and task context

### 19. Coding Style

Write clean, production-ready code.
Avoid fake placeholders unless clearly marked.
If a subsystem is complex, scaffold it properly with interfaces and TODO markers.
Prefer making a working vertical slice first.

Start by giving:

1. final architecture
2. tech stack choice with justification
3. folder structure
4. MVP milestones
5. then generate the codebase
