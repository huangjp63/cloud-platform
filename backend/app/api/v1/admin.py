from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.response import APIResponse
from app.services import admin_service
from app.dependencies import get_current_admin
from app.models.user import User

router = APIRouter()


@router.get("/user/list", response_model=APIResponse)
def get_user_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    users = admin_service.get_all_users(db)
    return APIResponse(code=200, message="获取成功", data=users)


@router.get("/analysis/total", response_model=APIResponse)
def get_total_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    data = admin_service.get_total_statistics(db)
    return APIResponse(code=200, message="获取成功", data=data)
