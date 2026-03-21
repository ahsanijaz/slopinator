from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # e.g. "A cinematic video of {subject} with a {theme} aesthetic"
    template_str = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
