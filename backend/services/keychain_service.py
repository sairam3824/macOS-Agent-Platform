"""Secure API key storage using macOS Keychain via keyring."""
import keyring
from backend.utils.logger import get_logger

logger = get_logger(__name__)

SERVICE_NAME = "macos-agent-platform"


def save_api_key(provider: str, api_key: str) -> bool:
    try:
        keyring.set_password(SERVICE_NAME, provider, api_key)
        logger.info(f"Saved API key for {provider} to Keychain")
        return True
    except Exception as e:
        logger.error(f"Failed to save API key for {provider}: {e}")
        return False


def get_api_key(provider: str) -> str | None:
    try:
        return keyring.get_password(SERVICE_NAME, provider)
    except Exception as e:
        logger.error(f"Failed to retrieve API key for {provider}: {e}")
        return None


def delete_api_key(provider: str) -> bool:
    try:
        keyring.delete_password(SERVICE_NAME, provider)
        return True
    except Exception as e:
        logger.warning(f"Failed to delete API key for {provider}: {e}")
        return False


def mask_key(key: str) -> str:
    if not key or len(key) < 8:
        return "***"
    return key[:4] + "..." + key[-4:]
