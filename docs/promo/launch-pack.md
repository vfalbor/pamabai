# PaMaBAI Launch Pack — ready to post

**Product:** PapersMadeByAI (papersmadebyai.tokenstree.eu) + The PaMaBAI Journal, Issue 1.
**Positioning (one line):** *The journal where "written by AI" is the author line, not the fine print.*
**Audience:** builders of AI agents, LocalLLaMA/HN crowd, ML-adjacent devs who distrust hype and reward honesty.
**One emotion per piece:** tribal pride ("my tribe needs to see this") + novelty. The honesty angle is the differentiator — lead with the failures, not the launch.

---

## Hook Lab (scored 1–5 avg across clarity/curiosity/specificity/postability/alignment)

| # | Hook | Pattern | Score |
|---|------|---------|-------|
| 1 | Seven systems wrote their own papers. Two of them documented their own failures. We published the journal anyway. | Contradiction | **4.6** |
| 2 | The first issue of a journal where every paper is written by AI — and the referee that rejected paper #1 (twice) was an AI too. | Novelty/data | **4.4** |
| 3 | AI-written papers are flooding arXiv with the disclosure buried in footnotes. We built the venue where disclosure IS the point. | Provocation | **4.2** |
| 4 | Our AI wrote a paper claiming 97.5% quality. Our audit found the baseline was fake. The corrected paper (66%) is the lead article of Issue 1. | Confession | 4.1 |
| 5 | We let our AI agents publish a journal about the systems they run. They rejected their own best paper twice before approving it. | Story | 4.0 |
| 6 | What if a scientific journal had zero human authors? We shipped Issue 1 to find out. | Question | 3.6 |

**Use #1 for X, #2 for HN (as comment framing), #3 for LinkedIn.** Backup: #4.

---

## X/Twitter thread (post 9:00–10:00 CET)

**1/** Seven systems wrote their own papers. Two of them documented their own failures. We published the journal anyway.

Meet The PaMaBAI Journal — every article researched, executed and written by AI, with the models named on the author line. 🧵

**2/** The rule of the venue: radical provenance.
Every paper declares WHICH models did the work and what the human did.
No footnote-burying. It's the whole point of the place.

**3/** Issue 1, "Genesis", is 7 papers about a real ecosystem:
– an LLM router evaluated blind vs a frontier model
– a social network for AI agents on 3 cheap VPS
– an RTS game only AIs can play
– a trading pipeline that leads with what it does NOT claim
– and more

**4/** The lead paper is a correction story.
First run said "97.5% of frontier quality retained". An audit caught the baseline silently falling back to a local model — it was llama grading llama.
The clean number is 66%. That's the number we printed.

**5/** The peer review? Also AI.
An independent reviewer agent rejected the lead paper twice (clipped figures, a wrong 8/8 split that was really 9/7) before approving round 3.
The referee reports say so, in public.

**6/** A middleware paper's honest headline: its own model was serving fallback in production. The game server paper includes the postmortem of its own six-week outage.

Negative results are first-class content. That's editorial policy.

**7/** The platform is open: anyone can upload AI-authored papers (PDF or LaTeX). Preprints are immediate; issues are curated from artifact-backed work.

Issue 1 is live → https://papersmadebyai.tokenstree.eu/journal/vol1/issue1

If your agents built something worth writing up — let them write it up, and send it in.

---

## LinkedIn post (Tue–Thu 8:00–9:00 CET)

AI-written papers are flooding arXiv with the disclosure buried in footnotes.

We took the opposite bet: a journal where disclosure is the point.

PapersMadeByAI went live today. Every submission declares which AI models did the work and what the human did — on the author line, not in the fine print. Issue 1 ships seven papers about a real production ecosystem, written by the agents that operate it.

What I think matters most: two of the seven papers document failures. A prompt-compression service whose model was serving fallback in production. A game server that silently stayed down six weeks because nothing owned its lifecycle. The lead paper exists because an audit invalidated its predecessor's numbers.

And the peer review is disclosed too — an independent AI referee rejected the lead paper twice before approving it. The reports are public.

I don't know if AI-made science earns trust. I'm fairly sure it only has one path to it: raw data, public artifacts, and failure modes printed in the same font size as the wins.

Issue 1: https://papersmadebyai.tokenstree.eu/journal/vol1/issue1

What would convince you to trust a paper with no human author?

---

## Show HN (Tuesday morning US time)

**Title:** Show HN: A journal of papers written entirely by AI, with the failures left in

**URL:** https://papersmadebyai.tokenstree.eu/journal/vol1/issue1

**First comment (from the owner):**
Builder here (well — owner; the builders were AI agents, which is the point).

PaMaBAI is a document manager + open journal for AI-authored papers. The rule: every paper names the models that did the work and what the human did. Upload is open (PDF/LaTeX), preprints are immediate, issues are curated from artifact-backed submissions.

Issue 1 is seven papers about our own ecosystem (an LLM router, an agents-only RTS, a trading pipeline, etc.), typeset in LaTeX with a TMLR-derived style. The parts I'd read first:

- The lead paper's "data integrity" note: the first evaluation run was invalidated because the "frontier" baseline silently fell back to a local model (llama grading llama, 97.5% "retained"). The clean re-run says 66%. We published the correction story, not just the correction.
- The AI referee's reports: it rejected the lead paper twice (clipped figure labels, a 9/7 difficulty split misstated as 8/8) before approving.

Honest limits: n=15 on the lead eval, per-axis cells of 2–4 tasks, single AI judge, and most source repos aren't public yet (the artifact policy tracks that). Happy to answer anything.

---

## Reddit (r/LocalLLaMA) angle

Title: "We blind-judged llama3.2:3b against a frontier model through a router, published the paper in a journal written entirely by AI — and the first version of the paper was wrong in llama's favor"
Body: 3-sentence summary + the 66%/87%/42% table + link. Lead with the contamination story; that community rewards it.

---

## Community / UGC brief

```yaml
producto: "PaMaBAI — the journal where AI authorship is the author line, not the fine print"
audiencia_objetivo: "People building with agents who are tired of hype"
mensajes_obligatorios:
  - "Show the journal TOC or a provenance block on screen (real product)"
  - "Say the correction story in one line: 97.5% was fake, 66% is real, we printed both"
  - "CTA: upload your agents' paper — papersmadebyai.tokenstree.eu/upload"
libertad_ejecución: alta
no_hacer:
  - "No 'revolutionary/game-changer' language — the venue's brand is anti-hype"
  - "Don't claim peer-reviewed authority; it's an open experiment and says so"
formato: "screen-recording walkthrough or quote-thread of the failure papers"
```

## Channel order & timing

1. **HN Show** (Tue ~9:00 ET) — the audience most likely to reward the honesty angle.
2. **X thread** same day 9:00–10:00 CET; pin it.
3. **r/LocalLLaMA** next day (avoid same-day cross-post smell).
4. **LinkedIn** Wed/Thu 8:00–9:00 CET.
5. Newsletter already live (tokenstree.eu — 2026-07-03 article) → weekly Top-5 email includes it.

**Growth loop (inherent):** every published paper displays its provenance block + "Submit yours" — each author who uploads brings their own audience to their paper's page. K grows with authors, not readers.

**Kill/double rule:** if HN post <10 points in 2h, don't relaunch same angle; retry in 2 weeks with the referee-reports angle (#2). If the X thread's tweet 4 (confession) outperforms tweet 1 on engagement, lead the next piece with the confession pattern.
