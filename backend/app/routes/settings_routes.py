"""Settings API routes."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.models.schemas import UserSettings
from backend.app.services.watchlist_service import SettingsService

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=UserSettings)
def get_settings() -> UserSettings:
    """Get saved user settings."""
    return SettingsService().get_settings()


@router.post("", response_model=UserSettings)
def save_settings(settings: UserSettings) -> UserSettings:
    """Save user settings."""
    return SettingsService().save_settings(settings)

