from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Literal
import os


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    open_browser_on_start: bool = True

    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "gemma3:4b"

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    model_routing: Literal["local_first", "cloud_first", "local_only"] = "local_first"

    require_confirmation_for_actions: bool = True
    dry_run_mode: bool = False
    safe_mode: bool = False

    db_path: str = "./data/agent.db"
    log_path: str = "./data/logs"

    secret_key: str = "dev-secret-key"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_data_dirs(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.log_path).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_data_dirs()
