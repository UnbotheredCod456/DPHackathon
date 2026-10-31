# ⚛️ PhysiCraft: Voice-to-3D AP Physics Lab Builder

Built with **Gemini 4 Argon (`gemini-4-argon`)** and companion models (`gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-3.5-transcribe`, `gemini-3.8-flash-tts`) on the **Interactions API**.

---

## 🚀 Quick Start

```bash
# 1. Start the server (already running on port 8000!)
.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```
Open **http://127.0.0.1:8000** in your browser.

---

## 🏆 3-Minute Live Judging Script (Step-by-Step)

### Minute 0:00 – 0:40 | The Hook & Hero Demo #1 (Lorentz Force Spiral)
1. **Say**: *"Meet Sarah, an AP Physics teacher. When she tries to draw a 3D magnetic Lorentz force spiral on a flat 2D whiteboard, half her class loses intuition on the right-hand rule. Writing Three.js takes hours she doesn't have. With PhysiCraft, Sarah speaks her lesson and gets a verified, interactive 3D physics lab in seconds."*
2. Show the **🧲 Lorentz** preset running at 60 FPS:
   - Orbit the 3D camera with your mouse.
   - Click **Electron (-q)** vs **Proton (+q)** to show the spiral chirality (handedness) flip instantly while the cyan velocity ($\vec{v}$) and magenta force ($\vec{F}$) vectors stay perpendicular.
   - Click **🔊 15s Audio Guide** (`gemini-3.8-flash-tts`) to play Sarah's classroom narration.

### Minute 0:40 – 1:30 | Hero Demo #2 & #3 (Kepler's 2nd Law & Chaos Theory)
1. Click **🪐 Kepler**:
   - Point out the alternating cyan and amber **Equal-Time Area Wedges** ($\Delta A / \Delta t = \text{constant}$) proving conservation of angular momentum in 3D.
   - Click **Crank Gravity (Crash!)** to show the planet spiral into the star when gravity overcomes angular momentum.
2. Click **🦋 Chaos (Double Pendulum)**:
   - Show the **two coupled pendulums** starting just $0.05^\circ$ apart—moving identically for 4 seconds before diverging wildly (the Butterfly Effect).

### Minute 1:30 – 2:20 | Live Voice-to-3D + Multi-Turn `previous_interaction_id`
1. Click **🎤 Speak Lesson** (or type a custom prompt) and click **✨ Build 3D Lab (Argon)**.
2. Point out the **Model Choreography Strip** in the top bar:
   - `gemini-3.5-flash-lite` checks safety & domain in ~150ms.
   - `gemini-3.8-flash` (curriculum subagent) and `gemini-4-argon` (`thinking_level="medium"`, 3D solver architect) run in parallel via the **Interactions API**.
3. Use the **Follow-up Edit bar** (`previous_interaction_id`) to refine the scene state without starting over.

### Minute 2:20 – 3:00 | Autonomous Verification Loop & Human-in-the-Loop Gate
1. **Autonomous Verification Loop (Judge Test #2)**:
   - Point to the green **Verified: 60 FPS • 0 NaN • Bounded** badge receiving live telemetry from the sandboxed iframe.
   - Click **Test Self-Heal** to inject a singularity fault and watch `gemini-4-argon` automatically patch the simulation!
2. **Human-in-the-Loop Control (Judge Test #3)**:
   - Click **🎓 Assign to Class** in the top right.
   - Show the **Human-in-the-Loop Approval Modal** where `gemini-3.5-flash-lite` audits the payload for FERPA/student PII compliance before Sarah explicitly approves pushing the assignment to her 28 students in Google Classroom.
