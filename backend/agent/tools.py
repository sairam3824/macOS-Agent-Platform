"""Tool definitions exposed to the LLM for function-calling style agent loops."""
from backend.automation.actions import ACTION_REGISTRY


TOOL_DEFINITIONS = [
    {
        "name": "capture_screen",
        "description": "Take a screenshot of the current macOS screen",
        "parameters": {},
    },
    {
        "name": "read_clipboard",
        "description": "Read the current clipboard contents",
        "parameters": {},
    },
    {
        "name": "open_app",
        "description": "Open a macOS application by name",
        "parameters": {"app_name": {"type": "string", "description": "Name of the app, e.g. Mail, Finder"}},
    },
    {
        "name": "open_file",
        "description": "Open a file with its default app",
        "parameters": {"path": {"type": "string", "description": "Absolute path to the file"}},
    },
    {
        "name": "search_files",
        "description": "Search for files on the Mac using Spotlight",
        "parameters": {
            "query": {"type": "string"},
            "location": {"type": "string", "description": "Directory to search in, default ~"},
        },
    },
    {
        "name": "get_latest_downloads",
        "description": "List recently downloaded files",
        "parameters": {"count": {"type": "integer", "description": "Number of files to return"}},
    },
    {
        "name": "get_recent_emails",
        "description": "Read metadata of recent emails from Mail.app",
        "parameters": {"count": {"type": "integer"}},
    },
    {
        "name": "draft_email",
        "description": "Create an email draft without sending it",
        "parameters": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
    },
    {
        "name": "open_url",
        "description": "Open a URL in the default browser",
        "parameters": {"url": {"type": "string"}},
    },
    {
        "name": "extract_text_from_image",
        "description": "Use OCR to extract text from an uploaded image",
        "parameters": {"image_b64": {"type": "string", "description": "base64-encoded image"}},
    },
    {
        "name": "reveal_in_finder",
        "description": "Reveal a file in Finder",
        "parameters": {"path": {"type": "string"}},
    },
    {
        "name": "get_frontmost_app",
        "description": "Get the currently active macOS application name",
        "parameters": {},
    },
    {
        "name": "get_chrome_tabs",
        "description": "List all open Chrome browser tabs",
        "parameters": {},
    },
]


SYSTEM_PROMPT = """You are a macOS desktop agent with access to powerful tools.
You help the user by understanding their requests and using available actions to control macOS.

Rules:
1. ALWAYS prefer local actions — do not call cloud services when a local action suffices.
2. For risky actions (drafting/sending email, deleting files), state what you plan to do and list the parameters clearly before calling the tool.
3. If you need a screenshot to understand the screen, use capture_screen first.
4. If the user provides an image, analyse it carefully.
5. Respond in a clear, concise way. After taking an action, summarize what happened.
6. If you cannot complete a request, explain why and suggest alternatives.
7. Never fabricate file paths or email addresses — read them from context or ask the user.

Available tools are described in the tool list. Use them when the user's request requires macOS interaction.
"""


def build_tool_call_instructions(tool_list: list[dict]) -> str:
    """Render tool list as a text block for models that don't support native function calling."""
    lines = ["You have the following tools available. To call a tool, respond ONLY with JSON in this format:"]
    lines.append('{"tool": "<tool_name>", "parameters": {<key>: <value>}}')
    lines.append("\nAvailable tools:")
    for t in tool_list:
        param_str = ", ".join(t["parameters"].keys()) if t["parameters"] else "none"
        lines.append(f"- {t['name']}({param_str}): {t['description']}")
    lines.append("\nIf no tool is needed, respond normally in plain text.")
    return "\n".join(lines)
