# comp-envs findings (verbatim summary, 2026-07-06)
MEASURED (1000 steps, this box): CartPole-v1 p50 5.45µs; pettingzoo tictactoe 4.22µs; connect_four 15.13µs. AndroidWars (reused same-day data): 21.0ms REST + 2.0s tick.
Thinking-time fraction @3s LLM thinking: in-process 0.0001-0.0005%; AndroidWars request-only 0.69%; avg tick-wait 25.4%; worst-case 40.3% (bound). webDiplomacy deadlines (5min-10d) dwarf all.
Feature table vs TextArena (MIT, in-process, TrueSkill), BALROG (single-agent), Melting Pot (mixed-motive RL, in-process), OpenSpiel (self-play), webDiplomacy/Cicero (persistent, async 5min-10d, negotiation-private only). AndroidWars uniquely combines: persistent world + adversarial + server-enforced fog + REST-first; competitors all in-process libraries except webDiplomacy. All competitor rows REPORTED from docs.
Caveats: competitor features from docs; 3s thinking constant assumption; 40.3% is unlucky-timing bound.
