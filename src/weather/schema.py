from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    city: str = Field(..., description="Name of the city")
    temperature: float = Field(...,
                               description="Current temperature in Celsius")
    condition: str = Field(..., description="Weather condition")
    humidity: int = Field(..., description="Humidity percentage")
