from fastapi import APIRouter, Depends, HTTPException, status
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


@router.get("/file/list", response_model=APIResponse)
def get_file_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    files = admin_service.get_all_files(db)
    return APIResponse(code=200, message="获取成功", data=files)


@router.delete("/user/{user_id}", response_model=APIResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    success = admin_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除失败，用户不存在或为管理员"
        )
    
    return APIResponse(code=200, message="删除成功", data=None)


@router.put("/user/{user_id}/role", response_model=APIResponse)
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色"
        )
    
    success = admin_service.update_user_role(db, user_id, role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="修改失败，用户不存在"
        )
    
    return APIResponse(code=200, message="修改成功", data=None)


@router.delete("/file/{file_id}", response_model=APIResponse)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    success = admin_service.delete_file(db, file_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除失败，文件不存在"
        )
    
    return APIResponse(code=200, message="删除成功", data=None)

