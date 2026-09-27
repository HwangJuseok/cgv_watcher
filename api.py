from fastapi import APIRouter
from models import TargetRequest
import database

router = APIRouter()

@router.get("/targets")
async def get_targets():
    """크롤러 확인용 전체 감시 조건 목록"""
    targets = database.get_all_target_conditions()
    return {"status": "success", "data": targets}

@router.get("/targets/{user_id}")
async def get_user_targets(user_id: str):
    """아이폰에서 내 감시 조건 목록을 요청할 때 사용"""
    targets = database.get_user_subscriptions(user_id)
    return {"status": "success", "data": targets}

@router.post("/targets")
async def add_target(target: TargetRequest):
    """아이폰에서 새로운 감시 조건을 등록할 때 사용"""
    database.add_subscription(
        target.user_id, 
        "ios", 
        target.movie_code, 
        target.theater_code, 
        target.target_date, 
        target.screen_type,
        target.telegram_id or ""
    )
    return {"status": "success", "message": "아이폰 감시 조건이 추가되었습니다."}

@router.delete("/targets")
async def delete_target(target: TargetRequest):
    """아이폰에서 스와이프하여 감시 조건을 삭제할 때 사용"""
    database.delete_subscription(
        target.user_id, 
        target.movie_code, 
        target.theater_code, 
        target.target_date, 
        target.screen_type
    )
    return {"status": "success", "message": "해당 감시 조건이 삭제되었습니다."}