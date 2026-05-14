# JAZEKKER

JAZEKKER is a calm orientation news portal.

It is designed to turn noisy information into readable civic signals:

```text
noise -> signal -> context -> orientation
```

The public product is not a dashboard, not a chatbot, and not a control panel.
It is a lightweight news and orientation surface for readers.

## What This Branch Contains

- Public homepage: `/jazekker`
- Public news feed: `/jazekker/news`
- Readable article pages: `/jazekker/articles/{slug}`
- Local JSON article content
- Static visual assets
- Minimal FastAPI runtime

## Project Structure

```text
backend/
  main.py                 # minimal JAZEKKER FastAPI app
  requirements.txt

frontend/
  jazekker.html           # public homepage
  jazekker-news.html      # public news feed
  assets/                 # public visual assets

content/
  articles/               # local published article JSON

tests/
  test_jazekker_surfaces.py
```

## Run Locally

```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/jazekker
```

## Editorial Principle

JAZEKKER does not compete on outrage, speed, or volume.

It competes on:

- clarity
- context
- source awareness
- calm presentation
- orientation value

## Current Status

This branch is the public news-portal version of JAZEKKER.
