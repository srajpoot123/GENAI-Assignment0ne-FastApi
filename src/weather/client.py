from __future__ import annotations

import httpx
from fastapi import HTTPException, status

from src.config import settings


async def get_weather_by_city(city: str) -> dict:
    if not city or not city.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="City is required")

    url = f"{settings.openweather_base_url}/weather"
    params = {
        "q": city.strip(),
        "appid": settings.openweather_api_key,
        "units": "metric",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Weather upstream request failed") from exc

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR or not response.is_success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Weather service unavailable")

    data = response.json()
    if "main" not in data or "weather" not in data:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Weather data format unexpected")

    return {
        "city": data.get("name", city.strip()),
        "temperature": data["main"].get("temp", 0.0),
        "condition": data["weather"][0].get("main", "Unknown"),
        "humidity": data["main"].get("humidity", 0),
    }
