# Facilitator runbook — AI → ML → LLMs (Reveal deck)

**Open the deck locally:** from `presentations/ai_ml_journey/`, run `python3 -m http.server` (pick any free port) and open `http://127.0.0.1:<port>/index.html` so asset paths resolve correctly.

This file is the **only** place for wall-clock pacing, break suggestions, and contingency notes. Slides intentionally avoid timers and session-length callouts.

## Suggested flow (full workshop)

Order on the deck: **Hook → Lab A → AI (Ch.2) → ML (Ch.3) → Deep learning (Ch.4) → Generative AI (Ch.5) → LLMs (Ch.6) → Lab C (tokenizer) → Bridge → Lab D (embeddings) → Lab E (self-attention) → Capstone.**

- **Morning block:** Hook through Lab A and the ML chapter (or into the deep-learning intro), depending on group speed. Build vocabulary on “rules vs data” before code.
- **Lab A (in-deck):** Learners use **two “Sort on screen” slides** (part 1: scenarios 1–4, part 2: 5–7). The progress bar and **Clear picks** stay in sync across both. Budget ~6–8 minutes total for pairs, then **one** full-group pass comparing disagreements before opening the **“Debrief”** `<details>` blocks. Clicks on those controls are wired so they do not advance Reveal accidentally.
- **Short break** after a natural lab close (not printed on slides).
- **Afternoon block:** Labs C–E in `day1_building_transformer/` with live demos; capstone nesting as the closing frame.

## Optional shorten paths

- **Tight on time:** Shorten Lab A discussion; trim one generative-AI or LLM vertical instead of rushing the code labs.
- **Defer advanced code:** Run Lab C (tokenizer) fully; summarize embeddings (Lab D) with one matrix inspection; demo attention (Lab E) from facilitator machine only.
- **Non-coders in the room:** Emphasize Lab A and the concept chapters; pair each table with one driver for Labs C–E while others observe and take notes.

## Prerequisites

- Python 3, `numpy`, a code editor, terminal.
- Clone this repo; confirm `day1_building_transformer/` imports work from the paths you use (`cd day1_building_transformer` vs repo root and `PYTHONPATH`).

## Room logistics

- Decide early: **one shared demo** vs **everyone runs locally**. For everyone-local, budget setup time before Lab C.
- Pre-flight: run `tokenizer/simple_tokenizer.py` (or import `Tokenizer`) on a quirky sentence with punctuation and mixed case.

## Troubleshooting (code labs)

- **Import errors:** run modules from the directory that contains the package, or set `PYTHONPATH` to the repo root.
- **Encoding / weird characters:** pick test sentences that include quotes, URLs, and emoji to surface tokenizer edge cases.
- **NumPy shape errors in attention steps:** re-check sequence length, batch dimension, and that Q/K/V share the same embedding dimension before matmuls.

Speaker notes in the deck may say “see FACILITATOR.md” without quoting minutes on screen.

## Media & offline check

- **Vendored assets:** Before presenting offline or from a USB copy, confirm the folder `presentations/ai_ml_journey/assets/images/` exists and contains the images referenced from `index.html` (see **`ATTRIBUTIONS.md`** for the authoritative list, licenses, and source URLs).
- **Total size:** As vendored, media is about **1.4 MB** in `assets/images/` (JPEGs dominate); acceptable for laptops; avoid adding huge GIFs without compressing or converting to video first.
- **Reduced motion:** If anyone uses **Reduce motion** in macOS / Windows accessibility settings, the deck swaps configured GIFs to still alternatives and tones down CSS motion (`deck.css` + script in `index.html`). Mention verbally that stock loops are illustrative, not factual diagrams.
- **Swapping images:** If you replace a file, update **`ATTRIBUTIONS.md`** with filename, author, license, source URL, and retrieval date so the workshop stays license-safe.
