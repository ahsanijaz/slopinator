from fastapi import APIRouter

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("/")
def list_themes():
    return {"status": "ok", "router": "themes"}
