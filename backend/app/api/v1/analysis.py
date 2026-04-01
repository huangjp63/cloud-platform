from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.response import APIResponse
from app.services import analysis_service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/file", response_model=APIResponse)
def get_file_statistics(
    type: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = analysis_service.get_file_statistics(db, current_user.id, current_user.role, type)
    return APIResponse(code=200, message="获取成功", data=data)


@router.get("/behavior", response_model=APIResponse)
def get_behavior_statistics(
    type: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = analysis_service.get_behavior_statistics(db, current_user.id, current_user.role, type)
    return APIResponse(code=200, message="获取成功", data=data)


@router.get("/hot", response_model=APIResponse)
def get_hot_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = analysis_service.get_hot_files(db, current_user.id, current_user.role)
    return APIResponse(code=200, message="获取成功", data=data)


@router.get("/card", response_model=APIResponse)
def get_stat_card(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = analysis_service.get_stat_card(db, current_user.id, current_user.role)
    return APIResponse(code=200, message="获取成功", data=data)
