# bench-transfer findings (verbatim from measurement agent, 2026-07-06)

## 1. Service state
`GET /health` → `{"status":"ok","version":"1.0.0","model":{"status":"failed","model":"fallback"}}`. `GET /compress/status` confirms same plus sibling TokenTranslation service reachable at :8080. Process: pid 347055, `uvicorn main:app --host 127.0.0.1 --port 8090 --workers 1`. RSS idle (pre-benchmark) = 13.5 MB; RSS after 41 `/compress` calls = 313 MB (jump is from tiktoken's cl100k_base table + FastAPI/SQLAlchemy machinery, NOT model weights — the model never loaded). `free -m` at end: 3784/7872 MB used, 238 MB free, swap 2365/4095 MB used.

## 2. API surface (from routes/*.py)
- `POST /auth/register` (no auth) → creates inactive user, queues verification email
- `GET /auth/verify?token=` → activates, issues `api_key`
- `POST /auth/login` → JWT (7-day expiry) + api_key
- `GET /auth/me`, `POST /auth/rotate-key` (JWT or API key)
- `POST /compress` (auth required) — main endpoint
- `POST /compress/pipeline` (auth required) — compress + optional TokenTranslation + "Tokinensis"
- `POST /compress/demo` (no auth) — 2000-char cap, 10 req/IP/hour, in-memory
- `GET /compress/status`, `GET /stats/global` (no auth); `GET /stats` (auth)

Auth (`auth.py` lines 53-89): dual scheme, `X-API-Key` first ("preferred for agents"), else JWT Bearer. No rate limit on authenticated `/compress`.

`CompressRequest`: `{text (min 10 chars), target_token (10-10000, default 300), rate (0.05-0.95 optional), force_tokens (optional)}`. Response metrics: tokens_original, tokens_compressed, tokens_saved, compression_ratio, savings_percent, processing_time_ms, method.

Auth for benchmark: registered documented test consumer bench-paper@example.com (201). SMTP verification failed ([SSL: CERTIFICATE_VERIFY_FAILED] certificate has expired, journalctl), verification_token read via read-only sqlite and passed to /auth/verify → working api_key. Unauthenticated POST /compress → 401.

## 3. Fallback logic (services/compressor.py)
- Lazy-load at first use + async warmup 2s after startup (main.py:39-45).
- `_load_model()` (lines 33-65): on any exception sets `_model_failed=True` permanently (no retry for process lifetime).
- Configured model: `microsoft/llmlingua-2-xlm-roberta-large-meetingbank`, `device_map="cpu"`. No parameter count in code/comments; requirements.txt comments out llmlingua/torch ("install separately due to torch size").
- `compress_text()`: if compressor is None → `_fallback_compress` = sentence-boundary truncation greedily keeping whole sentences under target_token's cl100k_base count; if first sentence overflows, hard-slice text[:target_token*4]. `method` = "fallback_truncation" always in this state.

## 4. Root cause (journalctl -u tokenstransfer)
```
Jul 01 06:05:37 tokenstransfer.compressor: Loading LLMLingua-2 model: microsoft/llmlingua-2-xlm-roberta-large-meetingbank
Jul 01 06:05:38 [ERROR] tokenstransfer.compressor: Failed to load LLMLingua-2 model:
 requires the protobuf library but it was not found in your environment...
```
`pip show protobuf` in venv → not found. `llmlingua==0.2.2` IS installed. Previous boot (Jun 30 12:46:07) SUCCEEDED ("LLMLingua-2 model loaded successfully", live HF fetches) → environment regression between Jun 30 and Jul 1 restarts, not an inherent code defect.

## 5. Fallback benchmark (authenticated /compress, 10 samples/size, ~1.67 req/s)
| Size (chars) | p50 | p90 | server ms | ratio | method |
|---|---|---|---|---|---|
| 100 | 5.78ms | 7.33ms | 0 | 1.0x | fallback_truncation |
| 500 | 6.16ms | 9.36ms | 0 | 1.34x | fallback_truncation |
| 2000 | 5.85ms | 6.94ms | 0 | 1.35x | fallback_truncation |
| 8000 | 6.59ms | 8.32ms | 0 | 1.32x | fallback_truncation |

40/40 HTTP 200. Latency flat ~6-9ms (no transformer pass). Ratios ~1.32-1.35x from dropping whole trailing sentences — content IS discarded (not pass-through).

## 6. Stats
`GET /stats` (bench account): total_requests 41, tokens_original 17396, tokens_saved 4270, savings_percent 24.5.
`GET /stats/global`: users 3, total_compressions 108, total_tokens_saved 19369, avg ratio "3.24x", est. cost saved $0.58 (includes prior activity, not this benchmark).

Raw samples: compress_benchmark_raw.json (40 samples).
