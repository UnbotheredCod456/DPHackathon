# 🤝 PhysiCraft Team Task Split & Collaborator Guide

Welcome! To prevent Git merge conflicts and move fast during the hackathon, we have divided the codebase into two zero-overlap tracks.

---

## ⚡ 1-Minute Setup for Collaborators

```bash
# 1. Pull latest main
git pull origin main

# 2. Create virtual environment & install dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Copy .env.example -> .env and add GEMINI_API_KEY (or paste it in the UI top-right button)
cp .env.example .env

# 4. Run the server
.venv/bin/uvicorn app:app --reload --host 127.0.0.1 --port 8000
```
Then open **http://127.0.0.1:8000**.

---

## 🗂️ File Ownership Boundaries (Zero Merge Conflicts)

| Team Member | Track | Owned Files | Git Branch |
|---|---|---|---|
| **Louis (`UnbotheredCod456`)** | **Track A: AI Engine, Voice & Verification Loop** | `engine.py`, `app.py`, `subagent_simulations.py`, `subagent_verifier.py`, `subagent_ferpa_gate.py`, `test_track_a.py`, `AGENTS.md` | `main` / `feat/ai-engine` |
| **Collaborator (`pageni`)** | **Track B: 3D Physics Presets, Studio UI & Demo Pitch** | `presets.py`, `static/index.html`, `README.md` | `feat/3d-ui` |

---

## 🧠 Track A Checklist (Louis): Gemini 4 Argon Engine & Autonomous Verification
**Files**: `engine.py`, `app.py`, `subagent_simulations.py`, `subagent_verifier.py`, `subagent_ferpa_gate.py`, `test_track_a.py`

- [x] Integrate `google-genai >= 2.3.0` **Interactions API** (`client.interactions.create`).
- [x] Set up Central Lead Agent (`gemini-4-argon` `thinking_level="high"`) + 3 Parallel Subagents (`gemini-4-argon` `thinking_level="medium"`) + Companion Models:
  - **Central Lead Coordinator**: `gemini-4-argon` (`thinking_level="high"`) with `<10s` Voice-to-3D SLA enforcement.
  - **Subagent 1 (`subagent_simulations.py`)**: `gemini-4-argon` (`thinking_level="medium"`) for <10s Voice-to-3D physics animations (including Flagship **Magnetic Flux $\Phi_B = B \cdot A \cdot \cos\theta$ & Faraday's Law**, **Rutherford Alpha Coulomb Scattering**, **3D Ripple Tank Waves**, **3D Magnus Projectile**, and `<1s` `previous_interaction_id` multi-turn refinements).
  - **Subagent 2 (`subagent_verifier.py`)**: `gemini-4-argon` (`thinking_level="medium"`) for static AST & numerical physics verification (auto-patching `1/r^2` singularities with `Math.max(1.5, r * r)` and 1Hz `physicraft_telemetry` injection).
  - **Subagent 3 (`subagent_ferpa_gate.py`)**: `gemini-3.5-flash-lite` (`thinking_level="low"`) + `gemini-4-argon` (`thinking_level="medium"`) escalation + deterministic regex PII redaction (`[REDACTED_STUDENT_PII]`).
  - **Companion Models**: `gemini-3.8-flash` (`thinking_level="low"`), `gemini-3.5-transcribe`, and `gemini-3.8-flash-tts`.
- [x] **Live Prompt Stress-Testing & <10s Voice-to-3D SLA**: Verified spoken teacher prompts (*Magnetic Flux & Faraday's Law*, *Rutherford Alpha Scattering*, *3D Ripple Tank Interference*, *Magnus Effect Projectile*) and multi-turn `previous_interaction_id` refinements.
- [x] **Autonomous Verification Loop Tuning**: Verified `/api/self-heal` in `subagent_verifier.py` + `engine.py` + `app.py` so any runtime JS error or physics `NaN` is deterministically and/or Argon-repaired with `previous_interaction_id`.
- [x] **Human-in-the-Loop Gate Polish**: Verified `/api/publish-preview` and `/api/publish-confirm` with automatic PII redaction (`[REDACTED_STUDENT_PII]`), OAuth scope transparency, and explicit teacher confirmation.

---

## 🎨 Track B Checklist (Collaborator `pageni`): 3D Presets, UI UX & Live Pitch
**Files**: `presets.py`, `static/index.html`, `README.md`

- [ ] **Add Hero Preset #4 in `presets.py`**:
  - Add a `"waves"` (3D Two-Source Ripple Tank Wave Interference) or `"rutherford"` (3D Alpha Particle Coulomb Scattering) entry to the `PRESETS` dictionary in `presets.py` and add its quick-select button in `static/index.html`.
  - Keep the `window.parent.postMessage({ type: "physicraft_telemetry", ... }, "*")` heartbeat inside `animate()` so the green verification badge stays active!
- [ ] **Add "Projection / Student Mode" Toggle in `static/index.html`**:
  - Add a toggle button in the left panel that hides the Teacher Cheatsheet & reveals interactive multiple-choice or expandable hints for the 3 Student Intuition Questions so Sarah can project the screen to her class.
- [ ] **Visual Architecture Diagram Modal in `static/index.html`**:
  - Add an interactive "Architecture" modal showing how `gemini-4-argon` orchestrates `gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-3.5-transcribe`, and `gemini-3.8-flash-tts` so we can show judges the system pipeline in one click.
- [ ] **90-Second Backup Video & 3-Minute Pitch Rehearsal**:
  - Record a safety screen capture of the 3D presets, voice generation, self-heal loop, and Google Classroom approval gate.
