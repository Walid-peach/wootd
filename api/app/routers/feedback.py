from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter()


class FeedbackIn(BaseModel):
    recommendation_id: str
    rating: int = Field(..., ge=-1, le=1, description="-1 bad, 0 okay, 1 good")
    notes: str = ""


@router.post("/feedback", status_code=204)
def post_feedback(body: FeedbackIn) -> None:
    from supabase import create_client

    sb = create_client(settings.supabase_url, settings.supabase_service_role_key)  # type: ignore[attr-defined]
    sb.table("feedback").insert({
        "recommendation_id": body.recommendation_id,
        "rating": body.rating,
        "notes": body.notes,
    }).execute()
