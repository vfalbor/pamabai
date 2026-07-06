# bench-news findings (verbatim, 2026-07-06)

Store: ~/hnreviewer/data/review.db (SQLite/WAL, 6.2MB). Tables: tested_apps (561), daily_runs (88), weekly_top5 (10), daily_news, subscribers (3). reports/: 88 daily md files 2026-04-06..2026-07-05.

## Corpus
- 561 distinct apps reviewed (unique url). daily_runs: 562 found -> 542 tested + 20 skipped (dedup).
- Score 0-100: n=561 mean 58.05 median 58 p10 46 p90 70 min 17 max 82. Histogram 10-19:1, 30-39:17, 40-49:77, 50-59:213, 60-69:196, 70-79:56, 80-89:1.
- Badges: worth-watching 313 (55.8%), niche 223 (39.7%), skip 21 (3.7%), strong-candidate 4 (0.7%).
- Reviews/ISO week ~30-55 from W15-W27.
- TESTABILITY (derived from enriched.tests_passed/tests_total; no ground-truth flag): zero tests run 261/561 (46.5%); ran-but-passed-none 197/561 (35.1%); partial 73 (13.0%); full pass 30 (5.3%). => 81.6% ran no tests or passed zero.

## 11 criteria (src/scorer/scorer.js WEIGHTS): hn_sentiment 15, novelty 11, current_relevance 11, differentiation 11, performance 10, ease_of_use 8, ease_of_integration 8, documentation 7, maturity 7, community 7, system_requirements 5 (sum 100). total = round(sum(s_i*w_i)/sum(active_w)*10); null criteria excluded, weight redistributed.
Mean per-criterion (0-10): hn_sentiment 7.25 (n=395), novelty 7.37, current_relevance 7.16, differentiation 6.30, performance 5.17 (384), ease_of_use 3.23 (559, weakest), ease_of_integration 4.97 (518), documentation 5.74, maturity 5.03, community 4.66, system_requirements 4.57.
Off-schema keys from LLM judge in scores_json (<5% rows): overall*, security (8), additional_criterion (4)... not counted in weighted total.

## Pipeline
Cron: daily 15:00 UTC review; Fri 15:30 weekly HN comment; Fri 16:00 digest. Run duration: mean 346.1s (min 34.7, max 764.5, n=91).
DEFECT: GitHub artifact uploads failing "Bad credentials" 100% in last ~10 days of run.log; logged non-fatal; misleading "Uploaded to GitHub" line follows.

## Newsletter: weekly_top5 = 10 rows (1 init + 9 real: W15-19, W22, W24-26; gaps W20/21/23). 12 rendered weekly HTML (W14-W25). Subscribers: 3 confirmed.

## Gaps: no structured install-status field (testability inferred); portal card count not obtainable via curl (client-rendered); daily_news table unanalyzed.
