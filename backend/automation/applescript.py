"""AppleScript runner with error handling and timeout protection."""
import subprocess
import asyncio
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def run_applescript(script: str, timeout: int = 30) -> str:
    """Execute an AppleScript and return its stdout output."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "osascript", "-e", script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

        if proc.returncode != 0:
            err = stderr.decode().strip()
            logger.warning(f"AppleScript returned {proc.returncode}: {err}")
            raise RuntimeError(f"AppleScript error: {err}")

        return stdout.decode().strip()
    except asyncio.TimeoutError:
        proc.kill()
        raise TimeoutError(f"AppleScript timed out after {timeout}s")


async def run_applescript_file(path: str, timeout: int = 30) -> str:
    proc = await asyncio.create_subprocess_exec(
        "osascript", path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"AppleScript error: {stderr.decode().strip()}")
    return stdout.decode().strip()


def build_open_app_script(app_name: str) -> str:
    return f'tell application "{app_name}" to activate'


def build_open_file_script(file_path: str) -> str:
    return f'tell application "Finder" to open POSIX file "{file_path}"'


def build_get_frontmost_app_script() -> str:
    return 'tell application "System Events" to get name of first application process whose frontmost is true'


def build_get_selected_text_script() -> str:
    return '''
tell application "System Events"
    keystroke "c" using command down
end tell
delay 0.2
return the clipboard
'''


def build_clipboard_read_script() -> str:
    return "return the clipboard"


def build_clipboard_write_script(text: str) -> str:
    escaped = text.replace('"', '\\"')
    return f'set the clipboard to "{escaped}"'
