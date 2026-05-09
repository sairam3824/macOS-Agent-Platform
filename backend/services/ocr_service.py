"""OCR service using tesseract for local text extraction from images."""
import base64
import io
import tempfile
import os
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def extract_text_from_base64(image_b64: str) -> str:
    """Run OCR on a base64-encoded image, return extracted text."""
    try:
        import pytesseract
        from PIL import Image

        data = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(img)
        return text.strip()
    except ImportError:
        logger.warning("pytesseract not installed, skipping OCR")
        return "[OCR unavailable — install tesseract and pytesseract]"
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return f"[OCR error: {e}]"


async def extract_text_from_file(file_path: str) -> str:
    """Extract text from image file."""
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return await extract_text_from_base64(b64)


async def extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF using pdfminer or fallback."""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(file_path)
        return text.strip()
    except ImportError:
        # Fallback: use macOS textutil
        import subprocess
        result = subprocess.run(
            ["textutil", "-convert", "txt", "-stdout", file_path],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[PDF extraction error: {e}]"
