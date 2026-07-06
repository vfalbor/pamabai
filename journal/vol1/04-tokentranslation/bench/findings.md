# bench-translate findings (derived from raw_measurements.json + live_endpoint_results.json, 2026-07-06)
- Arbitrage es→en (15 prompts, cl100k_base via project token_counter): mean 30.18%, median 29.58%, sd 4.49, range 21.13–37.04. By category: instruction 29.3, qa 32.4, technical 28.8.
- tokinensis v2: reversibility 0/30 (decode(encode(x)) never restored input; lowercasing/accent-stripping/stemming destroy information). Mean saving 10.03% (median 9.8).
- Live endpoint: backend "google" served all samples; correct translations; savings 27.8–35.0%; latency 4.1s cold, 0.55–0.6s warm; tokinensis_applied=false throughout.
- Caveats: cl100k_base is a GPT-family proxy tokenizer, not Anthropic's; EN references produced by the measuring agent.

## ADDENDUM — agent final report (verbatim key items, 2026-07-06)
- Code's hardcoded LANGUAGE_TOKEN_MULTIPLIERS (token_counter.py:11-29) asserts ES=1.27x/EN; MEASURED ratio ≈1.43x — static constant diverges from measurement.
- Tokinensis split by language: ES mean 21.32% saving; EN mean **-1.27%**, 7/15 (47%) NEGATIVE (costs more tokens). Contradicts code's static 0.72x tokinensis multiplier.
- Failure causes: (a) encode = lossy prefix truncation (no inverse by construction); (b) decode does unconditional regex root substitution causing cross-language corruption ("del"→"delete", "por qué"→"for qué").
- Auth flow: require_email_verification=False live; register+bearer worked first try. .env unreadable → backend=google verified empirically (all 3 live calls), not from config.
- Latency: 4136/555/602 ms (first = cold outlier); n=3 → indicative only.
