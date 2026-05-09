"""
macOS Agent Platform — FastAPI backend entry point.
Start with: uvicorn backend.main:app --reload
"""
import asyncio
import webbrowser
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.config import settings
from backend.database import init_db
from backend.routes import agent, actions, settings as settings_router, logs, system, voice
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info(f"Backend starting on http://{settings.host}:{settings.port}")

    if settings.open_browser_on_start:
        # Short delay so the server is ready before browser opens
        async def open_browser():
            await asyncio.sleep(1.5)
            webbrowser.open(f"http://{settings.host}:{settings.port}")

        asyncio.create_task(open_browser())

    yield

    from backend.services.ollama_service import ollama_service
    await ollama_service.close()
    logger.info("Backend shut down cleanly.")


app = FastAPI(
    title="macOS Agent Platform",
    description="Local-first macOS desktop agent with Ollama + optional cloud LLMs",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(agent.router, prefix="/api")
app.include_router(actions.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(system.router, prefix="/api")
app.include_router(voice.router, prefix="/api")

# Serve the built frontend if it exists
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        index = frontend_dist / "index.html"
        return FileResponse(str(index))
else:
    @app.get("/")
    async def root():
        return {
            "message": "macOS Agent Platform API",
            "docs": f"http://{settings.host}:{settings.port}/docs",
            "status": "Frontend not built yet. Run: cd frontend && npm run build",
        }
