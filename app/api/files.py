import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.crud import get_task
from app.db.models import User
from app.auth.dependencies import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/files", tags=["Files"])
settings = get_settings()


@router.post("/upload/{task_id}", status_code=status.HTTP_201_CREATED)
async def upload_file(
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file to a task's workspace."""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    upload_dir = Path(settings.workspace_dir) / f"uploads" / f"task_{task_id}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_name = Path(file.filename).name
    file_path = upload_dir / safe_name

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": safe_name,
        "size_bytes": len(content),
        "path": str(file_path),
        "task_id": task_id,
    }


@router.get("/download/{task_id}/{filename}")
async def download_file(
    task_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download a file from a task's workspace."""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    safe_name = Path(filename).name

    # Check uploads directory first, then task workspace
    for base_dir in [
        Path(settings.workspace_dir) / "uploads" / f"task_{task_id}",
        Path(settings.workspace_dir) / f"task_{task_id}",
    ]:
        file_path = base_dir / safe_name
        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                filename=safe_name,
                media_type="application/octet-stream",
            )

    raise HTTPException(status_code=404, detail="File not found")
