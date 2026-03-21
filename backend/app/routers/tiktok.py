"""TikTok router: OAuth flow and manual video posting endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.post import Post
from app.models.video import Video, VideoStatus
from app.services import tiktok_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tiktok", tags=["tiktok"])


@router.get("/auth")
async def get_auth_url():
    """Return the TikTok OAuth authorization URL."""
    auth_url = await tiktok_service.get_auth_url()
    return {"auth_url": auth_url}


@router.get("/callback")
async def oauth_callback(code: str, state: str | None = None):
    """Handle the TikTok OAuth callback.

    TikTok redirects here with ?code=... after the user authorizes.
    The tokens are logged for now; in production they should be persisted.
    """
    try:
        token_data = await tiktok_service.exchange_code(code)
        logger.info(
            "TikTok OAuth successful — open_id=%s access_token=%s...",
            token_data["open_id"],
            token_data["access_token"][:8],
        )
        return {
            "status": "ok",
            "open_id": token_data["open_id"],
            "message": "Token received and logged. Persist it to use for posting.",
        }
    except Exception as exc:
        logger.error("TikTok OAuth callback failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/post/{video_id}")
async def post_video(video_id: int, db: Session = Depends(get_db)):
    """Manually trigger posting a specific video to TikTok."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    if video.status != VideoStatus.ready:
        raise HTTPException(
            status_code=400,
            detail=f"Video is not ready for posting (status={video.status.value}).",
        )
    if not video.video_path:
        raise HTTPException(status_code=400, detail="Video has no file path.")

    # Look up the most recent Post record for this video to get caption/hashtags
    post_record = (
        db.query(Post)
        .filter(Post.video_id == video_id)
        .order_by(Post.created_at.desc())
        .first()
    )
    caption = post_record.caption if post_record and post_record.caption else ""
    hashtags = (
        [h.strip() for h in post_record.hashtags.split(",") if h.strip()]
        if post_record and post_record.hashtags
        else []
    )

    try:
        publish_id = await tiktok_service.post_video(
            video_path=video.video_path,
            caption=caption,
            hashtags=hashtags,
        )
    except Exception as exc:
        logger.error("Failed to post video %d: %s", video_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

    return {"status": "posted", "publish_id": publish_id, "video_id": video_id}


@router.get("/posts")
def list_posts(db: Session = Depends(get_db)):
    """List all Post records."""
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "video_id": p.video_id,
            "platform": p.platform.value,
            "caption": p.caption,
            "hashtags": p.hashtags,
            "scheduled_at": p.scheduled_at.isoformat() if p.scheduled_at else None,
            "posted_at": p.posted_at.isoformat() if p.posted_at else None,
            "status": p.status.value,
            "created_at": p.created_at.isoformat(),
        }
        for p in posts
    ]
