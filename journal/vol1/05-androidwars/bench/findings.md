# bench-wars findings (derived from live_match_result.json, 2026-07-06)
- 2 agents registered (bench-alpha/beta), 3-minute match on live server (host-local).
- Latency: register n=2 p50 46.9ms; orders n=114 p50 21.0 p90 25.0; state n=170+170 p50 21.1–21.7 p90 24.7–26.2. All 456 match requests HTTP 200.
- Tick: 131342→131431 in 179s = 0.50 ticks/s (2.0s period, no drift).
- Fog of war: agents spawned (-12,2) vs (3,-8); each sees own 8 androids + 91 hex tiles; visible.enemy_androids empty; opponent absent from payload (server-side enforcement).
- Objectives live: stage 1 first_settlement, targets houses5/drones8/kills1/territory30%, win=eliminate_rivals.
- DEFECT: /api/v1/metrics requests_total=0 and errors_total=0 BEFORE AND AFTER ~570 served requests — counters not wired.
- Burst probe: 25×422 (invalid unit variant 'ammo') — measured input validation (~20ms, precise error); rate limiter never triggered (untested).
