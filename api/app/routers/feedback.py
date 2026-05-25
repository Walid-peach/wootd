from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.storage import insert_feedback

router = APIRouter()


class FeedbackIn(BaseModel):
    recommendation_id: str
    rating: int = Field(..., ge=-1, le=1, description="-1 bad, 0 okay, 1 good")
    notes: str = ""


@router.post("/feedback", status_code=204)
def post_feedback(body: FeedbackIn) -> None:
    insert_feedback(
        recommendation_id=body.recommendation_id,
        rating=body.rating,
        notes=body.notes,
    )
