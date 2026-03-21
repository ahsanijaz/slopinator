"""TikTok service: OAuth flow and video posting via Content Posting API v2."""

import math
import os
import urllib.parse
from typing import Optional

import httpx

from app.config import settings

TIKTOK_API_BASE = "https://open.tiktokapis.com"
TIKTOK_AUTH_BASE = "https://www.tiktok.com/v2/auth/authorize/"
CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB per chunk


async def get_auth_url() -> str:
    """Generate TikTok OAuth authorization URL."""
    params = {
        "client_key": settings.TIKTOK_CLIENT_KEY,
        "response_type": "code",
        "scope": "user.info.basic,video.publish,video.upload",
        "redirect_uri": settings.TIKTOK_REDIRECT_URI,
        "state": "slopinator_oauth",
    }
    return f"{TIKTOK_AUTH_BASE}?{urllib.parse.urlencode(params)}"


async def exchange_code(code: str) -> dict:
    """Exchange auth code for access token.

    Returns dict with keys: access_token, refresh_token, open_id
    """
    url = f"{TIKTOK_API_BASE}/v2/oauth/token/"
    payload = {
        "client_key": settings.TIKTOK_CLIENT_KEY,
        "client_secret": settings.TIKTOK_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.TIKTOK_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        data = resp.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "open_id": data["open_id"],
    }


async def refresh_access_token(refresh_token: str) -> dict:
    """Refresh an expired access token.

    Returns dict with keys: access_token, refresh_token, open_id
    """
    url = f"{TIKTOK_API_BASE}/v2/oauth/token/"
    payload = {
        "client_key": settings.TIKTOK_CLIENT_KEY,
        "client_secret": settings.TIKTOK_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        data = resp.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "open_id": data["open_id"],
    }


async def post_video(
    video_path: str,
    caption: str,
    hashtags: list[str],
    access_token: Optional[str] = None,
) -> str:
    """Upload a video to TikTok using the Content Posting API (FILE_UPLOAD method).

    Steps:
    1. POST /v2/post/publish/video/init/ to initialize the upload and receive an upload_url
    2. Upload the video file in chunks to the upload_url
    3. Return the publish_id

    Args:
        video_path: Absolute path to the video file on disk.
        caption: Caption text for the post.
        hashtags: List of hashtag strings (e.g. ["#funny", "#cat"]).
        access_token: TikTok OAuth access token. Falls back to settings.TIKTOK_ACCESS_TOKEN.

    Returns:
        publish_id string returned by TikTok.
    """
    token = access_token or settings.TIKTOK_ACCESS_TOKEN
    if not token:
        raise ValueError("No TikTok access token available.")

    video_size = os.path.getsize(video_path)
    total_chunk_count = math.ceil(video_size / CHUNK_SIZE)

    title = caption
    if hashtags:
        title = f"{caption} {' '.join(hashtags)}"

    # Step 1: Initialize upload
    init_url = f"{TIKTOK_API_BASE}/v2/post/publish/video/init/"
    init_payload = {
        "post_info": {
            "title": title[:150],  # TikTok title max ~150 chars
            "privacy_level": "SELF_ONLY",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": CHUNK_SIZE,
            "total_chunk_count": total_chunk_count,
        },
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        init_resp = await client.post(init_url, json=init_payload, headers=headers)
        init_resp.raise_for_status()
        init_data = init_resp.json()

    publish_id: str = init_data["data"]["publish_id"]
    upload_url: str = init_data["data"]["upload_url"]

    # Step 2: Upload video in chunks
    with open(video_path, "rb") as fh:
        for chunk_index in range(total_chunk_count):
            chunk_data = fh.read(CHUNK_SIZE)
            actual_chunk_size = len(chunk_data)
            start_byte = chunk_index * CHUNK_SIZE
            end_byte = start_byte + actual_chunk_size - 1

            chunk_headers = {
                "Content-Range": f"bytes {start_byte}-{end_byte}/{video_size}",
                "Content-Length": str(actual_chunk_size),
                "Content-Type": "video/mp4",
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                chunk_resp = await client.put(
                    upload_url,
                    content=chunk_data,
                    headers=chunk_headers,
                )
                chunk_resp.raise_for_status()

    return publish_id
