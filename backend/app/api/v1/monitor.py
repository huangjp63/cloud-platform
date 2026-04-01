from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.response import APIResponse
from app.services import monitor_service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/resource", response_model=APIResponse)
def get_resource_monitor(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = monitor_service.get_resource_monitor(current_user.role)
    return APIResponse(code=200, message="获取成功", data=data)


@router.get("/service", response_model=APIResponse)
def get_service_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = monitor_service.get_service_status(current_user.role)
    return APIResponse(code=200, message="获取成功", data=data)
