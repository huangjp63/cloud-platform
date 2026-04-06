from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.response import APIResponse
from app.services import recycle_service
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter()

def recycle_item_to_dict(item):
    """将RecycleItem对象转换为可序列化的字典"""
    return {
        "id": item.id,
        "item_type": item.item_type,
        "item_id": item.item_id,
        "name": item.name,
        "size": item.size,
        "user_id": item.user_id,
        "original_path": item.original_path,
        "delete_time": item.delete_time.strftime("%Y-%m-%d %H:%M:%S") if item.delete_time else None
    }


@router.get("/list", response_model=APIResponse)
def get_recycle_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        items = recycle_service.get_all_recycle_items(db)
    else:
        items = recycle_service.get_user_recycle_items(db, current_user.id)
    
    # 将RecycleItem对象转换为可序列化的字典列表
    items_dict = [recycle_item_to_dict(item) for item in items]
    
    return APIResponse(code=200, message="获取成功", data=items_dict)


@router.put("/recover/{item_id}", response_model=APIResponse)
def recover_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        if not recycle_service.check_item_owner(db, item_id, current_user.id):
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="无权恢复此项目")
    
    recycle_service.recover_item(db, item_id)
    return APIResponse(code=200, message="恢复成功", data=None)


@router.delete("/delete/{item_id}", response_model=APIResponse)
def delete_permanently(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        if not recycle_service.check_item_owner(db, item_id, current_user.id):
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="无权删除此项目")
    
    recycle_service.delete_permanently(db, item_id)
    return APIResponse(code=200, message="已彻底删除", data=None)


@router.post("/clean", response_model=APIResponse)
def clean_expired(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    count = recycle_service.clean_expired_items(db)
    return APIResponse(code=200, message=f"已清理 {count} 个过期项目", data={"count": count})

@router.get("/folder/{folder_id}", response_model=APIResponse)
def get_folder_contents(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = recycle_service.get_folder_contents(db, folder_id, current_user.id, current_user.role)
    if result:
        return APIResponse(code=200, message="获取成功", data=result)
    else:
        return APIResponse(code=404, message="文件夹不存在或无权访问", data=None)
