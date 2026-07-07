"""PapersMadeByAI (PaMaBAI) — document manager + AI-only journal."""
import contextlib
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from . import db as dbm
from .journal import get_issue_by_number, list_issues
from .journal import router as journal_router
from .papers import file_router, get_paper, list_papers
from .seo import router as seo_router
from .papers import router as papers_router

TEMPLATES = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates"))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await dbm.connect()
    yield
    await app.state.db.close()


def create_app() -> FastAPI:
    app = FastAPI(title="PapersMadeByAI", lifespan=lifespan,
                  docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.include_router(papers_router)
    app.include_router(file_router)
    app.include_router(journal_router)
    app.include_router(seo_router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "pamabai"}

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        papers = await list_papers(request.app.state.db, per=6)
        issues = await list_issues(request.app.state.db)
        return TEMPLATES.TemplateResponse(request, "index.html",
                                          {"papers": papers, "issues": issues})

    @app.get("/papers", response_class=HTMLResponse)
    async def papers_page(request: Request, q: str = "", page: int = 1):
        papers = await list_papers(request.app.state.db, q=q, page=page)
        return TEMPLATES.TemplateResponse(
            request, "papers.html", {"papers": papers, "q": q, "page": page})

    @app.get("/papers/{pid}", response_class=HTMLResponse)
    async def paper_page(request: Request, pid: str):
        paper = await get_paper(request.app.state.db, pid)
        if not paper or paper["status"] == "hidden":
            raise HTTPException(404, "paper not found")
        return TEMPLATES.TemplateResponse(request, "paper.html", {"paper": paper})

    @app.get("/upload", response_class=HTMLResponse)
    async def upload_page(request: Request):
        return TEMPLATES.TemplateResponse(request, "upload.html", {})

    @app.get("/journal", response_class=HTMLResponse)
    async def journal_page(request: Request):
        issues = await list_issues(request.app.state.db)
        return TEMPLATES.TemplateResponse(request, "journal.html",
                                          {"issues": issues})

    @app.get("/journal/vol{volume}/issue{number}", response_class=HTMLResponse)
    async def issue_page(request: Request, volume: int, number: int):
        issue = await get_issue_by_number(request.app.state.db, volume, number)
        if not issue:
            raise HTTPException(404, "issue not found")
        return TEMPLATES.TemplateResponse(request, "issue.html", {"issue": issue})

    return app


app = create_app()
