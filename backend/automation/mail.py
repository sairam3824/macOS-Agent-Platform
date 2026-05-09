"""Mail.app automation via AppleScript."""
from backend.automation.applescript import run_applescript
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def get_recent_emails(count: int = 10) -> list[dict]:
    """Fetch metadata for recent inbox emails."""
    script = f"""
tell application "Mail"
    set inbox to inbox
    set theMessages to messages of inbox
    set recentMessages to items 1 thru (minimum of {count} and (count of theMessages)) of theMessages
    set output to ""
    repeat with aMessage in recentMessages
        set msgSubject to subject of aMessage
        set msgSender to sender of aMessage
        set msgDate to date received of aMessage as string
        set msgRead to read status of aMessage
        set output to output & msgSubject & "|||" & msgSender & "|||" & msgDate & "|||" & msgRead & "---SPLIT---"
    end repeat
    return output
end tell
"""
    try:
        raw = await run_applescript(script)
        emails = []
        for line in raw.split("---SPLIT---"):
            line = line.strip()
            if not line:
                continue
            parts = line.split("|||")
            if len(parts) >= 4:
                emails.append({
                    "subject": parts[0],
                    "sender": parts[1],
                    "date": parts[2],
                    "read": parts[3].lower() == "true",
                })
        return emails
    except Exception as e:
        logger.error(f"Failed to read Mail: {e}")
        return []


async def get_unread_count() -> int:
    script = 'tell application "Mail" to return unread count of inbox'
    try:
        result = await run_applescript(script)
        return int(result)
    except Exception:
        return 0


async def open_mail() -> bool:
    try:
        await run_applescript('tell application "Mail" to activate')
        return True
    except Exception as e:
        logger.error(f"Failed to open Mail: {e}")
        return False


async def draft_email(to: str, subject: str, body: str) -> bool:
    """Create a draft email without sending it."""
    escaped_body = body.replace('"', '\\"')
    escaped_subject = subject.replace('"', '\\"')
    escaped_to = to.replace('"', '\\"')

    script = f"""
tell application "Mail"
    set newMessage to make new outgoing message with properties {{subject:"{escaped_subject}", content:"{escaped_body}", visible:true}}
    tell newMessage
        make new to recipient at end of to recipients with properties {{address:"{escaped_to}"}}
    end tell
    activate
end tell
"""
    try:
        await run_applescript(script)
        return True
    except Exception as e:
        logger.error(f"Failed to draft email: {e}")
        return False
