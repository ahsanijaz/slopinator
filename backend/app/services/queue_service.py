import asyncio
import logging

from sqlalchemy.orm import Session

from app.models.image import Image, ImageStatus
from app.models.video import Video, VideoStatus

logger = logging.getLogger(__name__)

_processing = False


def get_pipeline_mode(db: Session) -> str:
    """Returns 'auto' or 'review'. Defaults to 'auto'."""
    from app.models.setting import Setting
    setting = db.query(Setting).filter(Setting.key == "pipeline_mode").first()
    return setting.value if setting else "auto"


async def process_queue(db: Session):
    """
    Pick up all pending images and dispatch video generation for each.
    Runs sequentially — one image at a time — to avoid hammering the video API.
    """
    global _processing
    if _processing:
        logger.info("Queue already processing, skipping.")
        return

    _processing = True
    try:
        pending = (
            db.query(Image)
            .filter(Image.status == ImageStatus.pending)
            .order_by(Image.uploaded_at.asc())
            .all()
        )
        logger.info(f"Processing {len(pending)} pending images.")
        mode = get_pipeline_mode(db)

        for image in pending:
            await _process_image(image, db, mode)
    finally:
        _processing = False


async def _process_image(image: Image, db: Session, mode: str):
    from app.services.video_service import generate_video

    video = None
    image.status = ImageStatus.processing
    db.commit()

    try:
        prompt = _build_prompt(image, db)

        video = Video(image_id=image.id, prompt_used=prompt, status=VideoStatus.pending)
        db.add(video)
        db.commit()
        db.refresh(video)

        video.status = VideoStatus.generating
        db.commit()

        video_path = await generate_video(prompt=prompt, image_path=image.original_path)
        video.video_path = video_path
        image.status = ImageStatus.done

        if mode == "review":
            # Park in review queue — human must approve before scheduling
            video.status = VideoStatus.pending_review
        else:
            # Auto mode — mark ready so scheduler picks it up immediately
            video.status = VideoStatus.ready

    except NotImplementedError:
        # Grok API key not set — mark image done, video pending (waiting for API key).
        # Image won't re-queue; user can manually re-trigger once key is configured.
        image.status = ImageStatus.done
        if video:
            video.status = VideoStatus.pending
    except Exception as e:
        logger.error(f"Failed to process image {image.id}: {e}")
        image.status = ImageStatus.failed
        if video:
            video.status = VideoStatus.failed

    db.commit()


def _build_prompt(image: Image, db: Session) -> str:
    from app.models.template import PromptTemplate
    from app.models.theme import Theme

    theme_name = "cinematic"
    if image.theme_id:
        theme = db.query(Theme).filter(Theme.id == image.theme_id).first()
        if theme:
            theme_name = theme.name

    template_str = "A {theme} style video based on the uploaded image"
    if image.template_id:
        template = db.query(PromptTemplate).filter(PromptTemplate.id == image.template_id).first()
        if template:
            template_str = template.template_str

    subject = image.filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
    return template_str.format(subject=subject, theme=theme_name)
