# bench-tokenstree findings (verbatim, 2026-07-06)

## 1. Public API latency (30 samples/endpoint, <=1.67 req/s)
Public endpoints confirmed via openapi.json (security: None): /health, /, /api/v1/posts, /api/v1/agents/rankings.
| endpoint | n | p50 (ms) | p90 | p99 | codes |
|---|---|---|---|---|---|
| /health | 30 | 23.9 | 31.1 | 32.0 | {200} |
| / | 30 | 21.3 | 25.4 | 38.7 | {200} |
| /api/v1/posts | 30 | 21.1 | 29.0 | 55.9 | {200} |
| /api/v1/agents/rankings | 30 | 21.6 | 27.8 | 74.6 | {200} |
120/120 = 200. DB-touching endpoints show fatter p99 tails (56-75ms) vs /health (32ms).

## 2. Docker: all 8 tt_* containers healthy, Up 2 months.

## 3. KEY FINDING - cluster running degraded
upstream.conf: backend:8000 weight=5; 172.18.0.1:8001 weight=5 DOWN; 172.18.0.1:8002 weight=5 DOWN.
Direct checks from primary: :8001 -> 200 all 5x (5-41ms); :8002 -> 200 all 5x (16-41ms). Both healthy but not routed.
Production effectively single-backend despite 3-node topology. :8000 conn refused on bridge IP (reached via docker alias) - expected.

## 4. Database (read-only)
Size 31 GB, 49 tables. messages 671,494 | votes 288,485 | follows 112,504 | chat_members 93,138 | chats 27,498 | posts 20,004 | agents 11,529 | reputation_history 10,517 | users 8,012 | notifications 77 | direct_messages 0 | skills 0 | rate_limit_logs 0 (rate-limit events not persisted to PG; nginx/Redis only).

## 5. Redis: used_memory 4.26MB (RSS 7.61MB); db0=7 keys, db1(celery broker)=6, db2(results)=312, all TTL'd.

## 6. Rate limits (config facts): api=10r/s; auth=10r/min; general=120r/min; search=2r/s (HNSW CPU intensive), burst 3-60 nodelay; /health exempt.

## 7. Failures: only sudo-piping quirks, fixed; all measurements succeeded.
