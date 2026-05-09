from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import base64
from backend.models.agent import ChatRequest, ChatResponse, AgentStatus, ModelInfo, Attachment, AttachmentType
from backend.agent.orchestrator import process_chat, get_agent_status
from backend.services.llm_router import llm_router
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await process_chat(request)


@router.get("/status", response_model=AgentStatus)
async def status():
    return get_agent_status()


@router.get("/models", response_model=list[ModelInfo])
async def list_models():
    models_raw = await llm_router.get_available_models()
    return [ModelInfo(**m) for m in models_raw]


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image and return it as a base64 attachment ready for /chat."""
    content = await file.read()
    b64 = base64.b64encode(content).decode()
    mime = file.content_type or "image/png"
    return {
        "attachment": {
            "type": "image",
            "name": file.filename,
            "content": b64,
            "mime_type": mime,
        }
    }


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload a text or PDF file, return it as a text attachment."""
    from backend.services.ocr_service import extract_pdf_text
    import tempfile
    import os

    content = await file.read()
    mime = file.content_type or "application/octet-stream"

    if mime == "application/pdf" or (file.filename or "").endswith(".pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        try:
            text = await extract_pdf_text(tmp_path)
        finally:
            os.unlink(tmp_path)
        return {
            "attachment": {
                "type": "file",
                "name": file.filename,
                "content": text,
                "mime_type": "text/plain",
            }
        }

    # Try decode as text
    try:
        text = content.decode("utf-8")
    except Exception:
        text = base64.b64encode(content).decode()

    return {
        "attachment": {
            "type": "file",
            "name": file.filename,
            "content": text,
            "mime_type": mime,
        }
    }
