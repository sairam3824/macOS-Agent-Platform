#!/usr/bin/env python3
"""
Voice trigger daemon for macOS Agent.

Shortcuts:
  Cmd+Shift+V  — Start/stop voice recording
  Cmd+Shift+Space — Send selected text to agent (text shortcut)

When you press Cmd+Shift+V:
  • Recording starts (you'll see a ● REC indicator)
  • Speak your command
  • Press Cmd+Shift+V again OR stay silent for 2.5s → recording stops
  • Audio is transcribed locally (Whisper) or via OpenAI API
  • Transcribed text is sent to the agent
  • Agent response is printed

Usage:
  python3 scripts/voice_trigger.py
"""

import threading
import subprocess
import httpx
import numpy as np
import io
import wave
import sys
import time
from collections import deque
from pynput import keyboard

API_BASE = "http://127.0.0.1:8000"
SAMPLE_RATE = 16000      # Hz — Whisper expects 16kHz
CHANNELS = 1
SILENCE_SECONDS = 2.5    # auto-stop after this much silence
SILENCE_THRESHOLD = 0.01 # RMS below this = silence

# Keyboard state
_held_keys: set = set()
_lock = threading.Lock()

# Recording state
_recording = False
_audio_frames: list = []
_record_thread: threading.Thread | None = None
_stop_event = threading.Event()


def rms(chunk: np.ndarray) -> float:
    return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2))) / 32768.0


def record_audio():
    """Record from microphone until _stop_event is set or silence detected."""
    global _audio_frames
    try:
        import sounddevice as sd
    except ImportError:
        print("[Voice] sounddevice not installed: pip install sounddevice")
        return

    _audio_frames = []
    silence_chunks = 0
    max_silence_chunks = int(SILENCE_SECONDS * SAMPLE_RATE / 1024)

    print("● REC — speak now (press Cmd+Shift+V to stop, or pause for 2.5s)")

    def callback(indata, frames, time_info, status):
        nonlocal silence_chunks
        chunk = indata.copy().flatten()
        _audio_frames.append(chunk)

        if rms(chunk * 32768) < SILENCE_THRESHOLD:
            silence_chunks += 1
        else:
            silence_chunks = 0

        if silence_chunks >= max_silence_chunks:
            _stop_event.set()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=1024,
        callback=callback,
    ):
        while not _stop_event.is_set():
            sd.sleep(50)

    print("■ Recording stopped")


def frames_to_wav(frames: list) -> bytes:
    """Convert recorded int16 numpy frames to WAV bytes."""
    audio = np.concatenate(frames, axis=0).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    return buf.getvalue()


def send_voice_to_agent(wav_bytes: bytes):
    """POST WAV to backend /api/voice/transcribe-and-chat."""
    print("Transcribing...")
    try:
        resp = httpx.post(
            f"{API_BASE}/api/voice/transcribe-and-chat",
            files={"file": ("recording.wav", wav_bytes, "audio/wav")},
            data={"session_id": "voice-trigger"},
            timeout=90,
        )
        data = resp.json()
        transcription = data.get("transcription", "")
        response = data.get("response")

        print(f"\n[You said] {transcription}")
        if response:
            print(f"[Agent]    {response.get('message', '')}")
            if response.get("actions_taken"):
                for a in response["actions_taken"]:
                    status = "✓" if a["success"] else "✗"
                    print(f"           {status} {a['action']}: {a['output_summary'][:80]}")
        print()
    except Exception as e:
        print(f"[Error] {e}")


def start_recording():
    global _recording, _record_thread, _stop_event
    if _recording:
        return
    _recording = True
    _stop_event = threading.Event()
    _record_thread = threading.Thread(target=record_audio, daemon=True)
    _record_thread.start()


def stop_and_process():
    global _recording, _record_thread
    if not _recording:
        return
    _stop_event.set()
    if _record_thread:
        _record_thread.join(timeout=5)
    _recording = False

    if not _audio_frames:
        print("[Voice] No audio captured")
        return

    wav = frames_to_wav(_audio_frames)
    threading.Thread(target=send_voice_to_agent, args=(wav,), daemon=True).start()


def get_selected_text() -> str:
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


def send_text_to_agent(text: str):
    try:
        resp = httpx.post(
            f"{API_BASE}/api/agent/chat",
            json={
                "message": f"The user selected the following text. Analyze or summarize it:\n\n{text}",
                "session_id": "shortcut-trigger",
                "allow_actions": True,
            },
            timeout=90,
        )
        data = resp.json()
        print(f"\n[You selected] {text[:100]}")
        print(f"[Agent]        {data.get('message', '')[:400]}\n")
    except Exception as e:
        print(f"[Error] {e}")


# Key combinations
VOICE_SHORTCUT = frozenset([keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('v')])
TEXT_SHORTCUT = frozenset([keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char(' ')])


def on_press(key):
    with _lock:
        _held_keys.add(key)
        current = frozenset(_held_keys)

    if current == VOICE_SHORTCUT:
        with _lock:
            _held_keys.clear()
        if _recording:
            threading.Thread(target=stop_and_process, daemon=True).start()
        else:
            threading.Thread(target=start_recording, daemon=True).start()

    elif current == TEXT_SHORTCUT:
        with _lock:
            _held_keys.clear()
        def _do():
            text = get_selected_text()
            if text:
                print(f"[Text shortcut] Sending: {text[:80]}...")
                send_text_to_agent(text)
            else:
                print("[Text shortcut] No text selected")
        threading.Thread(target=_do, daemon=True).start()


def on_release(key):
    with _lock:
        _held_keys.discard(key)
    if key == keyboard.Key.esc:
        if _recording:
            threading.Thread(target=stop_and_process, daemon=True).start()


if __name__ == "__main__":
    print("macOS Agent — Voice & Text Shortcut Daemon")
    print("  Cmd+Shift+V      → Start/stop voice recording")
    print("  Cmd+Shift+Space  → Send selected text to agent")
    print("  Esc (while rec)  → Stop recording")
    print("  Ctrl+C           → Quit\n")

    # Quick check
    try:
        import sounddevice  # noqa
        print("[OK] sounddevice available")
    except ImportError:
        print("[WARN] sounddevice missing: pip install sounddevice")

    try:
        import whisper  # noqa
        print("[OK] Local Whisper available (runs fully offline)")
    except ImportError:
        print("[INFO] Local Whisper not installed. Will use OpenAI Whisper API if key is set.")
        print("       For offline: pip install -r requirements-voice.txt")

    print()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
