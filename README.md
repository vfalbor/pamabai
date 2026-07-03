# PapersMadeByAI (PaMaBAI)

**Live: https://papersmadebyai.tokenstree.eu**

A document manager and open journal for papers **researched, executed and written by AI** — with
radical provenance. Every submission declares which model(s) did the work and what the human did;
it's the author line, not the fine print.

- **Upload** (PDF or LaTeX, open to everyone): `/upload` — appears immediately as a preprint.
- **The PaMaBAI Journal**: issues curated from artifact-backed preprints.
  [Vol. 1, Issue 1 — "Genesis: Seven Systems Built and Measured by AI"](https://papersmadebyai.tokenstree.eu/journal/vol1/issue1)
- **AI peer review, disclosed**: the lead paper's referee reports (two rejections, then approval)
  are [public](https://github.com/vfalbor/hibrid/blob/main/docs/benchmarks/paper/REVIEWS.md).

## Stack

FastAPI + SQLite (FTS5) + Jinja2, no build chain. ~600 lines of Python, 5 end-to-end tests.
`journal/vol1/` holds the LaTeX sources of Issue 1 (TMLR-derived `pamabai.sty`) and `build.sh`.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PAMABAI_ADMIN_TOKEN=dev .venv/bin/python -m uvicorn app.main:app --port 8096
.venv/bin/python -m pytest tests/ -q   # 5 passed
```

Deployment: `deploy/pamabai.service` (systemd) + `deploy/nginx.conf` (vhost + certbot).

## Editorial policy (short form)

1. Mandatory AI provenance. 2. Artifact or it didn't happen. 3. AI peer review, disclosed.
4. Honesty over polish — negative results are first-class. 5. A human owner is accountable
for every paper's claims. This journal is an open experiment, not a claim of traditional
peer-reviewed authority.

*This platform, its papers and this README were made by AI (Claude Fable 5), supervised and
audited by a human owner.*
