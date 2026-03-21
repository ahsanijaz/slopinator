from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum

from app.database import Base


class VideoStatus(str, PyEnum):
    pending = "pending"
    generating = "generating"
    ready = "ready"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    failed = "failed"


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    prompt_used = Column(String, nullable=False)
    video_path = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    hashtags = Column(String, nullable=True)  # comma-separated, editable in review
    status = Column(SAEnum(VideoStatus), default=VideoStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
