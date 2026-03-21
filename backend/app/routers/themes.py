from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.theme import Theme

router = APIRouter(prefix="/themes", tags=["themes"])


class ThemeCreate(BaseModel):
    name: str
    description: str = ""
    is_default: bool = False


class ThemeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


def _serialize(t: Theme):
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "is_default": t.is_default,
        "created_at": t.created_at.isoformat(),
    }


@router.get("/")
def list_themes(db: Session = Depends(get_db)):
    return [_serialize(t) for t in db.query(Theme).order_by(Theme.name).all()]


@router.post("/")
def create_theme(body: ThemeCreate, db: Session = Depends(get_db)):
    existing = db.query(Theme).filter(Theme.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A theme with that name already exists.")
    theme = Theme(name=body.name, description=body.description, is_default=body.is_default)
    db.add(theme)
    db.commit()
    db.refresh(theme)
    return _serialize(theme)


@router.put("/{theme_id}")
def update_theme(theme_id: int, body: ThemeUpdate, db: Session = Depends(get_db)):
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found.")
    if body.name is not None:
        theme.name = body.name
    if body.description is not None:
        theme.description = body.description
    if body.is_default is not None:
        theme.is_default = body.is_default
    db.commit()
    db.refresh(theme)
    return _serialize(theme)


@router.delete("/{theme_id}")
def delete_theme(theme_id: int, db: Session = Depends(get_db)):
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found.")
    db.delete(theme)
    db.commit()
    return {"status": "deleted", "id": theme_id}
