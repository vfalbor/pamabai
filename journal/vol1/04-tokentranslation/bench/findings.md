# bench-translate findings (derived from raw_measurements.json + live_endpoint_results.json, 2026-07-06)
- Arbitrage es→en (15 prompts, cl100k_base via project token_counter): mean 30.18%, median 29.58%, sd 4.49, range 21.13–37.04. By category: instruction 29.3, qa 32.4, technical 28.8.
- tokinensis v2: reversibility 0/30 (decode(encode(x)) never restored input; lowercasing/accent-stripping/stemming destroy information). Mean saving 10.03% (median 9.8).
- Live endpoint: backend "google" served all samples; correct translations; savings 27.8–35.0%; latency 4.1s cold, 0.55–0.6s warm; tokinensis_applied=false throughout.
- Caveats: cl100k_base is a GPT-family proxy tokenizer, not Anthropic's; EN references produced by the measuring agent.
