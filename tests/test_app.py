"""End-to-end tests over the ASGI app (temp data dir, real SQLite)."""
import io
import os
import tempfile

import pytest
from httpx import ASGITransport, AsyncClient

os.environ["PAMABAI_DATA"] = tempfile.mkdtemp(prefix="pamabai-test-")
os.environ["PAMABAI_ADMIN_TOKEN"] = "test-admin-token"

from app.main import create_app  # noqa: E402

PDF = b"%PDF-1.4 minimal test pdf content padded to pass size check....."
FIELDS = {
    "title": "A Test Paper Made By AI",
    "authors": "The test project (AI agents)",
    "abstract": "We test the upload path end to end.",
    "keywords": "testing, routers",
    "ai_models": "claude-fable-5",
    "human_role": "audit",
    "artifact_url": "https://github.com/vfalbor/hibrid",
}
ADMIN = {"X-Admin-Token": "test-admin-token"}


@pytest.fixture()
async def client():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://t") as c:
        async with app.router.lifespan_context(app):
            yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "pamabai"}


@pytest.mark.asyncio
async def test_upload_list_search_download(client):
    r = await client.post("/api/papers", data=FIELDS,
                          files={"file": ("t.pdf", io.BytesIO(PDF), "application/pdf")})
    assert r.status_code == 201, r.text
    pid = r.json()["id"]

    r = await client.get("/api/papers")
    assert any(p["id"] == pid for p in r.json())

    r = await client.get("/api/papers", params={"q": "routers"})
    assert any(p["id"] == pid for p in r.json())
    r = await client.get("/api/papers", params={"q": "zzznope"})
    assert all(p["id"] != pid for p in r.json())

    r = await client.get(f"/papers/{pid}/file")
    assert r.status_code == 200 and r.content.startswith(b"%PDF-")

    for page in ("/", "/papers", f"/papers/{pid}", "/upload", "/journal"):
        rp = await client.get(page)
        assert rp.status_code == 200, page
    assert "Made by AI" in (await client.get(f"/papers/{pid}")).text


@pytest.mark.asyncio
async def test_upload_rejections(client):
    bad = dict(FIELDS)
    r = await client.post("/api/papers", data=bad,
                          files={"file": ("evil.exe", io.BytesIO(b"MZ" * 20), "application/x-dosexec")})
    assert r.status_code == 415

    r = await client.post("/api/papers", data=bad,
                          files={"file": ("fake.pdf", io.BytesIO(b"not a pdf but long enough"), "application/pdf")})
    assert r.status_code == 415

    noai = {k: v for k, v in FIELDS.items() if k != "ai_models"}
    r = await client.post("/api/papers", data=noai,
                          files={"file": ("t.pdf", io.BytesIO(PDF), "application/pdf")})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_latex_upload(client):
    r = await client.post("/api/papers", data=FIELDS,
                          files={"file": ("p.tex", io.BytesIO(b"\\documentclass{article}\\begin{document}x\\end{document}"), "text/x-tex")})
    assert r.status_code == 201
    assert (await client.get(f"/api/papers/{r.json()['id']}")).json()["kind"] == "latex"


@pytest.mark.asyncio
async def test_journal_flow(client):
    r = await client.post("/api/papers", data=FIELDS,
                          files={"file": ("t.pdf", io.BytesIO(PDF), "application/pdf")})
    pid = r.json()["id"]

    r = await client.post("/api/issues", data={"volume": 1, "number": 1,
                                               "title": "Genesis", "editorial": "First."})
    assert r.status_code == 401  # no token

    r = await client.post("/api/issues", data={"volume": 1, "number": 1,
                                               "title": "Genesis", "editorial": "First."},
                          headers=ADMIN)
    assert r.status_code == 201
    iid = r.json()["id"]

    r = await client.post(f"/api/issues/{iid}/articles",
                          data={"paper_id": pid, "position": 1, "pages": "1-8"},
                          headers=ADMIN)
    assert r.status_code == 201

    issue = (await client.get(f"/api/issues/{iid}")).json()
    assert issue["articles"][0]["id"] == pid
    assert issue["articles"][0]["status"] == "published"

    r = await client.get("/journal/vol1/issue1")
    assert r.status_code == 200 and "Genesis" in r.text
