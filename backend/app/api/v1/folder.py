from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.response import APIResponse
from app.services import folder_service
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter()


@router.post("/create", response_model=APIResponse)
def create_folder(
    name: str,
    parent_id: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    folder = folder_service.create_folder(db, name, parent_id, current_user.id)
    return APIResponse(code=200, message="创建成功", data={"id": folder.id, "name": folder.name})


@router.delete("/delete/{folder_id}", response_model=APIResponse)
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        if not folder_service.check_folder_owner(db, folder_id, current_user.id):
            raise HTTPException(status_code=403, detail="无权删除此文件夹")
    
    folder_service.delete_folder(db, folder_id, current_user.id)
    return APIResponse(code=200, message="删除成功，已移入回收站", data=None)


@router.put("/rename/{folder_id}", response_model=APIResponse)
def rename_folder(
    folder_id: int,
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        if not folder_service.check_folder_owner(db, folder_id, current_user.id):
            raise HTTPException(status_code=403, detail="无权重命名此文件夹")
    
    folder = folder_service.rename_folder(db, folder_id, name)
    return APIResponse(code=200, message="重命名成功", data={"id": folder.id, "name": folder.name})


@router.get("/list", response_model=APIResponse)
def get_folder_list(
    parent_id: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    folders = folder_service.get_folder_list(db, current_user.id, parent_id, current_user.role)
    return APIResponse(code=200, message="获取成功", data=[{"id": folder.id, "name": folder.name, "create_time": folder.create_time.isoformat() if folder.create_time else None} for folder in folders])
