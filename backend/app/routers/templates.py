from fastapi import APIRouter

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/")
def list_templates():
    return {"status": "ok", "router": "templates"}
