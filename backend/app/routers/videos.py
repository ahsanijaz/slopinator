from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.video import Video

router = APIRouter(prefix="/videos", tags=["videos"])


def _serialize(v: Video) -> dict:
    return {
        "id": v.id,
        "image_id": v.image_id,
        "prompt_used": v.prompt_used,
        "video_path": v.video_path,
        "caption": v.caption,
        "hashtags": v.hashtags,
        "status": v.status.value,
        "created_at": v.created_at.isoformat(),
    }


@router.get("/")
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).order_by(Video.created_at.desc()).all()
    return [_serialize(v) for v in videos]


@router.get("/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    return _serialize(video)
