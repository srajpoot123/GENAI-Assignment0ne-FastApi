from fastapi import APIRouter, status

from src.joke.client import get_random_joke
from src.joke.schema import JokeResponse

router = APIRouter(prefix="", tags=["joke"])


@router.get("/joke", response_model=JokeResponse, status_code=status.HTTP_200_OK)
async def joke_endpoint():
    return await get_random_joke()
