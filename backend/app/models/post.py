from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum

from app.database import Base


class Platform(str, PyEnum):
    tiktok = "tiktok"


class PostStatus(str, PyEnum):
    queued = "queued"
    posted = "posted"
    failed = "failed"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    platform = Column(SAEnum(Platform), default=Platform.tiktok, nullable=False)
    caption = Column(String, nullable=True)
    hashtags = Column(String, nullable=True)  # comma-separated
    scheduled_at = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    status = Column(SAEnum(PostStatus), default=PostStatus.queued, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
