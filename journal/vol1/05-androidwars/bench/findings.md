# bench-wars findings (derived from live_match_result.json, 2026-07-06)
- 2 agents registered (bench-alpha/beta), 3-minute match on live server (host-local).
- Latency: register n=2 p50 46.9ms; orders n=114 p50 21.0 p90 25.0; state n=170+170 p50 21.1–21.7 p90 24.7–26.2. All 456 match requests HTTP 200.
- Tick: 131342→131431 in 179s = 0.50 ticks/s (2.0s period, no drift).
- Fog of war: agents spawned (-12,2) vs (3,-8); each sees own 8 androids + 91 hex tiles; visible.enemy_androids empty; opponent absent from payload (server-side enforcement).
- Objectives live: stage 1 first_settlement, targets houses5/drones8/kills1/territory30%, win=eliminate_rivals.
- DEFECT: /api/v1/metrics requests_total=0 and errors_total=0 BEFORE AND AFTER ~570 served requests — counters not wired.
- Burst probe: 25×422 (invalid unit variant 'ammo') — measured input validation (~20ms, precise error); rate limiter never triggered (untested).

## ADDENDUM — agent final report (verbatim key items, 2026-07-06)
- RATE LIMIT CONFIRMED: burst of 25 POST /orders → requests 1-20: 422 (invalid enum); requests 21-25: **429 {"error":"rate_limited"}**. Limit = 20/10s as documented. KEY: 422s consumed budget → token bucket sits IN FRONT of body validation.
- FOG OF WAR (end of match, same tick 131431): alpha enemy_androids = 6 IDs == beta's own roster EXACTLY; beta's 6 == alpha's roster; zero overlap. enemy_structures likewise disjoint/complementary. Definitive per-agent filtering.
- DOC BUGS: register returns 200 (guide says 201); /metrics is Prometheus text (guide says JSON); produce enum is drone|vehicle|worker (guide says ammo|drone|vehicle).
- Metrics: orders_queued_total also stuck at 0; only agents_active moved (2→4).
- RSS 14.4MB → 91.4MB during the 4-min window (~100 other live agents concurrent; not cleanly attributable). CPU +25s. Release binary 15MB. postgres 48.8MiB, redis 15.1MiB.
- Tier progressed poblado→villa during match. ~100 pre-existing agents on leaderboard. Port 8080 localhost-only (external timed out).
