"""
Voice transcription service.
Priority: local Whisper → OpenAI Whisper API → error.
"""
import io
import tempfile
import os
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_whisper_model = None


def _load_local_whisper(model_size: str = "base"):
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    try:
        import whisper
        logger.info(f"Loading local Whisper model: {model_size}")
        _whisper_model = whisper.load_model(model_size)
        return _whisper_model
    except ImportError:
        return None


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """
    Transcribe audio bytes to text.
    Tries local Whisper first, then OpenAI Whisper API if configured.
    """
    # Write to a temp file (Whisper needs a file path)
    suffix = os.path.splitext(filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        # 1. Try local Whisper
        model = _load_local_whisper("base")
        if model is not None:
            import asyncio
            loop = asyncio.get_event_loop()
            # Run blocking Whisper inference in a thread pool
            result = await loop.run_in_executor(
                None,
                lambda: model.transcribe(tmp_path, language="en", fp16=False),
            )
            text = result.get("text", "").strip()
            logger.info(f"Local Whisper transcribed: {text[:80]}")
            return text

        # 2. Try OpenAI Whisper API
        if settings.openai_api_key:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            with open(tmp_path, "rb") as f:
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="en",
                )
            text = response.text.strip()
            logger.info(f"OpenAI Whisper transcribed: {text[:80]}")
            return text

        return "[Voice transcription unavailable. Install openai-whisper: pip install -r requirements-voice.txt]"

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return f"[Transcription error: {e}]"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def is_local_whisper_available() -> bool:
    try:
        import whisper  # noqa
        return True
    except ImportError:
        return False


def is_transcription_available() -> bool:
    return is_local_whisper_available() or bool(settings.openai_api_key)
