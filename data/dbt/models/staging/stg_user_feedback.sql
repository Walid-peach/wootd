select
    feedback_id,
    recommendation_id,
    rating,
    notes,
    created_at
from {{ source('raw', 'USER_FEEDBACK') }}
