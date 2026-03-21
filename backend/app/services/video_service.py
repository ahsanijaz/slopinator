"""
Video generation service — wraps xAI Grok video generation API.

The Grok video API is not yet publicly available. This module is built
against the expected API shape based on xAI's documentation. Once you
receive API access, set GROK_API_KEY in your .env file and it will work.

Expected flow:
  1. Submit a generation job (image + text prompt) → get a job_id
  2. Poll until the job is complete
  3. Download the video file and save it locally
"""

import asyncio
import logging
import os
import uuid

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GROK_API_BASE = "https://api.x.ai/v1"
OUTPUT_DIR = "generated_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Polling config
POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 60  # 5 min timeout


async def generate_video(prompt: str, image_path: str) -> str:
    """
    Submit a video generation job to Grok and poll until complete.
    Returns the local path to the downloaded video file.

    Raises:
        NotImplementedError: if GROK_API_KEY is not configured
        RuntimeError: if generation fails or times out
    """
    if not settings.GROK_API_KEY:
        raise NotImplementedError(
            "GROK_API_KEY is not set. Add it to your .env file once you receive xAI API access."
        )

    async with httpx.AsyncClient(timeout=30) as client:
        job_id = await _submit_job(client, prompt, image_path)
        video_url = await _poll_until_ready(client, job_id)
        local_path = await _download_video(client, video_url)

    logger.info(f"Video generated: {local_path}")
    return local_path


async def _submit_job(client: httpx.AsyncClient, prompt: str, image_path: str) -> str:
    """Submit a video generation job. Returns job_id."""
    with open(image_path, "rb") as f:
        image_data = f.read()

    import base64
    image_b64 = base64.b64encode(image_data).decode()
    ext = os.path.splitext(image_path)[1].lstrip(".") or "jpeg"
    mime = f"image/{ext}"

    response = await client.post(
        f"{GROK_API_BASE}/video/generations",
        headers={"Authorization": f"Bearer {settings.GROK_API_KEY}"},
        json={
            "model": "grok-2-vision",  # update when Grok video model name is confirmed
            "prompt": prompt,
            "image": f"data:{mime};base64,{image_b64}",
        },
    )
    response.raise_for_status()
    data = response.json()
    job_id = data.get("id") or data.get("job_id")
    if not job_id:
        raise RuntimeError(f"No job_id in Grok response: {data}")
    return job_id


async def _poll_until_ready(client: httpx.AsyncClient, job_id: str) -> str:
    """Poll the job status endpoint until the video URL is available."""
    for attempt in range(MAX_POLL_ATTEMPTS):
        response = await client.get(
            f"{GROK_API_BASE}/video/generations/{job_id}",
            headers={"Authorization": f"Bearer {settings.GROK_API_KEY}"},
        )
        response.raise_for_status()
        data = response.json()

        status = data.get("status", "").lower()
        logger.debug(f"Grok job {job_id} status: {status} (attempt {attempt + 1})")

        if status in ("completed", "succeeded", "done"):
            url = data.get("video_url") or data.get("output", {}).get("url")
            if not url:
                raise RuntimeError(f"Job completed but no video_url in response: {data}")
            return url

        if status in ("failed", "error", "cancelled"):
            raise RuntimeError(f"Grok video generation failed: {data.get('error', data)}")

        await asyncio.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError(f"Grok video generation timed out after {MAX_POLL_ATTEMPTS} attempts.")


async def _download_video(client: httpx.AsyncClient, url: str) -> str:
    """Download the generated video and save it locally. Returns local path."""
    filename = f"{uuid.uuid4().hex}.mp4"
    local_path = os.path.join(OUTPUT_DIR, filename)

    async with client.stream("GET", url) as response:
        response.raise_for_status()
        with open(local_path, "wb") as f:
            async for chunk in response.aiter_bytes(chunk_size=8192):
                f.write(chunk)

    return local_path
