# Woodchopping Handicap Calculator

An objective handicap system for competitive woodchopping that combines historical performance data, local LLM reasoning, and Monte Carlo simulation to produce verifiably fair race marks.

## Overview

In handicap woodchopping, every competitor in a heat is given a head-start (a "mark") so that, if the math is right, all competitors finish at roughly the same instant. Australia and New Zealand have refined the practice over 150 years using subjective judgment by appointed handicappers. The United States has no equivalent system, which means mid-tier competitors compete at a structural loss for years and top-tier competitors face no incentive to push themselves.

This project computes those marks objectively. It takes a competitor's historical times, the wood species and block diameter for the upcoming heat, and a 0 to 10 wood quality rating, and produces a start mark for each competitor in the heat. The prediction pipeline blends three layers: a cascading historical-data lookup that handles sparse training data, a local LLM (qwen2.5:7b via Ollama) that reasons about how wood quality should adjust the predicted time, and a Monte Carlo simulator that runs 250,000 races to verify whether the resulting marks actually produce equal win probability across all competitors.

The version in this repository is the final coursework deliverable for BMIS 365 (Business Application Development) at the University of Montana College of Business, Fall 2025. It runs as a Python CLI against an Excel workbook of competitor and wood data and is fully offline. No cloud LLMs, no API keys, no SaaS dependencies.

## What it does

- Loads a roster of competitors from an Excel workbook and lets a judge select competitors for the current heat.
- Configures the heat's wood characteristics (species, block diameter in mm, quality rating 0 to 10) and event type (Standing Block or Underhand).
- Predicts each competitor's finish time for the configured wood by combining historical results with LLM-based quality reasoning. If a competitor has no times for the exact species, the prediction falls back through three tiers: competitor + species + event, then competitor + event, then event-wide baseline.
- Calculates handicap marks per Australian Axemen's Association (AAA) rules: slowest predicted competitor gets a 3 second mark; everyone else gets `3 + ceil(slowest_time - their_time)` seconds; clamped to [3, 180].
- Validates fairness via Monte Carlo simulation. 250,000 simulated races with absolute ±3 second performance variance produce per-competitor win probability, average finish position, and a fairness rating from the LLM.
- Persists heat results back to Excel so the historical data improves over time.

## Tech stack

**Language / runtime**: Python 3.10+

**Data and numerics**: pandas, numpy, openpyxl, matplotlib

**Local LLM**: Ollama, model `qwen2.5:7b`. Chosen because it is optimized for mathematical reasoning and runs entirely on a laptop. No tokens, no rate limits, no network.

**Persistence**: Excel (`woodchopping.xlsx`), three sheets: `Competitor`, `wood`, `Results`. Excel was chosen over SQLite because the actual end users (event judges) are comfortable opening spreadsheets and not comfortable with database tools. Auditability and editability mattered more than performance.

**Validation**: custom Monte Carlo simulator (250,000 race iterations per validation) using numpy for sampling.

**Interface**: terminal / CLI.

## Quickstart

```powershell
# 1. Clone the repo
git clone <repo-url>
cd <repo-folder>

# 2. Create and activate a virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install and start Ollama (https://ollama.com), then pull the model
ollama pull qwen2.5:7b
ollama serve   # leave running in a separate terminal

# 5. Run the V2 application
cd project-deliverable-2
python DeliverableTwo.py
```

You will see the welcome screen and a 7-option main menu. A typical first session: option 1 to select competitors, option 2 to set wood characteristics, option 3 to pick the event (SB or UH), option 4 to view the calculated marks and optionally run the Monte Carlo simulation.

### Configuration

Ollama host and model are configurable at runtime via environment variables and have working defaults baked in. Override only if you run Ollama on a non-default host or want to swap models.

```powershell
$env:OLLAMA_HOST  = "http://localhost:11434"
$env:OLLAMA_MODEL = "qwen2.5:7b"
```

## Project evolution

This repo is the deliverable trail of a single course project. Each phase is preserved in its own folder so the problem-solving arc is visible.

| Phase | Folder | What this is |
| --- | --- | --- |
| 1 | [`project-proposal/`](./project-proposal) | The initial project proposal: problem framing, scope, value proposition. Written before any code. |
| 2 | [`project-deliverable-1/`](./project-deliverable-1) | V1 implementation. A purely deterministic handicap calculator: a hand-built wood-index formula combining size, quality, and species characteristics (Janka hardness, shear, MOR, MOE) to scale historical times. Worked well for the original roster, generalized poorly to new competitors. |
| 3 | [`project-deliverable-2/`](./project-deliverable-2) | V2 implementation, final deliverable. Replaces the deterministic formula with a cascading lookup plus LLM-assisted quality reasoning. Adds Monte Carlo fairness validation, the Underhand event, results persistence, and a richer competitor management workflow. |

The most consequential discovery between V1 and V2 was about variance. Early V2 used proportional variance (each competitor's predicted time wobbled by ±X% of itself) and produced badly biased outcomes. Front-mark competitors won 31% of simulated races while back-mark competitors won 6.7%. Switching to absolute variance (every competitor's time wobbles by ±3 seconds in absolute terms) produced near-equal win probability across all skill levels, because real-world factors (technique consistency, wood grain variation, equipment) actually do affect competitors equally in absolute terms, not proportionally. That single change is the cleanest piece of engineering in the repo and is documented in detail in [`docs/CASE_STUDY.md`](./docs/CASE_STUDY.md).

## Architecture

A two-file CLI: `DeliverableTwo.py` is the menu loop and main-state holder, `ProjectFunctions.py` is everything else. `woodchopping.xlsx` is the persistence layer with three sheets: `Competitor` (the roster), `wood` (species characteristics), `Results` (every recorded heat time). The prediction pipeline is in `predict_competitor_time_with_ai`, the Monte Carlo simulator is in `run_monte_carlo_simulation`, and the LLM bridge is `call_ollama`. See [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) for the full breakdown.

## Documentation

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md): system overview, data model, prediction pipeline, validation pipeline, failure modes.
- [`docs/CASE_STUDY.md`](./docs/CASE_STUDY.md): problem framing, the V1 to V2 redesign, the variance discovery, what I would do differently.
- [`docs/REFLECTION.md`](./docs/REFLECTION.md): academic reflection on the course project. What I learned about planning, scaffolding, and integrating an LLM into a deterministic system.

## My role

Solo developer. I designed the data model, built both V1 and V2, integrated Ollama, designed the variance model, wrote the Monte Carlo simulator, and produced all documentation. Two acknowledged contributions:

- A professional engineer I consulted with helped me reason about how axe behavior varies with wood density, Janka hardness, and shear force. That conversation produced the rough physical model that became V1's wood-index formula.
- David Moses Jr., my coach in the sport, reviewed V2's outputs against his own intuition for the discipline and recommended weighting recent times more heavily for older competitors whose careers peaked decades ago. That feedback is captured as future work in `docs/CASE_STUDY.md`.

I want to be precise about scope: this version uses LLM reasoning and Monte Carlo simulation. It does not use a trained machine-learning model. Earlier explorations of an XGBoost-based triple-prediction model existed but are not included in this repository.

## Project context

- **Course**: BMIS 365, Business Application Development, Fall 2025.
- **Institution**: University of Montana College of Business.
- **Submission scope**: 3 deliverables (proposal, V1, V2). All preserved in this repo.
- **Sport context**: I compete in timbersports. The Missoula Pro-Am and Mason County Western Qualifier may feature handicap races in the upcoming season; this tool is being evaluated for use at those events.

## License

MIT. See [`LICENSE`](./LICENSE).
