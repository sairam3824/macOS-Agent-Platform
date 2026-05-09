"""Screenshot capture and image utilities for macOS."""
import subprocess
import base64
import tempfile
import os
from pathlib import Path
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def capture_screen(region: dict | None = None) -> str:
    """Capture full screen or region, return base64-encoded PNG."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp_path = f.name

    try:
        cmd = ["screencapture", "-x", tmp_path]
        if region:
            x, y, w, h = region["x"], region["y"], region["width"], region["height"]
            cmd = ["screencapture", "-x", f"-R{x},{y},{w},{h}", tmp_path]

        result = subprocess.run(cmd, capture_output=True, timeout=10)
        if result.returncode != 0:
            raise RuntimeError(f"screencapture failed: {result.stderr.decode()}")

        with open(tmp_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


async def image_file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def get_image_size(b64_data: str) -> tuple[int, int]:
    """Return (width, height) of base64-encoded image."""
    from PIL import Image
    import io
    data = base64.b64decode(b64_data)
    img = Image.open(io.BytesIO(data))
    return img.size
