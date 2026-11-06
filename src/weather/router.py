from fastapi import APIRouter, Query, status

from src.weather.client import get_weather_by_city
from src.weather.schema import WeatherResponse

router = APIRouter(prefix="", tags=["weather"])


@router.get("/weather", response_model=WeatherResponse, status_code=status.HTTP_200_OK)
async def weather_endpoint(city: str = Query(..., description="City name for weather lookup")):
    return await get_weather_by_city(city)
