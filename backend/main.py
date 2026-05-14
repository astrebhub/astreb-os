import json
from html import escape
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"
CONTENT_DIR = BASE_DIR / "content"
ASSET_DIR = FRONTEND_DIR / "assets"

app = FastAPI(title="JAZEKKER News Portal")
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


def load_articles() -> list[dict[str, Any]]:
    articles_dir = CONTENT_DIR / "articles"
    articles: list[dict[str, Any]] = []
    for path in sorted(articles_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, list):
            articles.extend(item for item in data if isinstance(item, dict))
        elif isinstance(data, dict):
            articles.append(data)

    public_articles = [
        article
        for article in articles
        if article.get("status") in {"published_local", "published_external", "published"}
    ]
    return sorted(public_articles, key=lambda item: item.get("published_at", ""), reverse=True)


def article_url(article: dict[str, Any]) -> str:
    slug = article.get("slug") or article.get("id") or "article"
    return f"/jazekker/articles/{slug}"


def render_article(article: dict[str, Any]) -> str:
    paragraphs = "\n".join(
        f"<p>{escape(str(paragraph))}</p>" for paragraph in article.get("body", [])
    )
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(article.get("title", "JAZEKKER"))}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #071019;
      --panel: #0d1a25;
      --line: #203345;
      --text: #edf4f7;
      --muted: #9badba;
      --gold: #e2b354;
      --green: #6fd2a5;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: radial-gradient(circle at 75% 0%, #11243a 0, var(--bg) 38%); color: var(--text); }}
    .shell {{ width: min(920px, calc(100% - 36px)); margin: 0 auto; padding: 24px 0 64px; }}
    header {{ display: flex; justify-content: space-between; gap: 18px; align-items: center; padding-bottom: 22px; border-bottom: 1px solid var(--line); }}
    a {{ color: inherit; }}
    .back {{ min-height: 38px; border: 1px solid var(--line); border-radius: 6px; padding: 0 12px; display: inline-flex; align-items: center; text-decoration: none; background: #12283a; }}
    .brand {{ color: var(--gold); letter-spacing: 0; font-weight: 700; }}
    article {{ margin-top: 42px; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }}
    .chip {{ display: inline-flex; align-items: center; min-height: 24px; padding: 3px 8px; border-radius: 6px; background: #13283a; color: #c5d1db; font-size: 12px; }}
    .chip.local {{ background: #173628; color: #aee7c7; }}
    h1 {{ margin: 0; max-width: 820px; font-size: 44px; line-height: 1.05; letter-spacing: 0; }}
    .dek {{ margin-top: 18px; max-width: 760px; color: #c7d4df; font-size: 20px; line-height: 1.5; }}
    .lens {{ margin: 28px 0; padding: 16px; border: 1px solid #385339; border-radius: 8px; background: rgba(17, 38, 31, .88); color: #dceadf; }}
    .body {{ margin-top: 26px; max-width: 760px; }}
    p {{ color: #d7e1e8; font-size: 18px; line-height: 1.72; }}
    .next {{ margin-top: 34px; padding-top: 18px; border-top: 1px solid var(--line); color: var(--gold); }}
    @media (max-width: 760px) {{ h1 {{ font-size: 34px; }} .dek, p {{ font-size: 17px; }} }}
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="brand">JAZEKKER</div>
      <a class="back" href="/jazekker/news">Назад к ленте</a>
    </header>
    <article>
      <div class="meta">
        <span class="chip local">опубликовано</span>
        <span class="chip">{escape(article.get("category_label", ""))}</span>
        <span class="chip">{escape(str(article.get("reading_minutes", 4)))} мин</span>
        <span class="chip">{escape(article.get("published_at", ""))}</span>
      </div>
      <h1>{escape(article.get("title", ""))}</h1>
      <div class="dek">{escape(article.get("dek", ""))}</div>
      <div class="lens"><strong>Фокус материала:</strong> {escape(article.get("orientation_lens", ""))}</div>
      <div class="body">{paragraphs}</div>
      <div class="next"><strong>Следующий шаг:</strong> {escape(article.get("next_orientation_step", ""))}</div>
    </article>
  </div>
</body>
</html>"""


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "jazekker-news-portal"}


@app.get("/")
async def root():
    return RedirectResponse(url="/jazekker", status_code=307)


@app.get("/jazekker")
async def homepage():
    return FileResponse(FRONTEND_DIR / "jazekker.html", media_type="text/html")


@app.get("/jazekker/news")
async def news_page():
    return FileResponse(FRONTEND_DIR / "jazekker-news.html", media_type="text/html")


@app.get("/jazekker/assets/{asset_name}")
async def asset(asset_name: str):
    asset_path = ASSET_DIR / asset_name
    if not asset_path.exists() or asset_path.parent != ASSET_DIR:
        raise HTTPException(status_code=404, detail="asset_not_found")
    return FileResponse(asset_path)


@app.get("/jazekker/articles")
async def articles():
    items = []
    for article in load_articles():
        item = dict(article)
        item["url"] = article_url(article)
        items.append(item)
    return {"articles": items, "count": len(items)}


@app.get("/jazekker/articles/{slug}", response_class=HTMLResponse)
async def article_page(slug: str):
    for article in load_articles():
        if slug in {article.get("slug"), article.get("id")}:
            return render_article(article)
    raise HTTPException(status_code=404, detail="article_not_found")
