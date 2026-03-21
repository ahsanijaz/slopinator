from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum

from app.database import Base


class ImageStatus(str, PyEnum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    status = Column(SAEnum(ImageStatus), default=ImageStatus.pending, nullable=False)
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
