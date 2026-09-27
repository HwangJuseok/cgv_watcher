from pydantic import BaseModel
from typing import Optional

class TargetRequest(BaseModel):
    user_id: str
    movie_code: str
    theater_code: str
    target_date: str
    screen_type: str
    telegram_id: Optional[str] = ""