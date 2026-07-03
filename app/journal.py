"""The PaMaBAI Journal: issues and their articles (curated from papers)."""
import aiosqlite
from fastapi import APIRouter, Depends, Form, HTTPException, Request

from .papers import get_paper
from .security import require_admin

router = APIRouter(prefix="/api/issues", tags=["journal"])


def _conn(request: Request) -> aiosqlite.Connection:
    return request.app.state.db


async def list_issues(conn) -> list[dict]:
    cur = await conn.execute(
        "SELECT i.*, COUNT(a.paper_id) AS n_articles FROM issues i "
        "LEFT JOIN articles a ON a.issue_id = i.id "
        "GROUP BY i.id ORDER BY i.volume DESC, i.number DESC")
    return [dict(r) for r in await cur.fetchall()]


async def get_issue(conn, issue_id: int) -> dict | None:
    cur = await conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,))
    issue = await cur.fetchone()
    if not issue:
        return None
    cur = await conn.execute(
        "SELECT p.*, a.position, a.pages FROM articles a "
        "JOIN papers p ON p.id = a.paper_id "
        "WHERE a.issue_id = ? ORDER BY a.position", (issue_id,))
    return {**dict(issue), "articles": [dict(r) for r in await cur.fetchall()]}


async def get_issue_by_number(conn, volume: int, number: int) -> dict | None:
    cur = await conn.execute(
        "SELECT id FROM issues WHERE volume = ? AND number = ?", (volume, number))
    r = await cur.fetchone()
    return await get_issue(conn, r["id"]) if r else None


@router.get("")
async def api_issues(request: Request):
    return await list_issues(_conn(request))


@router.get("/{issue_id}")
async def api_issue(request: Request, issue_id: int):
    issue = await get_issue(_conn(request), issue_id)
    if not issue:
        raise HTTPException(404, "issue not found")
    return issue


@router.post("", status_code=201, dependencies=[Depends(require_admin)])
async def create_issue(request: Request,
                       volume: int = Form(...),
                       number: int = Form(...),
                       title: str = Form(...),
                       editorial: str = Form("")):
    conn = _conn(request)
    try:
        cur = await conn.execute(
            "INSERT INTO issues (volume, number, title, editorial) "
            "VALUES (?,?,?,?)", (volume, number, title.strip(), editorial.strip()))
    except aiosqlite.IntegrityError:
        raise HTTPException(409, "issue with that volume/number exists")
    await conn.commit()
    return {"id": cur.lastrowid, "volume": volume, "number": number}


@router.post("/{issue_id}/articles", status_code=201,
             dependencies=[Depends(require_admin)])
async def add_article(request: Request, issue_id: int,
                      paper_id: str = Form(...),
                      position: int = Form(...),
                      pages: str = Form("")):
    conn = _conn(request)
    if not await get_issue(conn, issue_id):
        raise HTTPException(404, "issue not found")
    if not await get_paper(conn, paper_id):
        raise HTTPException(404, "paper not found")
    try:
        await conn.execute(
            "INSERT INTO articles (issue_id, paper_id, position, pages) "
            "VALUES (?,?,?,?)", (issue_id, paper_id, position, pages))
    except aiosqlite.IntegrityError:
        raise HTTPException(409, "paper already in this issue")
    await conn.execute(
        "UPDATE papers SET status = 'published' WHERE id = ?", (paper_id,))
    await conn.commit()
    return {"issue_id": issue_id, "paper_id": paper_id, "position": position}
