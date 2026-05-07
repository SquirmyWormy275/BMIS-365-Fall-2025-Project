# Reflection

The Woodchopping Handicap Calculator was the central project of BMIS 365 (Business Application Development) at the University of Montana College of Business in Fall 2025. Across one semester I produced a written project proposal, an interim deterministic implementation (V1), and a final implementation (V2) that combined a cascading historical-data lookup with a local LLM and a Monte Carlo fairness validator. The technical results are documented in `docs/CASE_STUDY.md` and `docs/ARCHITECTURE.md`. This document is an account of what I learned that I expect to carry into work beyond this course.

Three takeaways shape what I would do differently in any future system that combines historical data, learned reasoning, and statistical validation: variance assumption as a structural shift, learned reasoning over per-instance numeric encoding when the underlying physics is high-dimensional, and the discipline of empirical validation when correctness is not provable in closed form.

## Variance assumption as a structural shift

The most important thing I learned this semester was that a system can be wrong because of how it models *uncertainty*, not because of how it models the *expected outcome*.

For about a week in the middle of V2 I believed my prediction pipeline was producing badly biased handicap marks. The Monte Carlo simulator was telling me that the back-marker was winning 31% of races and the slowest competitor was winning 6.7%. I rebuilt the prediction pipeline twice. I added competitor-specific weights. I tweaked the LLM prompt. None of it moved the bias.

The actual cause was in `simulate_single_race`. I had been adding performance noise as a percentage of each competitor's predicted time, which is proportional variance. A 30-second cutter's noise window was half the absolute size of a 60-second cutter's, and the integer-ceiling step in the mark calculation amplified that asymmetry. The fix was a six-line change: sample noise from a fixed `[-3, +3]` second range for every competitor regardless of speed.

The mean had been right the entire time. The shape of the variance was producing the bias.

The general principle I take from this: whenever a system's output looks systematically wrong and the central tendency seems correct, examine the variance model first. The mean is the part you have explicit control over and have carefully designed; the variance is the part you have unconsciously assumed. In retrospect this is obvious, but in the moment it is much easier to interrogate the part of the code you are proud of than the part you wrote without thinking. I now treat the variance assumption (distribution shape, scale, whether it is absolute or proportional, whether it is shared across instances) as a first-class decision that deserves its own justification, not a default carried over from intuition.

This lesson is not specific to handicapping. The same shape of error shows up in price forecasting (proportional volatility versus absolute), in scoring rubrics (relative noise versus absolute), in any system where decisions are made over a population with different scales. The carry-forward is to make the variance model an explicit, named part of any future statistical system I build, with a justification that I could defend to a reviewer.

## Learned reasoning over per-instance numeric encoding when the underlying physics is high-dimensional

V1's wood-index formula was a numeric encoding: a per-species multiplier derived from Janka hardness, shear strength, modulus of rupture, and modulus of elasticity, normalized against Eastern White Pine. It was elegant. It also failed as soon as I tested it on competitors and species I had not specifically tuned around.

The reason was that the encoding flattened qualitatively different physical behaviors into a one-dimensional multiplier. Different species fail under axe in qualitatively different ways: some shatter, some compress, some grain-bind. A multiplier captures none of that. The formula's degrees of freedom were all numeric; the physics it was trying to model were structural.

V2 replaced that with an LLM call. The LLM is given a structured prompt with the species name, the historical baseline times, and the wood quality rating, and returns a multiplier. That multiplier is bounded and falls back to a deterministic curve if the LLM is unavailable. The substantive change is that the *qualitative* knowledge about how species fail under axe is carried implicitly by the LLM's training, rather than being numerically projected by me.

The general principle: use a learned reasoner when the underlying domain is high-dimensional and your numeric encoding is a one-dimensional projection of it. Do not use a learned reasoner when a formula works. The reason to switch was specifically that the formula failed at out-of-distribution generalization, not that LLMs are trendy. The LLM was the right tool for this specific problem; it would have been the wrong tool if my data had been better-distributed across species and competitors.

The carry-forward is two-part. First, I now treat "we have a closed-form formula" as a strength to be preserved when the formula generalizes, and as a constraint to be questioned when it does not. Second, I now expect any LLM integration to come with a deterministic fallback path. Not as a courtesy to offline users but as an architectural discipline that forces me to articulate what the LLM is actually adding over the deterministic baseline. If I cannot articulate it, the LLM should not be there.

## The discipline of empirical validation when correctness is not provable

Handicap fairness has no closed-form definition that can be checked at the level of a single mark assignment. The math involves the joint distribution of all competitors' noisy performance. There is no analytical proof of "these marks are fair." There is only "if we ran this race a quarter-million times, every competitor would win about the same percent of the time."

For most of V1 and the first half of V2 I tried to reason about fairness deductively: tweaking the formula until the marks "looked right." That approach was the source of most of the biased outcomes I shipped before noticing them, because "looked right" is a low-bandwidth measurement.

Building the Monte Carlo simulator changed how I thought about correctness. It turned a deductive question (are these marks fair?) into a measurable one (does this win-rate distribution look uniform?). Once measurement existed, regressions became visible. A broken change to the prediction pipeline produced a visibly biased win-rate plot, which I could see immediately in the simulator output. The simulator was the cheapest piece of infrastructure I built and the highest-leverage one.

The general principle: when a system's correctness cannot be proven analytically, the next investment is measurement infrastructure. Pay the simulation cost (or the test-fixture cost, or the recording-and-replay cost) before paying the cost of debugging without measurement. The discipline is to recognize, early, when you are in a domain where deductive reasoning will not give you correctness (multi-agent simulation, statistical inference, distributed-system concurrency, machine learning) and to budget for measurement instead of trying to reason your way through it.

The carry-forward extends past the project. I now treat "is there a measurement that would have caught this?" as a useful question to ask after any non-trivial bug, and "what is the cheapest measurement that would tell me whether this is correct?" as a useful question to ask before starting any non-trivial system. The Monte Carlo simulator was eight seconds of compute per validation. It was the difference between shipping a system I could reason about and shipping one I could verify.

## Closing

Three habits I leave the semester with: be explicit about variance assumptions before I am explicit about means; reach for learned reasoning only when a formula has demonstrably failed and pair it with a deterministic fallback when I do; and invest in measurement infrastructure when correctness is not provable analytically. Each of these came out of a specific moment in this project where I held a wrong belief for several days before the project itself disproved me. The project is the artifact. The habits are the carry-forward.
