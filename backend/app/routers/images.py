from fastapi import APIRouter

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/")
def list_images():
    return {"status": "ok", "router": "images"}
