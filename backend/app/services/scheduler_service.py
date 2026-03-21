"""Scheduler service: smart queue spreading for TikTok video posts."""

import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.post import Post, PostStatus
from app.models.video import Video, VideoStatus

logger = logging.getLogger(__name__)


def schedule_ready_videos(db: Session, posts_per_day: int = 2) -> list[Post]:
    """Find all ready videos without a scheduled post and spread them evenly.

    The algorithm:
    - Queries all videos with status=ready that have no associated Post record.
    - Determines the next available posting slot by looking at the last scheduled post.
    - Spreads new posts at even intervals (24h / posts_per_day apart).
    - Creates and persists Post records with scheduled_at timestamps.

    Args:
        db: SQLAlchemy database session.
        posts_per_day: Maximum number of posts per day (controls spacing interval).

    Returns:
        List of newly created Post records.
    """
    # Find all ready videos that have no post record at all
    scheduled_video_ids = db.query(Post.video_id).distinct().subquery()
    unscheduled_videos = (
        db.query(Video)
        .filter(
            Video.status.in_([VideoStatus.ready, VideoStatus.approved]),
            ~Video.id.in_(scheduled_video_ids),
        )
        .order_by(Video.created_at.asc())
        .all()
    )

    if not unscheduled_videos:
        logger.debug("No ready, unscheduled videos found.")
        return []

    # Determine the interval between posts
    interval = timedelta(hours=24 / posts_per_day)

    # Find the most recently scheduled post to anchor the next slot
    last_post = (
        db.query(Post)
        .filter(Post.scheduled_at.isnot(None))
        .order_by(Post.scheduled_at.desc())
        .first()
    )

    if last_post and last_post.scheduled_at > datetime.utcnow():
        # There are future-scheduled posts; slot after the last one
        next_slot = last_post.scheduled_at + interval
    else:
        # No future posts; start from now (or slightly in the future for safety)
        next_slot = datetime.utcnow() + timedelta(minutes=1)

    created_posts: list[Post] = []
    for video in unscheduled_videos:
        post = Post(
            video_id=video.id,
            scheduled_at=next_slot,
            status=PostStatus.queued,
        )
        db.add(post)
        created_posts.append(post)
        logger.info(
            "Scheduled video %d for posting at %s", video.id, next_slot.isoformat()
        )
        next_slot += interval

    db.commit()
    for post in created_posts:
        db.refresh(post)

    return created_posts


async def post_due_videos(db: Session) -> None:
    """Find all queued posts whose scheduled_at has passed and post them to TikTok.

    This function is intended to be called periodically by the background task loop
    in main.py. It imports tiktok_service lazily to avoid circular imports.

    Args:
        db: SQLAlchemy database session.
    """
    from app.services import tiktok_service  # lazy import to avoid circular deps

    now = datetime.utcnow()
    due_posts = (
        db.query(Post)
        .filter(
            Post.status == PostStatus.queued,
            Post.scheduled_at <= now,
            Post.scheduled_at.isnot(None),
        )
        .all()
    )

    for post in due_posts:
        video = db.query(Video).filter(Video.id == post.video_id).first()
        if not video or not video.video_path:
            logger.warning(
                "Post %d skipped: video %s has no file path.", post.id, post.video_id
            )
            post.status = PostStatus.failed
            db.commit()
            continue

        hashtags = (
            [h.strip() for h in post.hashtags.split(",") if h.strip()]
            if post.hashtags
            else []
        )
        caption = post.caption or ""

        try:
            publish_id = await tiktok_service.post_video(
                video_path=video.video_path,
                caption=caption,
                hashtags=hashtags,
            )
            post.status = PostStatus.posted
            post.posted_at = datetime.utcnow()
            logger.info(
                "Posted video %d to TikTok, publish_id=%s", video.id, publish_id
            )
        except Exception as exc:
            post.status = PostStatus.failed
            logger.error(
                "Failed to post video %d: %s", video.id, exc, exc_info=True
            )

        db.commit()
