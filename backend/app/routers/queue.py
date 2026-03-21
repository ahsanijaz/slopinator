import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.image import Image, ImageStatus
from app.models.video import Video, VideoStatus
from app.services.queue_service import process_queue

router = APIRouter(prefix="/queue", tags=["queue"])


@router.get("/")
def get_queue_status(db: Session = Depends(get_db)):
    counts = {
        "pending": db.query(Image).filter(Image.status == ImageStatus.pending).count(),
        "processing": db.query(Image).filter(Image.status == ImageStatus.processing).count(),
        "done": db.query(Image).filter(Image.status == ImageStatus.done).count(),
        "failed": db.query(Image).filter(Image.status == ImageStatus.failed).count(),
    }
    recent_videos = (
        db.query(Video)
        .order_by(Video.created_at.desc())
        .limit(10)
        .all()
    )
    return {
        "counts": counts,
        "recent_videos": [
            {
                "id": v.id,
                "image_id": v.image_id,
                "status": v.status.value,
                "prompt_used": v.prompt_used,
                "created_at": v.created_at.isoformat(),
            }
            for v in recent_videos
        ],
    }


@router.post("/process")
async def trigger_queue(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger queue processing."""
    background_tasks.add_task(process_queue, db)
    return {"status": "queued", "message": "Queue processing started in background."}
