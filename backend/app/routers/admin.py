import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.image import Image
from app.models.setting import Setting
from app.models.video import Video, VideoStatus

router = APIRouter(prefix="/admin", tags=["admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _create_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expire}, settings.SECRET_KEY, algorithm=ALGORITHM)


def _verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> bool:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    try:
        jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(body: LoginRequest):
    if body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password.")
    token = _create_token({"sub": "admin"})
    return {"access_token": token, "token_type": "bearer"}


# ── Settings ──────────────────────────────────────────────────────────────────

@router.get("/settings")
def get_settings(db: Session = Depends(get_db), _=Depends(_verify_token)):
    mode = db.query(Setting).filter(Setting.key == "pipeline_mode").first()
    return {"pipeline_mode": mode.value if mode else "auto"}


class SettingsUpdate(BaseModel):
    pipeline_mode: str  # "auto" or "review"


@router.put("/settings")
def update_settings(body: SettingsUpdate, db: Session = Depends(get_db), _=Depends(_verify_token)):
    if body.pipeline_mode not in ("auto", "review"):
        raise HTTPException(status_code=400, detail="pipeline_mode must be 'auto' or 'review'.")
    setting = db.query(Setting).filter(Setting.key == "pipeline_mode").first()
    if setting:
        setting.value = body.pipeline_mode
    else:
        db.add(Setting(key="pipeline_mode", value=body.pipeline_mode))
    db.commit()
    return {"pipeline_mode": body.pipeline_mode}


# ── Review queue ──────────────────────────────────────────────────────────────

@router.get("/review-queue")
def get_review_queue(db: Session = Depends(get_db), _=Depends(_verify_token)):
    videos = (
        db.query(Video)
        .filter(Video.status == VideoStatus.pending_review)
        .order_by(Video.created_at.asc())
        .all()
    )
    return [_serialize_video(v, db) for v in videos]


@router.get("/rejected")
def get_rejected(db: Session = Depends(get_db), _=Depends(_verify_token)):
    videos = (
        db.query(Video)
        .filter(Video.status == VideoStatus.rejected)
        .order_by(Video.created_at.desc())
        .all()
    )
    return [_serialize_video(v, db) for v in videos]


class ReviewUpdate(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[str] = None  # comma-separated


@router.post("/approve/{video_id}")
def approve_video(video_id: int, body: ReviewUpdate, db: Session = Depends(get_db), _=Depends(_verify_token)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    if video.status not in (VideoStatus.pending_review, VideoStatus.rejected):
        raise HTTPException(status_code=400, detail="Video is not in review queue.")
    if body.caption is not None:
        video.caption = body.caption
    if body.hashtags is not None:
        video.hashtags = body.hashtags
    video.status = VideoStatus.approved
    db.commit()
    return {"status": "approved", "id": video_id}


@router.post("/reject/{video_id}")
def reject_video(video_id: int, db: Session = Depends(get_db), _=Depends(_verify_token)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    video.status = VideoStatus.rejected
    db.commit()
    return {"status": "rejected", "id": video_id}


@router.delete("/videos/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db), _=Depends(_verify_token)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    if video.video_path and os.path.exists(video.video_path):
        os.remove(video.video_path)
    db.delete(video)
    db.commit()
    return {"status": "deleted", "id": video_id}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serialize_video(v: Video, db: Session) -> dict:
    image = db.query(Image).filter(Image.id == v.image_id).first()
    return {
        "id": v.id,
        "image_id": v.image_id,
        "image_path": image.original_path if image else None,
        "image_filename": image.filename if image else None,
        "prompt_used": v.prompt_used,
        "video_path": v.video_path,
        "caption": v.caption,
        "hashtags": v.hashtags,
        "status": v.status.value,
        "created_at": v.created_at.isoformat(),
    }
