# Case study: Woodchopping Handicap Calculator

## Context

I built this for a one-semester course at the University of Montana, BMIS 365 (Business Application Development), Fall 2025. The deliverable was three artifacts: a written project proposal, an interim implementation, and a final implementation. I picked the problem because I compete in the sport of woodchopping and there is no objective handicap system anywhere in the United States. The lack of one is structurally bad for the sport: mid-tier athletes compete at a financial loss for years before improving, top-tier athletes face no incentive to push themselves, and there is no way to attract spectators with the kind of upset wins that drive crowds in Australia and New Zealand.

By the end of the semester I had a working CLI that combined a cascading historical-data lookup, a local LLM (qwen2.5:7b via Ollama) for wood-quality reasoning, and a Monte Carlo simulator that ran 250,000 races to verify fairness. The codebase was about 2,600 lines across ~30 documented functions in two files. The most important single result was a piece of statistical knowledge: switching from proportional performance variance to absolute variance changed the win-rate spread in simulated races from 31% / 6.7% to roughly equal probability across all competitors. That discovery was the difference between a system that produced biased races and one that produced fair ones.

## Constraints

**Timeline**: about fourteen weeks from proposal to final deliverable. Iteration was bounded by the course's three-deliverable structure.

**Team**: solo. I consulted with a professional engineer for the wood-physics framework that became V1's formula and with my coach David Moses Jr. for sport-domain validation, but all design and implementation was mine.

**Scope**: the system had to handle competitor management, wood configuration, mark calculation, and (eventually) results persistence, for at minimum the Standing Block and Underhand events. The 3-Board Jigger was explicitly out of scope due to data sparsity.

**Platform**: had to run on a judge's personal laptop at a tournament. That ruled out cloud LLMs (no reliable Wi-Fi), SaaS dependencies (no monthly subscription a club can justify), and anything requiring a database server. The deployment target was "open the laptop, double-click, run a heat."

**Stakeholders**: actual end users would be event judges, who are skilled in the sport but not in software. The interface had to be navigable without reading documentation. The data layer had to be inspectable without SQL.

**Self-imposed constraint**: every prediction had to be explainable. A judge handing a back-marker a 47-second mark needed to be able to say *why*, including which races the prediction was based on. Black-box outputs were not acceptable.

## Key technical decisions

### 1. LLM-assisted prediction over a rigid formula

**Situation.** V1 used a hand-built formula: a wood-index composed of a size factor, a quality multiplier (1.20 at quality 0 down to 0.80 at quality 10), and a species multiplier derived from Janka hardness, shear strength, MOR, and MOE relative to Eastern White Pine. The formula performed well on the original roster but degraded as soon as I added competitors I had not specifically tuned the system around.

**Decision.** For V2 I replaced the formula with a two-step pipeline: a deterministic median over historical times, then a local LLM that reasoned about how the wood characteristics for the specific block should adjust that median.

**Rationale.** The wood-index formula's weakness was that it needed every species to fit the same mathematical shape. In reality, different species fail under axe in qualitatively different ways: some shatter, some compress, some grain-bind. A multiplier captures none of that. Encoding it numerically would have meant per-species tuning constants that would never scale to species I had no data for. An LLM prompted with the species name and a historical baseline could carry that qualitative knowledge implicitly without me hand-encoding it.

**Lesson.** Use a learned model when the underlying physics is high-dimensional and your formula is a one-dimensional projection of it. Don't use a learned model when a formula works. The reason to swap was specifically that the formula failed at out-of-distribution generalization, not that LLMs were trendy.

### 2. Monte Carlo validation rather than trusting the calculation

**Situation.** Even after the prediction pipeline produced sensible-looking marks, I had no way to know whether the resulting race would actually be fair. A handicap is fair if and only if every competitor wins about the same percentage of the time. There is no closed-form way to verify that. The math involves the joint distribution of all competitors' noisy performance.

**Decision.** I built a Monte Carlo simulator that runs 250,000 races for any given mark assignment and reports per-competitor win rate, average finish position, and finish-time spread. Every set of marks the system computes can be optionally validated by simulation before being used.

**Rationale.** The simulator turned an opaque correctness question ("are these marks fair?") into a measurable one ("does this distribution look uniform?"). It also gave me a regression test: a broken change to the prediction pipeline produced visibly biased win-rate plots, which I could see immediately. It cost roughly eight seconds of compute per validation, which is acceptable given that judges run it once per heat.

**Lesson.** When you cannot prove a system is correct analytically, pay the simulation cost to measure it empirically. The simulator was the cheapest piece of infrastructure I built and the highest-leverage one. It also turned the hardest question in the project ("am I being fair?") into something I could answer with a histogram.

### 3. Absolute performance variance over proportional variance

**Situation.** Early Monte Carlo runs were giving me badly biased outcomes. In one configuration the back-marker was winning 31% of races and the slowest competitor was winning 6.7%. I assumed my marks were wrong. I rebuilt the prediction pipeline twice trying to fix it.

**Decision.** I changed the variance model. The original simulator added performance noise as a percentage of each competitor's predicted time (proportional variance). I changed it to add noise as an absolute number of seconds, sampled from `[-3, +3]` for every competitor regardless of their speed.

**Rationale.** The cause of the bias was not the prediction; it was the variance assumption. A faster competitor's proportional noise was a smaller absolute window than a slower competitor's, and the integer-ceiling in the mark calculation amplified the difference. More importantly, the proportional model was just *physically wrong*. The things that actually make a real race noisy (technique inconsistency, wood grain, equipment slip) are roughly constant in seconds, not in percent. A 30-second cutter and a 60-second cutter both have approximately the same range of "good day vs bad day."

**Lesson.** When a system seems unfair, suspect your variance model before suspecting your mean. The mean is usually the part you have explicit control over and have carefully designed; the variance is the part you have unconsciously assumed away. The fix here was a six-line change in `simulate_single_race`. Identifying it took a week.

### 4. Cascading fallback over hard "insufficient data" failures

**Situation.** A real competitor's history is sparse. They might have ten races on Tasmanian Bluegum but zero on Silver Birch. A naïve system would refuse to predict for the species the competitor has never cut, which is exactly the case where the judge needs help most.

**Decision.** `get_competitor_historical_times_flexible` and `get_event_baseline_flexible` implement a three-tier cascade. The system first tries `competitor + species + event`; if fewer than three matches exist it broadens to `competitor + event` (any species); if still empty it falls through to an event-wide baseline. The function also returns a human-readable `data_source` string that travels with the prediction so the judge sees what they are looking at.

**Rationale.** The system is most useful in the data-sparse case. Refusing to operate there would defeat the project's value proposition for novice competitors and travelling competitors. The cost of being wrong with a fallback prediction is bounded by the explicit "low confidence" label that travels with it.

**Lesson.** Your fallback path is part of your product. Design it as carefully as the happy path, and make the data-source provenance visible to the user.

### 5. Excel as data store

**Situation.** I needed persistence for the competitor roster, wood characteristics, and historical results. The technically correct answer was SQLite or even a small Postgres instance.

**Decision.** I chose Excel. Three sheets in `woodchopping.xlsx`: `Competitor`, `wood`, `Results`. Reads via `pandas.read_excel`; writes via `openpyxl`.

**Rationale.** The actual users were not me. They were event judges who are not database administrators. Judges already use spreadsheets for scoring; asking them to install a database tool would have made the system less likely to be used, not more. Excel also gave them an inspection and audit interface for free: when something looks wrong, they can open the file and see exactly what is in it. The cost was concurrency safety (two open files = silent overwrite), which I documented in `docs/ARCHITECTURE.md` as a known failure mode rather than a correctness issue.

**Lesson.** Pick the persistence layer your *users* can audit, not the one your résumé wants. The right answer for a tournament judge in a barn in western Montana is not the right answer for a SaaS startup.

## What I would do differently

The largest single regret is that I did not write any automated tests. I tested by hand throughout the semester, and the Monte Carlo simulator served as a passable end-to-end regression check (biased outputs were visible in the win-rate plots) but I have no `pytest` suite. A prediction-pipeline change today could silently break the cascading fallback ordering and I would only notice the next time I ran a simulation. Were I to start V2 over, the first thing I would write would be unit tests on the deterministic paths in `predict_competitor_time_with_ai`, `compute_marks`, and `simulate_single_race`, and a stub for `call_ollama` so the LLM-dependent paths could be exercised offline. That would have taken less than a day and saved me roughly that much in debugging across the semester.

The second regret is that the LLM `confidence_level` strings (`high`, `medium`, `low`) are nominal, derived from data-source breadth rather than from calibrated prediction error. A competitor with three exact-match races on the same wood block could still have wildly variable real-world performance, and the system would call that `high`-confidence. The honest fix is hold-out validation: predict the most recent N races per competitor against held-out training data, bin observed error, and label confidences from that. I had the data; I did not have time.

The third regret is that all the magic numbers (±3 seconds variance, 180-second cap, 3-second floor, baseline diameters, LLM `temperature=0.3`) are encoded inline in the functions that use them. They should live in a single `config` module so they are inspectable, overridable, and changeable as a unit. This is a thirty-minute refactor that I deferred and have not done.

The fourth regret is the absence of recency weighting on historical times. David Moses Jr. flagged this in feedback: an older professional whose career peaked decades ago carries historical times that are no longer representative. The current median treats all historical times equally. The fix is exponential decay weighting on race date, with the half-life as a tunable parameter. I have a clear specification but no implementation.

## Outcomes

The system shipped as the final deliverable for BMIS 365 and is the version preserved at `project-deliverable-2/` in this repository. Specific results:

- **2,600 lines of code** across two Python files. ~30 documented functions.
- **Three preserved phases** (proposal, V1, V2) showing the engineering arc of the semester.
- **Variance discovery**: identified that absolute (not proportional) performance variance is the fair-race assumption, with a measurable improvement from a 31% / 6.7% win-rate spread to roughly uniform per-competitor probability.
- **Validation harness**: 250,000-race Monte Carlo simulation per heat, with LLM-assisted fairness assessment and deterministic fallback.
- **Fully offline**: no cloud APIs, no third-party services, no API keys.
- **Demonstrated to the sport community**: my coach has reviewed the outputs against domain intuition. The Missoula Pro-Am and Mason County Western Qualifier are evaluating the tool for handicap races in the upcoming season.

The system is not yet adopted in production. It is a candidate that needs the test suite, the recency weighting, and the calibrated confidences before I would put it in front of an actual handicapper at an actual tournament. That work is articulated as a clear roadmap in `docs/ARCHITECTURE.md`.
