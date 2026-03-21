"""Caption generation service: uses Claude API to generate TikTok captions."""

import json

import anthropic

from app.config import settings


async def generate_caption(theme: str, subject: str) -> dict:
    """Call Claude to generate a TikTok caption and hashtags.

    Args:
        theme: The visual/stylistic theme of the video (e.g. "cinematic", "lofi").
        subject: What the video is about (e.g. "a cat playing piano").

    Returns:
        dict with keys "caption" (str) and "hashtags" (list[str]).
    """
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate a TikTok caption for a {theme} style video about {subject}. "
                    'Return JSON only: {"caption": "...", "hashtags": ["#tag1", "#tag2"]}'
                ),
            }
        ],
    )
    text = message.content[0].text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text.strip())
