"""Voice endpoints: upload audio → transcribe → optionally run through agent."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.voice_service import transcribe_audio, is_transcription_available
from backend.agent.orchestrator import process_chat
from backend.models.agent import ChatRequest

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/status")
async def voice_status():
    from backend.services.voice_service import is_local_whisper_available
    from backend.config import settings
    return {
        "available": is_transcription_available(),
        "local_whisper": is_local_whisper_available(),
        "openai_fallback": bool(settings.openai_api_key),
    }


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Upload a WAV/MP3/M4A/WebM file, get back the transcribed text."""
    if not is_transcription_available():
        raise HTTPException(
            status_code=503,
            detail="No transcription engine available. Install openai-whisper or add an OpenAI API key.",
        )
    audio_bytes = await file.read()
    text = await transcribe_audio(audio_bytes, filename=file.filename or "audio.wav")
    return {"text": text}


@router.post("/transcribe-and-chat")
async def transcribe_and_chat(
    file: UploadFile = File(...),
    session_id: str = "voice",
    model: str | None = None,
):
    """Upload audio → transcribe → send to agent → return full response."""
    if not is_transcription_available():
        raise HTTPException(status_code=503, detail="No transcription engine available.")

    audio_bytes = await file.read()
    text = await transcribe_audio(audio_bytes, filename=file.filename or "audio.wav")

    if not text or text.startswith("["):
        return {"transcription": text, "response": None}

    request = ChatRequest(
        message=text,
        session_id=session_id,
        model=model,
        allow_actions=True,
    )
    response = await process_chat(request)
    return {"transcription": text, "response": response}
