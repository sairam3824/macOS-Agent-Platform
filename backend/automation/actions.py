"""Registry of all automation actions with metadata."""
import subprocess
from backend.automation import applescript, mail, finder, browser
from backend.services import screenshot, ocr_service
from backend.models.action import ActionCategory, RiskLevel, ActionDefinition, ActionResult
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# All registered actions with their risk levels
ACTION_REGISTRY: dict[str, ActionDefinition] = {
    "capture_screen": ActionDefinition(
        name="capture_screen",
        description="Take a screenshot of the current screen",
        category=ActionCategory.screenshot,
        risk_level=RiskLevel.low,
        requires_permission=True,
    ),
    "read_clipboard": ActionDefinition(
        name="read_clipboard",
        description="Read text from the clipboard",
        category=ActionCategory.clipboard,
        risk_level=RiskLevel.low,
    ),
    "write_clipboard": ActionDefinition(
        name="write_clipboard",
        description="Write text to the clipboard",
        category=ActionCategory.clipboard,
        risk_level=RiskLevel.low,
    ),
    "open_app": ActionDefinition(
        name="open_app",
        description="Open a macOS application",
        category=ActionCategory.app_control,
        risk_level=RiskLevel.low,
        parameters_schema={"app_name": "string"},
    ),
    "open_file": ActionDefinition(
        name="open_file",
        description="Open a file with its default application",
        category=ActionCategory.file,
        risk_level=RiskLevel.low,
        parameters_schema={"path": "string"},
    ),
    "search_files": ActionDefinition(
        name="search_files",
        description="Search for files using Spotlight",
        category=ActionCategory.finder,
        risk_level=RiskLevel.low,
        parameters_schema={"query": "string", "location": "string"},
    ),
    "get_latest_downloads": ActionDefinition(
        name="get_latest_downloads",
        description="List the most recently downloaded files",
        category=ActionCategory.finder,
        risk_level=RiskLevel.low,
    ),
    "get_recent_emails": ActionDefinition(
        name="get_recent_emails",
        description="Read recent email metadata from Mail.app",
        category=ActionCategory.mail,
        risk_level=RiskLevel.low,
        requires_permission=True,
    ),
    "draft_email": ActionDefinition(
        name="draft_email",
        description="Create an email draft (does NOT send it)",
        category=ActionCategory.mail,
        risk_level=RiskLevel.medium,
        requires_permission=True,
        parameters_schema={"to": "string", "subject": "string", "body": "string"},
    ),
    "send_email": ActionDefinition(
        name="send_email",
        description="Send an email — requires explicit confirmation",
        category=ActionCategory.mail,
        risk_level=RiskLevel.high,
        requires_permission=True,
        parameters_schema={"to": "string", "subject": "string", "body": "string"},
    ),
    "open_url": ActionDefinition(
        name="open_url",
        description="Open a URL in the default browser",
        category=ActionCategory.browser,
        risk_level=RiskLevel.low,
        parameters_schema={"url": "string"},
    ),
    "extract_text_from_image": ActionDefinition(
        name="extract_text_from_image",
        description="Use OCR to extract text from an image",
        category=ActionCategory.screenshot,
        risk_level=RiskLevel.low,
    ),
    "reveal_in_finder": ActionDefinition(
        name="reveal_in_finder",
        description="Reveal a file in Finder",
        category=ActionCategory.finder,
        risk_level=RiskLevel.low,
        parameters_schema={"path": "string"},
    ),
    "get_frontmost_app": ActionDefinition(
        name="get_frontmost_app",
        description="Get the name of the currently active app",
        category=ActionCategory.system,
        risk_level=RiskLevel.low,
    ),
    "get_chrome_tabs": ActionDefinition(
        name="get_chrome_tabs",
        description="List open Chrome browser tabs",
        category=ActionCategory.browser,
        risk_level=RiskLevel.low,
    ),
}


async def execute_action(name: str, parameters: dict, dry_run: bool = False) -> ActionResult:
    """Dispatch an action by name and return its result."""
    if name not in ACTION_REGISTRY:
        return ActionResult(action_name=name, success=False, error=f"Unknown action: {name}", dry_run=dry_run)

    if dry_run:
        definition = ACTION_REGISTRY[name]
        return ActionResult(
            action_name=name,
            success=True,
            output=f"[DRY RUN] Would execute: {definition.description} with params: {parameters}",
            dry_run=True,
        )

    try:
        if name == "capture_screen":
            b64 = await screenshot.capture_screen(parameters.get("region"))
            return ActionResult(action_name=name, success=True, output={"screenshot_b64": b64})

        elif name == "read_clipboard":
            raw = await applescript.run_applescript(applescript.build_clipboard_read_script())
            return ActionResult(action_name=name, success=True, output=raw)

        elif name == "write_clipboard":
            script = applescript.build_clipboard_write_script(parameters.get("text", ""))
            await applescript.run_applescript(script)
            return ActionResult(action_name=name, success=True, output="Written to clipboard")

        elif name == "open_app":
            app = parameters.get("app_name", "")
            script = applescript.build_open_app_script(app)
            await applescript.run_applescript(script)
            return ActionResult(action_name=name, success=True, output=f"Opened {app}")

        elif name == "open_file":
            path = parameters.get("path", "")
            success = await finder.open_file(path)
            return ActionResult(action_name=name, success=success, output=f"Opened {path}")

        elif name == "search_files":
            results = await finder.search_files(
                parameters.get("query", ""),
                parameters.get("location", "~"),
            )
            return ActionResult(action_name=name, success=True, output=results)

        elif name == "get_latest_downloads":
            files = await finder.get_latest_downloads(parameters.get("count", 5))
            return ActionResult(action_name=name, success=True, output=files)

        elif name == "get_recent_emails":
            emails = await mail.get_recent_emails(parameters.get("count", 10))
            return ActionResult(action_name=name, success=True, output=emails)

        elif name == "draft_email":
            success = await mail.draft_email(
                parameters.get("to", ""),
                parameters.get("subject", ""),
                parameters.get("body", ""),
            )
            return ActionResult(action_name=name, success=success, output="Draft created in Mail.app")

        elif name == "open_url":
            success = await browser.open_url(parameters.get("url", ""))
            return ActionResult(action_name=name, success=success, output=f"Opened {parameters.get('url')}")

        elif name == "extract_text_from_image":
            b64 = parameters.get("image_b64", "")
            text = await ocr_service.extract_text_from_base64(b64)
            return ActionResult(action_name=name, success=True, output=text)

        elif name == "reveal_in_finder":
            success = await finder.reveal_in_finder(parameters.get("path", ""))
            return ActionResult(action_name=name, success=success, output="Revealed in Finder")

        elif name == "get_frontmost_app":
            app = await applescript.run_applescript(applescript.build_get_frontmost_app_script())
            return ActionResult(action_name=name, success=True, output=app)

        elif name == "get_chrome_tabs":
            tabs = await browser.get_chrome_tabs()
            return ActionResult(action_name=name, success=True, output=tabs)

        else:
            return ActionResult(action_name=name, success=False, error=f"Unhandled action: {name}")

    except Exception as e:
        logger.error(f"Action {name} failed: {e}")
        return ActionResult(action_name=name, success=False, error=str(e))
