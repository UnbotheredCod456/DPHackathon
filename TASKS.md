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
| **Louis (`UnbotheredCod456`)** | **Track A: AI Engine, Voice & Verification Loop** | `engine.py`, `app.py`, `AGENTS.md` | `main` / `feat/ai-engine` |
| **Collaborator (`pageni`)** | **Track B: 3D Physics Presets, Studio UI & Demo Pitch** | `presets.py`, `static/index.html`, `README.md` | `feat/3d-ui` |

---

## 🧠 Track A Checklist (Louis): Gemini 4 Argon Engine & Autonomous Verification
**Files**: `engine.py`, `app.py`

- [x] Integrate `google-genai >= 2.3.0` **Interactions API** (`client.interactions.create`).
- [x] Set up multi-model choreography:
  - `gemini-3.5-flash-lite` (`thinking_level="low"`) for fast intent routing & FERPA privacy guardrails.
  - `gemini-3.8-flash` (`thinking_level="low"`) for parallel curriculum equations, misconception alerts & student intuition questions.
  - `gemini-4-argon` (`thinking_level="medium"`) for lead 3D Three.js synthesis and multi-turn `previous_interaction_id` refinement.
  - `gemini-3.5-transcribe` & `gemini-3.8-flash-tts` for teacher voice input and 15-second audio narration.
- [ ] **Live Prompt Stress-Testing**: Test 3–5 novel voice prompts with live `GEMINI_API_KEY` (e.g., *3D Ripple Tank Interference*, *Magnus Effect Projectile*, *Rutherford Scattering*) and tune `SYSTEM_PROMPT_3D_ARCHITECT` in `engine.py`.
- [ ] **Autonomous Verification Loop Tuning**: Refine `/api/self-heal` in `engine.py` + `app.py` so any runtime JS error or physics `NaN` reported by the sandboxed iframe is automatically patched by `gemini-4-argon` using `previous_interaction_id`.
- [ ] **Human-in-the-Loop Gate Polish**: Ensure `/api/publish-preview` and `/api/publish-confirm` return clear FERPA/PII audit telemetry for the judges.

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
