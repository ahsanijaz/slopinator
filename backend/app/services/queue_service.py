import asyncio
import logging

from sqlalchemy.orm import Session

from app.models.image import Image, ImageStatus
from app.models.video import Video, VideoStatus

logger = logging.getLogger(__name__)

_processing = False


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

        for image in pending:
            await _process_image(image, db)
    finally:
        _processing = False


async def _process_image(image: Image, db: Session):
    from app.models.template import PromptTemplate
    from app.models.theme import Theme
    from app.services.video_service import generate_video

    image.status = ImageStatus.processing
    db.commit()

    try:
        # Build prompt from template + theme
        prompt = _build_prompt(image, db)

        # Create a video record
        video = Video(image_id=image.id, prompt_used=prompt, status=VideoStatus.pending)
        db.add(video)
        db.commit()
        db.refresh(video)

        # Attempt video generation (will raise NotImplementedError until Grok key is set)
        video.status = VideoStatus.generating
        db.commit()

        video_path = await generate_video(prompt=prompt, image_path=image.original_path)
        video.video_path = video_path
        video.status = VideoStatus.ready
        image.status = ImageStatus.done

    except NotImplementedError:
        # Grok API not configured yet — mark as pending to retry later
        image.status = ImageStatus.pending
        if video:
            video.status = VideoStatus.failed
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
