import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routers import images, queue, templates, themes, videos
from app.routers import tiktok
from app.routers import admin

logger = logging.getLogger(__name__)

app = FastAPI(title="Slopinator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(themes.router, prefix="/api")
app.include_router(queue.router, prefix="/api")
app.include_router(videos.router, prefix="/api")
app.include_router(tiktok.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


import os
os.makedirs("generated_videos", exist_ok=True)
os.makedirs("uploads", exist_ok=True)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def start_scheduler():
    """Launch the background scheduling loop."""
    asyncio.create_task(_scheduler_loop())


async def _scheduler_loop():
    """Background loop: every 60 seconds, schedule ready videos and post due ones."""
    from app.services.scheduler_service import post_due_videos, schedule_ready_videos

    while True:
        await asyncio.sleep(60)
        db = SessionLocal()
        try:
            created = schedule_ready_videos(db)
            if created:
                logger.info("Scheduler: scheduled %d new post(s).", len(created))
            await post_due_videos(db)
        except Exception as exc:
            logger.error("Scheduler loop error: %s", exc, exc_info=True)
        finally:
            db.close()


@app.get("/")
def root():
    return {"status": "ok", "app": "slopinator"}
