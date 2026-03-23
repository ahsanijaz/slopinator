# Privacy Policy

**Last updated:** March 23, 2026

## 1. Overview

This Privacy Policy describes how Slopinator ("the App") handles information when you use it to generate and publish videos to social media platforms.

## 2. Information We Collect

**Content you provide:**
- Images you upload for video generation
- Prompt templates and themes you create
- Captions and hashtags you write or edit

**Automatically collected:**
- Generated video files stored locally on your machine
- Basic usage logs for debugging purposes

## 3. How We Use Your Information

Your data is used solely to operate the App:
- Images are processed to generate videos via the Grok API
- Captions and hashtags are generated via the Anthropic Claude API
- Videos and metadata are posted to TikTok on your behalf

We do not sell, rent, or share your data with any third parties beyond what is necessary to operate the App.

## 4. Third-Party Services

The App connects to the following third-party services. Their privacy policies govern how they handle your data:

- **TikTok** — [https://www.tiktok.com/legal/privacy-policy](https://www.tiktok.com/legal/privacy-policy)
- **xAI (Grok)** — [https://x.ai/privacy](https://x.ai/privacy)
- **Anthropic (Claude)** — [https://www.anthropic.com/privacy](https://www.anthropic.com/privacy)

## 5. Data Storage

All data (uploaded images, generated videos, database) is stored locally on your own machine. No data is stored on remote servers operated by the App developers.

## 6. Data Retention

You have full control over your data. You can delete images, videos, and all associated records directly through the App at any time.

## 7. Security

The App uses JWT-based authentication to protect access to media files and the admin console. We recommend setting a strong `ADMIN_PASSWORD` and `SECRET_KEY` in your `.env` file.

## 8. Changes to This Policy

This policy may be updated at any time. Continued use of the App after changes constitutes acceptance of the updated policy.

## 9. Contact

For privacy-related questions, please open an issue at https://github.com/ahsanijaz/slopinator.
