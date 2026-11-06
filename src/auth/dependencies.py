from __future__ import annotations

import os

from fastapi import Header, HTTPException, status

from src.config import settings


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    expected_key = (settings.app_api_key or os.getenv(
        "APP_API_KEY") or "").strip()

    if not x_api_key or x_api_key != expected_key or not expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key
