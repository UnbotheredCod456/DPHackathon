# AGENTS.md — PhysiCraft Gemini 4 Argon Engineering & Physics Conventions

## 1. Gemini 4 Argon & Interactions API Rules (`google-genai >= 2.3.0`)
- Always use `client.interactions.create(...)` (the **Interactions API**) rather than legacy `generate_content`.
- Pass `thinking_level` (`"low"` | `"medium"` | `"high"`) inside `generation_config`. Never pass deprecated `thinking_budget`, `temperature`, `top_p`, or `top_k` to `gemini-4-argon`.
- Maintain multi-turn stateful 3D scene refinement by passing `previous_interaction_id=interaction.id`.
- Rely on implicit context caching (automatic 95% discount on repeated system instructions and 3D scene context).

## 2. Companion Model Choreography
- **Guardrail & FERPA Privacy Check**: `gemini-3.5-flash-lite` (`thinking_level="low"`) for sub-second classroom safety routing and outbound Google Classroom PII checks.
- **Parallel Curriculum Subagent**: `gemini-3.8-flash` (`thinking_level="low"`) runs concurrently via `asyncio.gather` alongside `gemini-4-argon` so equations, misconception alerts, and student intuition questions arrive with zero added wall-clock latency.
- **Lead 3D Three.js & Physics Solver**: `gemini-4-argon` (`thinking_level="medium"`) synthesizes standalone HTML5 + Three.js scenes with numerical stability guarantees.
- **Voice & Narration**: `gemini-3.5-transcribe` for microphone audio input and `gemini-3.8-flash-tts` (`response_modalities=["AUDIO"]`) for 15-second teacher intuition narration.

## 3. 3D Numerical Physics & Autonomous Verification Loop
- **Singularity Softening**: All inverse-square forces ($1/r^2$) must include a softening factor (`Math.max(1.5, r * r)`) to prevent `NaN` or `Infinity` blowups at small radii.
- **Symplectic / Energy-Preserving Solvers**:
  - Magnetic Lorentz forces ($\vec{F} = q\vec{v} \times \vec{B}$) must use a Boris rotation step so kinetic energy remains strictly constant.
  - Orbital mechanics must use Velocity-Verlet integration so Kepler area sweep rate ($dA/dt = L/2m$) is conserved.
  - Nonlinear coupled oscillators (Double Pendulum) must use 4th-order Runge-Kutta (RK4).
- **Iframe Telemetry Heartbeat**: Every generated 3D simulation posts `physicraft_telemetry` (`fps`, `hasNaN`, `errors`, `energyBounded`) once per second to the parent window. Any `NaN` or runtime error automatically triggers `/api/self-heal` with `previous_interaction_id`.
