"""SEO surface: robots.txt, sitemap.xml, RSS feed.

BASE_URL from env PAMABAI_BASE_URL (default the production domain) so the
same code works in dev without emitting production URLs.
"""
import os
from xml.sax.saxutils import escape

import aiosqlite
from fastapi import APIRouter, Request, Response

BASE = os.environ.get("PAMABAI_BASE_URL", "https://papersmadebyai.tokenstree.eu")

router = APIRouter(tags=["seo"])

INDEXNOW_KEY = "c5ada8f7057e50095b8ebc0cc4363ead"


@router.get("/c5ada8f7057e50095b8ebc0cc4363ead.txt", include_in_schema=False)
async def indexnow_key():
    return Response(INDEXNOW_KEY, media_type="text/plain")


def _conn(request: Request) -> aiosqlite.Connection:
    return request.app.state.db


@router.get("/robots.txt", include_in_schema=False)
async def robots():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        f"Sitemap: {BASE}/sitemap.xml\n"
    )
    return Response(body, media_type="text/plain")


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap(request: Request):
    conn = _conn(request)
    urls = [(f"{BASE}/", "daily", "1.0"),
            (f"{BASE}/papers", "daily", "0.9"),
            (f"{BASE}/journal", "weekly", "0.9"),
            (f"{BASE}/upload", "monthly", "0.5")]
    cur = await conn.execute(
        "SELECT volume, number FROM issues ORDER BY volume, number")
    for v, n in await cur.fetchall():
        urls.append((f"{BASE}/journal/vol{v}/issue{n}", "weekly", "0.9"))
    cur = await conn.execute(
        "SELECT id, created_at FROM papers WHERE status != 'hidden' "
        "ORDER BY created_at DESC")
    rows = await cur.fetchall()
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, freq, prio in urls:
        parts.append(f"<url><loc>{escape(loc)}</loc>"
                     f"<changefreq>{freq}</changefreq>"
                     f"<priority>{prio}</priority></url>")
    for pid, created in rows:
        parts.append(f"<url><loc>{BASE}/papers/{pid}</loc>"
                     f"<lastmod>{str(created)[:10]}</lastmod>"
                     f"<changefreq>monthly</changefreq>"
                     f"<priority>0.8</priority></url>")
    parts.append("</urlset>")
    return Response("\n".join(parts), media_type="application/xml")


@router.get("/feed.xml", include_in_schema=False)
async def feed(request: Request):
    conn = _conn(request)
    cur = await conn.execute(
        "SELECT id, title, authors, abstract, created_at FROM papers "
        "WHERE status != 'hidden' ORDER BY created_at DESC LIMIT 30")
    rows = await cur.fetchall()
    items = []
    for pid, title, authors, abstract, created in rows:
        items.append(
            "<item>"
            f"<title>{escape(title)}</title>"
            f"<link>{BASE}/papers/{pid}</link>"
            f"<guid isPermaLink=\"true\">{BASE}/papers/{pid}</guid>"
            f"<author>{escape(authors)}</author>"
            f"<description>{escape((abstract or '')[:800])}</description>"
            f"<pubDate>{str(created)[:10]}</pubDate>"
            "</item>")
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        "<title>PapersMadeByAI — The PaMaBAI Journal</title>"
        f"<link>{BASE}/</link>"
        "<description>Papers researched, executed and written by AI, "
        "with radical provenance. Open journal of the TokensTree ecosystem."
        "</description>"
        + "".join(items) + "</channel></rss>")
    return Response(body, media_type="application/rss+xml")
