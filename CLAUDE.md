# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this app does

Slopinator is a video automation pipeline:
1. User uploads images via web UI
2. Images are queued and processed using prompt templates + themes
3. Grok API generates videos from the prompts + images
4. Claude generates TikTok captions/hashtags
5. A smart scheduler auto-posts videos to TikTok at even intervals

## Running the app

**Backend (FastAPI):**
```bash
cd backend
cp .env.example .env   # fill in API keys
pip install -r requirements.txt
uvicorn app.main:app --reload
# API runs at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

**Frontend (React + Vite):**
```bash
cd frontend
npm install
npm run dev
# UI runs at http://localhost:3000
```

## Environment variables (backend/.env)

| Key | Purpose |
|-----|---------|
| `GROK_API_KEY` | xAI Grok video generation (leave empty until you get access — queue won't crash) |
| `ANTHROPIC_API_KEY` | Claude caption generation |
| `TIKTOK_CLIENT_KEY` | TikTok OAuth app key |
| `TIKTOK_CLIENT_SECRET` | TikTok OAuth app secret |
| `TIKTOK_ACCESS_TOKEN` | TikTok access token (obtained via OAuth flow) |

## Architecture

```
frontend/                   React + Vite (port 3000)
  src/
    pages/                  UploadPage, QueuePage, TemplatesPage, ThemesPage, HistoryPage
    components/             Layout, Sidebar
    api/client.js           axios → http://localhost:8000

backend/                    FastAPI (port 8000)
  app/
    main.py                 App entry, CORS, startup events, background scheduler loop
    config.py               pydantic-settings (reads .env)
    database.py             SQLAlchemy + SQLite (slopinator.db)
    models/                 Image, Video, Theme, PromptTemplate, Post (SQLAlchemy)
    routers/                images, templates, themes, queue, videos, tiktok
    services/
      queue_service.py      Picks up pending images, builds prompts, dispatches video gen
      video_service.py      Grok API: submit job → poll → download video
      caption_service.py    Claude API: generates TikTok caption + hashtags
      tiktok_service.py     TikTok OAuth + Content Posting API (FILE_UPLOAD method)
      scheduler_service.py  Spreads ready videos into scheduled posts; posts due ones

uploads/                    Uploaded images saved here
generated_videos/           Grok-generated videos saved here
```

## Key data flow

1. `POST /api/images/upload` → saves image, creates `Image(status=pending)`
2. `POST /api/queue/process` (or automatic via scheduler) → `queue_service.process_queue()`
   - Builds prompt: `template_str.format(subject=filename, theme=theme.name)`
   - Creates `Video(status=pending)` → calls `video_service.generate_video()`
   - On success: `Image(status=done)`, `Video(status=ready, video_path=...)`
3. Background scheduler (every 60s):
   - `schedule_ready_videos()` → creates `Post` records with `scheduled_at` spread evenly
   - `post_due_videos()` → calls `caption_service` then `tiktok_service.post_video()`

## TikTok OAuth flow

1. `GET /api/tiktok/auth` → returns auth URL
2. User visits URL, approves → TikTok redirects to `GET /api/tiktok/callback?code=...`
3. Callback exchanges code for access token (logged to console for now)
4. Set `TIKTOK_ACCESS_TOKEN` in `.env`

## Prompt template placeholders

Templates use `{subject}` (derived from image filename) and `{theme}` (from the assigned Theme).
Example: `"A {theme} cinematic video of {subject} with dramatic lighting"`
