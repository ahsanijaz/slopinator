from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.template import PromptTemplate

router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateCreate(BaseModel):
    name: str
    template_str: str


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_str: Optional[str] = None


def _serialize(t: PromptTemplate):
    return {
        "id": t.id,
        "name": t.name,
        "template_str": t.template_str,
        "created_at": t.created_at.isoformat(),
    }


@router.get("/")
def list_templates(db: Session = Depends(get_db)):
    return [_serialize(t) for t in db.query(PromptTemplate).order_by(PromptTemplate.name).all()]


@router.post("/")
def create_template(body: TemplateCreate, db: Session = Depends(get_db)):
    template = PromptTemplate(name=body.name, template_str=body.template_str)
    db.add(template)
    db.commit()
    db.refresh(template)
    return _serialize(template)


@router.put("/{template_id}")
def update_template(template_id: int, body: TemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found.")
    if body.name is not None:
        template.name = body.name
    if body.template_str is not None:
        template.template_str = body.template_str
    db.commit()
    db.refresh(template)
    return _serialize(template)


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found.")
    db.delete(template)
    db.commit()
    return {"status": "deleted", "id": template_id}
