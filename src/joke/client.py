from __future__ import annotations

import httpx
from fastapi import HTTPException, status

from src.config import settings


async def get_random_joke() -> dict:
    url = f"{settings.joke_api_base_url}/joke/Any?type=single"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Joke upstream request failed") from exc

    if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR or not response.is_success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Joke service unavailable")

    data = response.json()
    if data.get("error"):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="No joke returned by upstream service")

    return {
        "joke": data.get("joke", "No joke available"),
        "category": data.get("category", "unknown"),
    }
