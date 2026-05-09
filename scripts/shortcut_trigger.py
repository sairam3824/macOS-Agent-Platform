#!/usr/bin/env python3
"""
Global keyboard shortcut daemon.
Press Cmd+Shift+Space to send selected text to the agent.
Runs as a background process alongside the main server.

Usage: python3 scripts/shortcut_trigger.py
"""

import subprocess
import threading
import httpx
from pynput import keyboard

API_BASE = "http://127.0.0.1:8000"
SHORTCUT = {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char(' ')}
_current_keys: set = set()
_lock = threading.Lock()


def get_selected_text() -> str:
    """Read selected text via clipboard after simulating Cmd+C."""
    script = '''
tell application "System Events"
    keystroke "c" using command down
end tell
delay 0.15
return the clipboard
'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return ""


def send_to_agent(text: str):
    """POST the selected text to the agent chat endpoint."""
    try:
        resp = httpx.post(
            f"{API_BASE}/api/agent/chat",
            json={
                "message": f"The user selected the following text. Please analyze or summarize it:\n\n{text}",
                "session_id": "shortcut-trigger",
                "allow_actions": True,
            },
            timeout=60,
        )
        data = resp.json()
        print(f"\n[Agent] {data.get('message', '')[:300]}")
        print(f"Model: {data.get('model_used', '?')}\n")
    except Exception as e:
        print(f"[Error] Could not reach agent: {e}")


def trigger():
    print("[Shortcut] Triggered — reading selection...")
    text = get_selected_text()
    if text:
        print(f"[Shortcut] Sending: {text[:80]}...")
        threading.Thread(target=send_to_agent, args=(text,), daemon=True).start()
    else:
        print("[Shortcut] No text selected")


def on_press(key):
    with _lock:
        _current_keys.add(key)
        if all(k in _current_keys for k in SHORTCUT):
            _current_keys.clear()
            trigger()


def on_release(key):
    with _lock:
        _current_keys.discard(key)


if __name__ == "__main__":
    print("macOS Agent Global Shortcut Daemon")
    print("Press Cmd+Shift+Space to analyze selected text")
    print("Ctrl+C to quit\n")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
