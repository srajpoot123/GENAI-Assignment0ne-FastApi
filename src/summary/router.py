from fastapi import APIRouter, Depends, status

from src.auth.dependencies import require_api_key
from src.summary.client import generate_summary
from src.summary.schema import SummaryRequest, SummaryResponse

router = APIRouter(prefix="", tags=["summary"])


@router.post("/summary", response_model=SummaryResponse, status_code=status.HTTP_200_OK)
async def summary_endpoint(
    payload: SummaryRequest,
    _: str = Depends(require_api_key),
):
    return {"summary": generate_summary(payload.text)}
