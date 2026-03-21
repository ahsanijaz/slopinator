from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import images, queue, templates, themes, videos

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


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok", "app": "slopinator"}
