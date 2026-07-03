"""Admin gate + upload validation."""
import os

from fastapi import Header, HTTPException, UploadFile

MAX_BYTES = 25 * 1024 * 1024
ALLOWED = {".pdf": "pdf", ".tex": "latex", ".zip": "latex"}


def require_admin(x_admin_token: str = Header(default="")) -> None:
    expected = os.environ.get("PAMABAI_ADMIN_TOKEN", "")
    if not expected:
        raise HTTPException(503, "admin token not configured")
    if x_admin_token != expected:
        raise HTTPException(401, "invalid admin token")


async def validate_upload(file: UploadFile) -> tuple[str, bytes]:
    """Return (kind, content) or raise 413/415."""
    name = (file.filename or "").lower()
    ext = os.path.splitext(name)[1]
    if ext not in ALLOWED:
        raise HTTPException(415, "only .pdf, .tex or .zip (LaTeX bundle) accepted")
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(413, "file exceeds 25 MB limit")
    if len(content) < 16:
        raise HTTPException(415, "file too small to be a paper")
    if ext == ".pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(415, "not a valid PDF")
    if ext == ".zip" and not content.startswith(b"PK"):
        raise HTTPException(415, "not a valid ZIP archive")
    if ext == ".tex":
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(415, "not a UTF-8 LaTeX source")
    return ALLOWED[ext], content
