from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from urllib.parse import quote
from app.database import get_db
from app.schemas.response import APIResponse
from app.services import file_service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/check/md5", response_model=APIResponse)
def check_md5(
    md5: str,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exist = file_service.check_file_md5(db, md5)
    return APIResponse(
        code=200,
        message="校验完成",
        data={"exist": exist, "md5": md5}
    )


def file_to_dict(file):
    """将 File 对象转换为字典"""
    return {
        "id": file.id,
        "name": file.name,
        "size": file.size,
        "file_type": file.file_type,
        "create_time": file.create_time.isoformat() if file.create_time else None,
        "update_time": file.update_time.isoformat() if file.update_time else None
    }


@router.post("/upload/single", response_model=APIResponse)
async def upload_single(
    file: UploadFile = File(...),
    parent_id: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_info = await file_service.upload_single_file(db, file, parent_id, current_user.id)
    return APIResponse(code=200, message="上传成功", data=file_to_dict(file_info))


@router.get("/upload/chunk", response_model=APIResponse)
def get_uploaded_chunks(
    md5: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chunks = file_service.get_uploaded_chunks(db, md5, current_user.id)
    return APIResponse(code=200, message="获取成功", data={"chunks": chunks})


@router.post("/upload/chunk", response_model=APIResponse)
async def upload_chunk(
    md5: str = Query(...),
    index: int = Query(...),
    total: int = Query(...),
    chunk: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await file_service.upload_chunk_file(db, md5, index, total, chunk, current_user.id)
    return APIResponse(code=200, message=f"分片 {index}/{total} 上传成功", data=None)


@router.post("/upload/merge", response_model=APIResponse)
def merge_chunks(
    md5: str,
    filename: str,
    total: int,
    parent_id: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_info = file_service.merge_chunks(db, md5, filename, total, parent_id, current_user.id)
    return APIResponse(code=200, message="合并成功", data=file_to_dict(file_info))


@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        if not file_service.check_file_owner(db, file_id, current_user.id):
            raise HTTPException(status_code=403, detail="无权下载此文件")
    
    result = file_service.download_file(db, file_id)
    if not result:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file = result["file"]
    file_data = result["data"]
    
    return StreamingResponse(
        file_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(file.name)}"
        }
    )


@router.post("/download/batch")
def download_batch(
    file_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    zip_buffer = file_service.download_batch_files(db, file_ids, current_user.id, current_user.role)
    if not zip_buffer:
        raise HTTPException(status_code=404, detail="没有找到可下载的文件")
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=files.zip"
        }
    )


@router.delete("/delete/{file_id}", response_model=APIResponse)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        if not file_service.check_file_owner(db, file_id, current_user.id):
            raise HTTPException(status_code=403, detail="无权删除此文件")
    
    file_service.delete_file(db, file_id, current_user.id)
    return APIResponse(code=200, message="删除成功，已移入回收站", data=None)


@router.put("/rename/{file_id}", response_model=APIResponse)
def rename_file(
    file_id: int,
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        if not file_service.check_file_owner(db, file_id, current_user.id):
            raise HTTPException(status_code=403, detail="无权重命名此文件")
    
    file = file_service.rename_file(db, file_id, name, current_user.id)
    return APIResponse(code=200, message="重命名成功", data={"id": file.id, "name": file.name})


@router.get("/preview/{file_id}")
def preview_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        if not file_service.check_file_owner(db, file_id, current_user.id):
            raise HTTPException(status_code=403, detail="无权预览此文件")
    
    return file_service.preview_file(db, file_id)


@router.get("/list", response_model=APIResponse)
def get_file_list(
    parent_id: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    files = file_service.get_file_list(db, current_user.id, parent_id, current_user.role)
    return APIResponse(code=200, message="获取成功", data=[file_to_dict(file) for file in files])
