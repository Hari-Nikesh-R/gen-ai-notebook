# Day 4 Presentation Decks & Central Launch Portal

This directory contains the split, interactive slide presentations and a central landing portal for **Day 4: Beyond LLMs — RAG & Agentic AI**.

---

## 🌟 The Architecture

Instead of a single heavy presentation, the curriculum is divided into a sleek, modular presentation ecosystem:

1. **Central Launch Portal (`index.html`)**: A premium, state-of-the-art glassmorphic hub styling with harmonized gradient borders, dynamic floating backdrop orbs, and scale transitions. It serves as the entryway to launch either presentation.
2. **RAG Foundations Presentation (`rag.html`)**: A dedicated Reveal.js slide deck focusing on vector databases, sentence similarity math, chunking strategies, and an **interactive, vertical step-by-step code sync simulator** (Slide 7) syncing python source code with pipeline nodes.
3. **Agentic AI Presentation (`agent.html`)**: A dedicated Reveal.js slide deck focusing on planning models (ReAct), agent memory caches, API tools, multi-agent dev team setups, and risk guardrails.

---

## 🚀 How to Run

Since all Reveal.js dependencies are loaded directly via secure, high-performance CDNs, you can run the presentations in two simple ways:

### Method A: Double-Click (Local Browser)
Simply double-click [index.html](file:///Users/harinikesh/Downloads/Project/gen-ai-notebook/day4_beyond_llm/presentation/index.html) to open the premium central portal in your default web browser, and choose your learning track!

### Method B: Local HTTP Server (Recommended)
To enable clean, standard URL hashing and prevent potential CORS warnings in some browsers, run a simple local web server in this directory:

```bash
# Using Python 3
python -m http.server 8000
```
Then, navigate your browser to `http://localhost:8000`.

---

## 🎮 Presentation Controls

Reveal.js supports quick navigation shortcuts out-of-the-box:

*   **`Space` or `→`**: Advance to the next slide (or trigger a vertical execution step on the interactive RAG Code Flow slide).
*   **`Shift + Space` or `←`**: Go backward.
*   **`ESC` or `O`**: Toggle grid overview mode to jump between section slides.
*   **`F`**: Enter fullscreen mode.
*   **`S`**: Open presenter view window (showing slide timers and lecture notes).
*   **Floating Button (`⬅ Back to Portal`)**: Click the absolute overlay button at the bottom-left of any slide to instantly return to the central portal page.

---

## 📁 File Structure

```text
presentation/
├── index.html        # Central Launch Portal
├── rag.html          # RAG Foundations presentation (10 slides)
├── agent.html        # Agentic AI presentation (8 slides)
├── deck.css          # Customized global presentation & portal styles
└── README.md         # This execution & setup guide
```
