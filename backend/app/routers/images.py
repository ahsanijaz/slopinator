import os
import uuid
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.image import Image, ImageStatus

router = APIRouter(prefix="/images", tags=["images"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/")
def list_images(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Image)
    if status:
        query = query.filter(Image.status == status)
    images = query.order_by(Image.uploaded_at.desc()).all()
    return [
        {
            "id": img.id,
            "filename": img.filename,
            "original_path": img.original_path,
            "status": img.status.value,
            "theme_id": img.theme_id,
            "template_id": img.template_id,
            "uploaded_at": img.uploaded_at.isoformat(),
        }
        for img in images
    ]


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    theme_id: Optional[int] = Form(None),
    template_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)

    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    image = Image(
        filename=file.filename,
        original_path=save_path,
        status=ImageStatus.pending,
        theme_id=theme_id,
        template_id=template_id,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    return {
        "id": image.id,
        "filename": image.filename,
        "status": image.status.value,
        "uploaded_at": image.uploaded_at.isoformat(),
    }


@router.delete("/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")
    if os.path.exists(image.original_path):
        os.remove(image.original_path)
    db.delete(image)
    db.commit()
    return {"status": "deleted", "id": image_id}
