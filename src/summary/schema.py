from pydantic import BaseModel, Field, ConfigDict


class SummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(..., min_length=1,
                      description="Text that must be summarized")


class SummaryResponse(BaseModel):
    summary: str = Field(..., description="Generated summary")
