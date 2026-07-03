"""Papers: upload, browse, search, detail, file download."""
import os
import uuid

import aiosqlite
from fastapi import APIRouter, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse

from . import db as dbm
from .security import require_admin, validate_upload
from fastapi import Depends

router = APIRouter(prefix="/api/papers", tags=["papers"])

MEDIA = {"pdf": "application/pdf", "latex": "text/plain"}


def _conn(request: Request) -> aiosqlite.Connection:
    return request.app.state.db


async def create_paper(conn, *, title, authors, abstract, keywords, ai_models,
                       human_role, artifact_url, license_, kind, filename,
                       content) -> dict:
    pid = uuid.uuid4().hex[:12]
    pdir = os.path.join(dbm.data_dir(), "uploads", pid)
    os.makedirs(pdir, exist_ok=True)
    safe_name = os.path.basename(filename) or f"paper.{kind}"
    with open(os.path.join(pdir, safe_name), "wb") as f:
        f.write(content)
    row = dict(id=pid, title=title.strip(), authors=authors.strip(),
               abstract=abstract.strip(), keywords=keywords.strip(),
               ai_models=ai_models.strip(), human_role=human_role.strip(),
               artifact_url=artifact_url.strip(), license=license_.strip(),
               kind=kind, filename=safe_name, size_bytes=len(content))
    await conn.execute(
        "INSERT INTO papers (id,title,authors,abstract,keywords,ai_models,"
        "human_role,artifact_url,license,kind,filename,size_bytes) "
        "VALUES (:id,:title,:authors,:abstract,:keywords,:ai_models,"
        ":human_role,:artifact_url,:license,:kind,:filename,:size_bytes)", row)
    await dbm.fts_index(conn, row)
    await conn.commit()
    return row


async def get_paper(conn, pid: str) -> dict | None:
    cur = await conn.execute("SELECT * FROM papers WHERE id = ?", (pid,))
    r = await cur.fetchone()
    return dict(r) if r else None


async def list_papers(conn, q: str = "", page: int = 1, per: int = 20,
                      include_hidden: bool = False) -> list[dict]:
    off = (max(page, 1) - 1) * per
    vis = "" if include_hidden else "AND p.status != 'hidden'"
    if q.strip():
        cur = await conn.execute(
            f"SELECT p.* FROM papers_fts f JOIN papers p ON p.id = f.id "
            f"WHERE papers_fts MATCH ? {vis} "
            f"ORDER BY p.created_at DESC LIMIT ? OFFSET ?",
            (dbm.fts_query(q), per, off))
    else:
        cur = await conn.execute(
            f"SELECT p.* FROM papers p WHERE 1=1 {vis} "
            f"ORDER BY p.created_at DESC LIMIT ? OFFSET ?", (per, off))
    return [dict(r) for r in await cur.fetchall()]


@router.post("", status_code=201)
async def upload(request: Request,
                 file: UploadFile,
                 title: str = Form(...),
                 authors: str = Form(...),
                 abstract: str = Form(""),
                 keywords: str = Form(""),
                 ai_models: str = Form(...),
                 human_role: str = Form(""),
                 artifact_url: str = Form(""),
                 license: str = Form("CC BY 4.0")):
    if not title.strip() or not authors.strip():
        raise HTTPException(422, "title and authors are required")
    if not ai_models.strip():
        raise HTTPException(422, "ai_models is required: disclose which AI model(s) made this paper")
    kind, content = await validate_upload(file)
    row = await create_paper(
        _conn(request), title=title, authors=authors, abstract=abstract,
        keywords=keywords, ai_models=ai_models, human_role=human_role,
        artifact_url=artifact_url, license_=license, kind=kind,
        filename=file.filename or "", content=content)
    if "text/html" in (request.headers.get("accept") or ""):
        return RedirectResponse(f"/papers/{row['id']}", status_code=303)
    return {"id": row["id"], "url": f"/papers/{row['id']}"}


@router.get("")
async def api_list(request: Request, q: str = "", page: int = 1):
    return await list_papers(_conn(request), q=q, page=page)


@router.get("/{pid}")
async def api_detail(request: Request, pid: str):
    paper = await get_paper(_conn(request), pid)
    if not paper or paper["status"] == "hidden":
        raise HTTPException(404, "paper not found")
    return paper


@router.patch("/{pid}", dependencies=[Depends(require_admin)])
async def api_moderate(request: Request, pid: str, status: str = Form(...)):
    if status not in ("preprint", "published", "hidden"):
        raise HTTPException(422, "bad status")
    conn = _conn(request)
    if not await get_paper(conn, pid):
        raise HTTPException(404, "paper not found")
    await conn.execute("UPDATE papers SET status = ? WHERE id = ?", (status, pid))
    await conn.commit()
    return {"id": pid, "status": status}


# File download lives outside /api so the URL reads naturally.
file_router = APIRouter(tags=["papers"])


@file_router.get("/papers/{pid}/file")
async def download(request: Request, pid: str):
    paper = await get_paper(_conn(request), pid)
    if not paper or paper["status"] == "hidden":
        raise HTTPException(404, "paper not found")
    path = os.path.join(dbm.data_dir(), "uploads", pid, paper["filename"])
    if not os.path.exists(path):
        raise HTTPException(410, "file missing")
    media = "application/zip" if paper["filename"].endswith(".zip") \
        else MEDIA[paper["kind"]]
    disp = "inline" if paper["kind"] == "pdf" else "attachment"
    return FileResponse(path, media_type=media, filename=paper["filename"],
                        content_disposition_type=disp)
