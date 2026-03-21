from fastapi import APIRouter

router = APIRouter(prefix="/queue", tags=["queue"])


@router.get("/")
def get_queue():
    return {"status": "ok", "router": "queue"}
