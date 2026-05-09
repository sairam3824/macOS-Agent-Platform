"""Browser automation via AppleScript (Safari/Chrome)."""
import subprocess
from backend.automation.applescript import run_applescript
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def open_url(url: str, browser: str = "default") -> bool:
    try:
        result = subprocess.run(["open", url], capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Failed to open URL {url}: {e}")
        return False


async def get_chrome_active_tab_url() -> str:
    script = '''
tell application "Google Chrome"
    return URL of active tab of first window
end tell
'''
    try:
        return await run_applescript(script)
    except Exception:
        return ""


async def get_safari_active_tab_url() -> str:
    script = '''
tell application "Safari"
    return URL of current tab of first window
end tell
'''
    try:
        return await run_applescript(script)
    except Exception:
        return ""


async def open_new_tab(url: str, browser: str = "chrome") -> bool:
    if browser == "chrome":
        script = f'''
tell application "Google Chrome"
    tell first window
        make new tab with properties {{URL:"{url}"}}
    end tell
    activate
end tell
'''
    else:
        script = f'''
tell application "Safari"
    tell first window
        make new tab with properties {{URL:"{url}"}}
    end tell
    activate
end tell
'''
    try:
        await run_applescript(script)
        return True
    except Exception as e:
        logger.error(f"Failed to open new tab: {e}")
        return open_url(url)


async def get_chrome_tabs() -> list[dict]:
    script = '''
tell application "Google Chrome"
    set tabList to ""
    repeat with w in windows
        repeat with t in tabs of w
            set tabList to tabList & title of t & "|||" & URL of t & "---SPLIT---"
        end repeat
    end repeat
    return tabList
end tell
'''
    try:
        raw = await run_applescript(script)
        tabs = []
        for entry in raw.split("---SPLIT---"):
            entry = entry.strip()
            if not entry:
                continue
            parts = entry.split("|||")
            if len(parts) >= 2:
                tabs.append({"title": parts[0], "url": parts[1]})
        return tabs
    except Exception as e:
        logger.error(f"Failed to get Chrome tabs: {e}")
        return []
