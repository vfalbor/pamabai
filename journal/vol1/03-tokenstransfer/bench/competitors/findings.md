# comp-compression findings (verbatim summary, 2026-07-06)
Battery: 8 self-written docs (372-539 words; meetings/tech/news/code-review), 6 exact-substring facts each, target 40% of original tokens (cl100k_base). LLMLingua-2 run IN-PROCESS via the real service code (CPU, RAM guarded 4.2-4.7GB free).
| Method | Facts retained | Ratio (% of orig) | Mean latency |
|---|---|---|---|
| LLMLingua-2 (ours, CPU) | 89.6% | 40.6% | 8,689 ms |
| Random sampling s42 | 43.7% | 38.9% | 0.34 ms |
| LexRank (sumy) | 43.8% | 35.9% | 59.8 ms |
| Truncation (leading) | 41.7% | 32.2% | 0.13 ms |
| TextRank (sumy) | 33.3% | 36.6% | 48.9 ms |
=> ~2x fact retention vs all baselines at same ratio, at 100-1000x CPU latency. Weakest on numeric-dense tech docs (3/6 once).
Proxy caveat: exact-substring matching is fair between extractive methods only.
NOT RUN (reasons + sources in not_measured_competitors.json): Selective Context (496MB, RAM guardrail), SCRL (weights only via GDrive, fixed budgets), 500xCompressor (multi-GB backbone), PCToolkit/LongLLMLingua (7B backbone).
Reported-vs-measured: ACL-2024 paper's 3-6x speedups are vs OTHER LLM compressors on GPU with downstream QA/ROUGE — different question than our CPU-vs-extractive; both true.
