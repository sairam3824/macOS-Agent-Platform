"""Finder automation via AppleScript."""
import subprocess
import os
from pathlib import Path
from backend.automation.applescript import run_applescript
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def open_finder(path: str | None = None) -> bool:
    if path:
        script = f'tell application "Finder" to open POSIX file "{path}"'
    else:
        script = 'tell application "Finder" to activate'
    try:
        await run_applescript(script)
        return True
    except Exception as e:
        logger.error(f"Finder open error: {e}")
        return False


async def get_downloads_folder() -> str:
    return str(Path.home() / "Downloads")


async def get_latest_downloads(count: int = 5) -> list[dict]:
    downloads = Path.home() / "Downloads"
    if not downloads.exists():
        return []

    files = sorted(downloads.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)
    result = []
    for f in files[:count]:
        stat = f.stat()
        result.append({
            "name": f.name,
            "path": str(f),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "type": f.suffix,
        })
    return result


async def search_files(query: str, location: str = "~") -> list[str]:
    """Use mdfind (Spotlight) to search files."""
    try:
        expanded = os.path.expanduser(location)
        result = subprocess.run(
            ["mdfind", "-onlyin", expanded, query],
            capture_output=True, text=True, timeout=15
        )
        paths = [p.strip() for p in result.stdout.splitlines() if p.strip()]
        return paths[:20]
    except Exception as e:
        logger.error(f"File search error: {e}")
        return []


async def open_file(path: str) -> bool:
    try:
        result = subprocess.run(["open", path], capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Failed to open file {path}: {e}")
        return False


async def reveal_in_finder(path: str) -> bool:
    script = f'tell application "Finder" to reveal POSIX file "{path}"'
    try:
        await run_applescript(script)
        await run_applescript('tell application "Finder" to activate')
        return True
    except Exception as e:
        logger.error(f"Reveal in Finder error: {e}")
        return False
