from pydantic import BaseModel, Field


class JokeResponse(BaseModel):
    joke: str = Field(..., description="Random joke text")
    category: str = Field(..., description="Joke category")
