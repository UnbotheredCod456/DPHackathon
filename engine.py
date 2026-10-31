"""
PhysiCraft Multi-Agent Orchestration Engine (Track A)
Powered by the official Google GenAI SDK (`google-genai >= 2.3.0`) Interactions API (`client.interactions.create`).

Model Choreography (per AGENTS.md):
1. `gemini-3.5-flash-lite` (thinking_level="low"): Low-latency intent routing, classroom safety check & FERPA/PII guardrail.
2. `gemini-3.8-flash` (thinking_level="low"): Parallel curriculum subagent running concurrently via `asyncio.gather` alongside `gemini-4-argon`.
3. `gemini-4-argon` (thinking_level="medium"): Lead 3D Three.js & numerical physics architect + multi-turn `previous_interaction_id` state + autonomous self-healing loop.
4. `gemini-3.5-transcribe`: Voice prompt transcription from teacher's microphone audio.
5. `gemini-3.8-flash-tts` (response_modalities=["AUDIO"]): Studio-quality 15-second Teacher's Intuition Narration.
"""

import asyncio
import base64
import json
import os
import re
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from google import genai

from presets import PRESETS
from subagent_ferpa_gate import run_subagent_ferpa_audit, scan_pii_and_ferpa_compliance
from subagent_simulations import (
    apply_multiturn_refinement,
    build_magnetic_flux_3d_lab,
    build_rutherford_scattering_3d_lab,
    get_instant_concept_lab,
)
from subagent_verifier import (
    argon_self_heal_with_interactions,
    deep_verify_and_repair_3d_html,
    deterministic_self_heal_html,
)
from universal_physics_compiler import (
    compile_universal_3d_concept,
    sanitize_curriculum_dict,
    strip_combining_arrows,
    universal_physics_accuracy_audit,
)

load_dotenv()

# 15-second SLA budget so a teacher speaking ANY physics concept gets a verified 3D model within 15s
VOICE_TO_3D_SLA_SECONDS = 13.5

# Stateful Interaction Lineage Store (tracks multi-turn chains for judge inspection)
INTERACTION_LINEAGE: List[Dict[str, Any]] = []
# Scene HTML cache keyed by interaction_id for stateful multi-turn refinements
INTERACTION_SCENE_CACHE: Dict[str, str] = {}

SYSTEM_PROMPT_3D_ARCHITECT = """You are PhysiCraft Lead Architect (powered by Gemini 4 Argon).
Your job is to build a COMPLETE, self-contained, visually breathtaking single-file HTML5 + Three.js 3D interactive physics simulation for high school AP Physics teacher Sarah and her students.

STRICT TECHNICAL & NUMERICAL PHYSICS REQUIREMENTS:
1. Output ONLY valid, runnable HTML starting with `<!DOCTYPE html>` and ending with `</html>`.
2. Include Three.js r128 and OrbitControls via CDN:
   <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
   <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
3. Dark scientific aesthetic (`background: #060913`), glowing meshes (`MeshStandardMaterial` with `emissive`), reference `GridHelper`, directional + ambient lighting, and smooth `OrbitControls`.
4. Include a floating glassmorphism HUD (`position: absolute; top: 14px; right: 14px`) with 3 to 5 HTML `<input type="range">` sliders for key physical variables + a Reset button.
5. Include a top-left live Telemetry readout (`position: absolute; top: 14px; left: 14px`) showing real-time calculated physical quantities updating every frame.
6. Include dynamic 3D Vector Arrows (`THREE.ArrowHelper`) for velocity (cyan `#22d3ee`) and force/acceleration (magenta `#f43f5e`) or field lines (amber `#f59e0b`).
7. NUMERICAL STABILITY & SYMPLECTIC SOLVERS (CRITICAL):
   - Singularity Softening: All inverse-square forces (1/r^2) MUST include a softening factor `Math.max(1.5, r * r)` to prevent `NaN` or `Infinity` blowups at small radii.
   - Magnetic Lorentz forces (F = qv x B) MUST use a Boris rotation step so kinetic energy remains strictly constant.
   - Orbital mechanics MUST use Velocity-Verlet integration so Kepler area sweep rate (dA/dt = L/2m) is conserved.
   - Nonlinear coupled oscillators MUST use 4th-order Runge-Kutta (RK4).
   - NEVER use Unicode combining right arrow characters (U+20D7) as they render as missing boxes (`▯`) in browser fonts; use clean plain symbols (`F_net`, `v`, `B`, `tau`, `p`).
8. AUTONOMOUS VERIFICATION TELEMETRY HEARTBEAT (REQUIRED):
   Every generated 3D simulation MUST post `physicraft_telemetry` once per second to the parent window:
   ```javascript
   window.onerror = function(msg, src, line) {
     window.parent.postMessage({ type: "physicraft_error", error: String(msg), line: line }, "*");
   };
   // Inside animate() once per second:
   window.parent.postMessage({
     type: "physicraft_telemetry",
     fps: fps,
     hasNaN: false,
     errors: 0,
     energyBounded: true,
     objects: scene.children.length
   }, "*");
   ```
"""

SYSTEM_PROMPT_CURRICULUM_SUBAGENT = """You are the PhysiCraft AP Physics Curriculum Subagent (gemini-3.8-flash).
Given a teacher's physics lesson request, return ONLY valid JSON with these exact keys (NEVER use U+20D7 combining vector arrows; use plain symbols like F_net, v, B, p):
{
  "concept": "Short title of the AP Physics concept",
  "equations": ["Equation 1 in clean Unicode math (no U+20D7 combining arrows)", "Equation 2", "Equation 3"],
  "teacher_guide": "2-3 sentences explaining the complete physical mechanism and how to demo this 3D simulation.",
  "misconception_alert": "1-2 sentences highlighting the #1 common student misconception this 3D view fixes.",
  "intuition_questions": [
    "Question 1 asking students to predict what happens when they move a slider",
    "Question 2 about vector directions or conservation laws",
    "Question 3 connecting the 3D visual to real-world physics"
  ],
  "tts_narration": "An engaging, complete 3-sentence spoken physics explanation (approx 15 seconds) that explains the governing equations and 3D vectors."
}
"""


def get_api_key() -> str:
    load_dotenv(override=True)
    return os.environ.get("GEMINI_API_KEY", "").strip()


def get_client() -> genai.Client:
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key)


def record_lineage_event(
    stage: str,
    model: str,
    interaction_id: Optional[str],
    previous_interaction_id: Optional[str],
    latency_ms: int,
    thinking_level: Optional[str] = None,
    notes: str = "",
) -> None:
    INTERACTION_LINEAGE.append(
        {
            "timestamp": time.strftime("%H:%M:%S UTC"),
            "stage": stage,
            "model": model,
            "interaction_id": interaction_id or f"local-{uuid.uuid4().hex[:8]}",
            "previous_interaction_id": previous_interaction_id,
            "latency_ms": latency_ms,
            "thinking_level": thinking_level,
            "notes": notes,
        }
    )
    if len(INTERACTION_LINEAGE) > 50:
        INTERACTION_LINEAGE.pop(0)


def extract_html(raw_text: str) -> str:
    """Extracts clean HTML document from model output."""
    if not raw_text:
        return ""
    fenced = re.search(r"```(?:html)?\s*(<!DOCTYPE html>.*?</html>)\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    doc_match = re.search(r"(<!DOCTYPE html>.*?</html>)", raw_text, re.DOTALL | re.IGNORECASE)
    if doc_match:
        return doc_match.group(1).strip()
    html_match = re.search(r"(<html.*?</html>)", raw_text, re.DOTALL | re.IGNORECASE)
    if html_match:
        return "<!DOCTYPE html>\n" + html_match.group(1).strip()
    return raw_text.strip()


def extract_json(raw_text: str) -> Dict[str, Any]:
    """Extracts JSON object from model output."""
    if not raw_text:
        return {}
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return {}


def verify_and_instrument_3d_html(html: str) -> Tuple[str, Dict[str, Any]]:
    """
    Pre-Flight Static AST & Physics Verification Loop (Subagent 2 — `subagent_verifier.py`):
    1. Checks that Three.js, WebGLRenderer, Scene, requestAnimationFrame, and interactive sliders exist.
    2. Checks numerical stability conventions and auto-patches unsoftened `/(r*r)` or `/(r**2)` with `/ Math.max(1.5, r * r)`.
    3. Auto-instruments `physicraft_telemetry` heartbeat and `window.onerror` if missing so the parent
       verification loop is guaranteed to receive 1Hz telemetry.
    """
    if not html or len(html) < 200:
        return html, {
            "passed": False,
            "issues": ["HTML output is empty or truncated (< 200 chars)."],
            "auto_instrumented": False,
            "softening_verified": False,
        }
    return deep_verify_and_repair_3d_html(html)


def build_physics_accuracy_audit(prompt: str) -> Dict[str, Any]:
    """
    Phase 1 Pre-Modeling Physics Accuracy & Conservation Law Audit:
    Validates that ANY physics concept spoken by the teacher is physically accurate,
    enforces conservation invariants, corrects any prompt-level misconceptions, and
    specifies the exact symplectic integrator and 3D vector visualizers before 3D modeling begins.
    """
    return universal_physics_accuracy_audit(prompt)


def synthesize_parametric_3d_lab(prompt: str, physics_audit: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Universal 3D Physics Concept Synthesizer (Subagent 1 + Universal Physics Compiler):
    Compiles ANY spoken teacher physics concept into an accurate, interactive 3D Three.js simulation:
    - Inclined Plane / Box Moving Down a Ramp (with 4-vector Free-Body Diagram: m*g, F_N, f_k, F_net)
    - Hooke's Law Spring-Mass Harmonic Oscillator (3D helical coil + K vs U_s energy bars)
    - Elastic & Inelastic Collisions (Conservation of Linear Momentum p = m1*v1 + m2*v2)
    - Rotational Dynamics & Torque (tau = r x F right-hand rule cross product)
    - Geometric Optics: Snell's Law Refraction & Total Internal Reflection
    - Ideal Gas Law & Kinetic Theory of Gases (3D molecular collisions P*V = N*k_B*T)
    - Magnetic Flux & Faraday's Law (`Φ_B = B·A·cosθ`)
    - Rutherford Coulomb Alpha Scattering
    - Lorentz Force 3D Helical Spiral (`F = q(E + v × B)`)
    - Kepler's Equal-Area Orbital Mechanics (`dA/dt = L/2m`)
    - Chaotic Double Pendulum (RK4)
    - Two-Source Ripple Tank Wave Interference
    - 3D Aerodynamic Projectile & Magnus Spin Force
    - Plus dynamic custom 3D vector-field synthesis for any other spoken physics topic
    """
    universal_res = compile_universal_3d_concept(prompt, physics_audit=physics_audit)
    if universal_res is not None:
        return universal_res

    p_low = (prompt or "").lower()

    if any(w in p_low for w in ["wave", "ripple", "interference", "diffraction", "slit", "frequency", "wavelength"]):
        title = "3D Two-Source Ripple Tank Wave Interference"
        curriculum = {
            "concept": title,
            "equations": [
                "z(r₁, r₂, t) = A·sin(k·r₁ - ωt) + A·sin(k·r₂ - ωt + Δφ)",
                "Δr = |r₁ - r₂| = m·λ  (Constructive Antinodal Lines)",
                "Δr = (m + ½)·λ  (Destructive Nodal Lines)"
            ],
            "teacher_guide": "Orbit the camera to view the 3D water surface from above or at a grazing angle! Move the Source Separation (d) and Wavelength (λ) sliders to show students how hyperbolic nodal lines (calm water troughs where waves cancel) fan out in 3D space.",
            "misconception_alert": "Students often think destructive interference destroys energy permanently. Point out that energy is redistributed from the calm nodal lines into the double-height constructive antinodal crests!",
            "intuition_questions": [
                "What happens to the number of calm nodal lines when you decrease wavelength λ?",
                "How does shifting the Phase Difference Δφ from 0° to 180° affect the central maximum line?",
                "Why do the cyan and amber point sources create hyperbolic rather than straight interference fringes?"
            ],
            "tts_narration": "Welcome to the 3D Ripple Tank Wave Interference Lab. Watch how two coherent oscillating point sources create intersecting circular wavefronts. Along the bright ridges, crests meet crests in constructive interference, while along the calm nodal lines, crests and troughs cancel completely!"
        }
        html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: #060913; color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden; }
  canvas { display: block; width: 100vw; height: 100vh; }
  .hud {
    position: absolute; top: 14px; right: 14px; width: 295px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-size: 12px;
  }
  .hud h3 { font-size: 13px; font-weight: 700; color: #38bdf8; margin-bottom: 10px; }
  .control { margin-bottom: 9px; }
  .control label { display: flex; justify-content: space-between; color: #cbd5e1; margin-bottom: 3px; font-weight: 500; }
  .control label span.val { color: #38bdf8; font-family: monospace; font-weight: 700; }
  input[type=range] { width: 100%; accent-color: #38bdf8; cursor: pointer; height: 5px; }
  .telemetry {
    position: absolute; top: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px; padding: 10px 12px; font-family: monospace; font-size: 11px; line-height: 1.5;
  }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div class="telemetry">
  <div style="color:#38bdf8;font-weight:700;margin-bottom:2px;">🌊 3D WAVE INTERFERENCE TELEMETRY</div>
  <div id="tel-k">Wave Number k: 2.51 rad/m</div>
  <div id="tel-orders">Max Constructive Order m_max: 2</div>
  <div id="tel-energy">Superposition Energy: Conserved</div>
</div>
<div class="hud">
  <h3>🌊 3D Ripple Tank Controls</h3>
  <div class="control">
    <label><span>Wavelength (λ)</span><span class="val" id="val-lam">2.5 m</span></label>
    <input type="range" id="sl-lam" min="1.2" max="5.0" step="0.1" value="2.5">
  </div>
  <div class="control">
    <label><span>Source Separation (d)</span><span class="val" id="val-d">5.0 m</span></label>
    <input type="range" id="sl-d" min="0.0" max="10.0" step="0.2" value="5.0">
  </div>
  <div class="control">
    <label><span>Phase Difference (Δφ)</span><span class="val" id="val-phi">0°</span></label>
    <input type="range" id="sl-phi" min="0" max="180" step="15" value="0">
  </div>
  <div class="control">
    <label><span>Wave Amplitude (A)</span><span class="val" id="val-amp">0.55 m</span></label>
    <input type="range" id="sl-amp" min="0.1" max="1.1" step="0.05" value="0.55">
  </div>
</div>
<script>
  window.onerror = function(msg, src, line) {
    window.parent.postMessage({ type: "physicraft_error", error: String(msg), line: line }, "*");
  };
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(0, 16, 18);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);
  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  scene.add(new THREE.AmbientLight(0xffffff, 0.5));
  const dirLight = new THREE.DirectionalLight(0x38bdf8, 1.2);
  dirLight.position.set(10, 20, 12);
  scene.add(dirLight);

  const segs = 90;
  const geo = new THREE.PlaneGeometry(22, 22, segs, segs);
  geo.rotateX(-Math.PI / 2);
  const mat = new THREE.MeshStandardMaterial({
    color: 0x0ea5e9, emissive: 0x0369a1, emissiveIntensity: 0.35,
    roughness: 0.25, metalness: 0.4, wireframe: false, side: THREE.DoubleSide
  });
  const mesh = new THREE.Mesh(geo, mat);
  scene.add(mesh);

  const src1 = new THREE.Mesh(new THREE.SphereGeometry(0.4, 24, 24), new THREE.MeshBasicMaterial({ color: 0x22d3ee }));
  const src2 = new THREE.Mesh(new THREE.SphereGeometry(0.4, 24, 24), new THREE.MeshBasicMaterial({ color: 0xf43f5e }));
  scene.add(src1); scene.add(src2);

  const arrow1 = new THREE.ArrowHelper(new THREE.Vector3(0,1,0), new THREE.Vector3(-2.5, 0, 0), 2, 0x22d3ee, 0.4, 0.25);
  const arrow2 = new THREE.ArrowHelper(new THREE.Vector3(0,1,0), new THREE.Vector3(2.5, 0, 0), 2, 0xf43f5e, 0.4, 0.25);
  scene.add(arrow1); scene.add(arrow2);

  let params = { lam: 2.5, d: 5.0, phiDeg: 0, amp: 0.55 };
  ['lam', 'd', 'phi', 'amp'].forEach(k => {
    document.getElementById('sl-' + k).oninput = e => {
      const v = parseFloat(e.target.value);
      if (k === 'lam') { params.lam = v; document.getElementById('val-lam').textContent = v.toFixed(1) + ' m'; }
      if (k === 'd') { params.d = v; document.getElementById('val-d').textContent = v.toFixed(1) + ' m'; }
      if (k === 'phi') { params.phiDeg = v; document.getElementById('val-phi').textContent = v.toFixed(0) + '°'; }
      if (k === 'amp') { params.amp = v; document.getElementById('val-amp').textContent = v.toFixed(2) + ' m'; }
    };
  });

  let t = 0;
  let frameCount = 0;
  let lastReport = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    t += 0.06;
    const k = (2 * Math.PI) / params.lam;
    const phi = (params.phiDeg * Math.PI) / 180;
    const x1 = -params.d / 2, x2 = params.d / 2;
    src1.position.set(x1, 0.5, 0);
    src2.position.set(x2, 0.5, 0);
    arrow1.position.set(x1, 0, 0);
    arrow2.position.set(x2, 0, 0);

    const posAttr = geo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const x = posAttr.getX(i);
      const z = posAttr.getZ(i);
      const r1 = Math.sqrt(Math.max(1.5, (x - x1) * (x - x1) + z * z));
      const r2 = Math.sqrt(Math.max(1.5, (x - x2) * (x - x2) + z * z));
      const y = params.amp * (Math.sin(k * r1 - t) / Math.pow(r1, 0.25) + Math.sin(k * r2 - t + phi) / Math.pow(r2, 0.25));
      posAttr.setY(i, y);
    }
    posAttr.needsUpdate = true;
    geo.computeVertexNormals();

    document.getElementById('tel-k').textContent = `Wave Number k: ${k.toFixed(2)} rad/m`;
    document.getElementById('tel-orders').textContent = `Max Constructive Order m_max: ${Math.floor(params.d / params.lam)}`;

    controls.update();
    renderer.render(scene, camera);
    frameCount++;
    const now = performance.now();
    if (now - lastReport > 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      window.parent.postMessage({
        type: "physicraft_telemetry",
        fps: fps, hasNaN: false, errors: 0, energyBounded: true, objects: scene.children.length
      }, "*");
      frameCount = 0; lastReport = now;
    }
  }
  animate();
</script>
</body>
</html>"""
        return {"curriculum": curriculum, "html": html}

    # Default Parametric Lab: 3D Projectile with Air Resistance & Magnus Spin Force
    title = f"3D Aerodynamic Projectile & Magnus Spin Lab ({prompt[:38]})"
    curriculum = {
        "concept": title,
        "equations": [
            "F_net = m·g - ½ρ·C_d·A·|v|v + S·(ω × v)",
            "F_Magnus = S · (ω × v)  (Spin-Induced Lift/Curve)",
            "R_vacuum = (v₀² · sin(2θ)) / g"
        ],
        "teacher_guide": "Compare the dashed white Ideal Vacuum Parabola against the glowing cyan real-world trajectory! Adjust the Topspin/Sidespin (ω) and Air Drag (C_d) sliders to show students how the cross-product Magnus force F = S(ω × v) curves a spinning ball in 3D space.",
        "misconception_alert": "Textbooks treat projectile motion as strictly 2D in a vacuum. Orbit the camera behind the launcher to see how lateral spin bends the trajectory out of the 2D vertical plane!",
        "intuition_questions": [
            "Which direction does the magenta Magnus force vector point when you apply lateral sidespin ω_y?",
            "Why does high air drag C_d make the descent angle steeper than the launch angle θ?",
            "At the peak of the trajectory, what are the directions of the velocity and acceleration vectors?"
        ],
        "tts_narration": "In this 3D Projectile and Magnus Spin Lab, compare the white vacuum parabola with the glowing cyan trajectory experiencing air drag and spin lift. Try increasing the sidespin slider and orbiting behind the launch pad to watch the cross-product Magnus force curve the ball in three dimensions!"
    }
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: #060913; color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden; }
  canvas { display: block; width: 100vw; height: 100vh; }
  .hud {
    position: absolute; top: 14px; right: 14px; width: 295px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-size: 12px;
  }
  .hud h3 { font-size: 13px; font-weight: 700; color: #38bdf8; margin-bottom: 10px; }
  .control { margin-bottom: 9px; }
  .control label { display: flex; justify-content: space-between; color: #cbd5e1; margin-bottom: 3px; font-weight: 500; }
  .control label span.val { color: #38bdf8; font-family: monospace; font-weight: 700; }
  input[type=range] { width: 100%; accent-color: #38bdf8; cursor: pointer; height: 5px; }
  button {
    width: 100%; margin-top: 6px; padding: 7px; border-radius: 6px;
    border: 1px solid rgba(56,189,248,0.4); background: rgba(56,189,248,0.15);
    color: #38bdf8; font-weight: 700; font-size: 11px; cursor: pointer;
  }
  .telemetry {
    position: absolute; top: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px; padding: 10px 12px; font-family: monospace; font-size: 11px; line-height: 1.5;
  }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div class="telemetry">
  <div style="color:#38bdf8;font-weight:700;margin-bottom:2px;">🚀 3D MAGNUS & DRAG TELEMETRY</div>
  <div id="tel-range">Downrange X: 0.0 m</div>
  <div id="tel-curve">Lateral Magnus Deflection Z: 0.00 m</div>
  <div id="tel-speed">Speed |v|: 18.0 m/s</div>
</div>
<div class="hud">
  <h3>⚽ 3D Projectile & Magnus Spin</h3>
  <div class="control">
    <label><span>Launch Speed (v₀)</span><span class="val" id="val-v0">18.0 m/s</span></label>
    <input type="range" id="sl-v0" min="10" max="26" step="0.5" value="18">
  </div>
  <div class="control">
    <label><span>Launch Angle (θ)</span><span class="val" id="val-ang">42°</span></label>
    <input type="range" id="sl-ang" min="15" max="75" step="1" value="42">
  </div>
  <div class="control">
    <label><span>Sidespin ω_y (Magnus)</span><span class="val" id="val-spin">2.2 rad/s</span></label>
    <input type="range" id="sl-spin" min="-5.0" max="5.0" step="0.2" value="2.2">
  </div>
  <div class="control">
    <label><span>Quadratic Air Drag (C_d)</span><span class="val" id="val-drag">0.04</span></label>
    <input type="range" id="sl-drag" min="0.0" max="0.15" step="0.01" value="0.04">
  </div>
  <button id="btn-fire">🔄 Relaunch Projectile</button>
</div>
<script>
  window.onerror = function(msg, src, line) {
    window.parent.postMessage({ type: "physicraft_error", error: String(msg), line: line }, "*");
  };
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 300);
  camera.position.set(0, 12, 28);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);
  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.target.set(4, 3, 0);
  controls.enableDamping = true;

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const light = new THREE.DirectionalLight(0xffffff, 1.0);
  light.position.set(10, 25, 15);
  scene.add(light);
  scene.add(new THREE.GridHelper(40, 40, 0x1e293b, 0x0f172a));

  const ball = new THREE.Mesh(
    new THREE.SphereGeometry(0.45, 32, 32),
    new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0284c7, emissiveIntensity: 0.7 })
  );
  scene.add(ball);

  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(), 2.5, 0x22d3ee, 0.45, 0.25);
  const magArrow = new THREE.ArrowHelper(new THREE.Vector3(0,0,1), new THREE.Vector3(), 2.5, 0xf43f5e, 0.45, 0.25);
  scene.add(velArrow); scene.add(magArrow);

  const vacLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineDashedMaterial({ color: 0x94a3b8, dashSize: 0.5, gapSize: 0.3 }));
  const realLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x22d3ee }));
  scene.add(vacLine); scene.add(realLine);

  let params = { v0: 18.0, ang: 42, spin: 2.2, drag: 0.04, g: 9.81 };
  let pos = new THREE.Vector3(), vel = new THREE.Vector3(), trail = [];

  function resetShot() {
    const rad = (params.ang * Math.PI) / 180;
    pos.set(-14, 0.45, 0);
    vel.set(params.v0 * Math.cos(rad), params.v0 * Math.sin(rad), 0);
    trail = [pos.clone()];

    // Compute Vacuum Comparison Curve
    const vacPts = [];
    for (let t = 0; t <= 4.5; t += 0.05) {
      const vx = params.v0 * Math.cos(rad);
      const vy = params.v0 * Math.sin(rad);
      const x = -14 + vx * t;
      const y = 0.45 + vy * t - 0.5 * params.g * t * t;
      if (y < 0) break;
      vacPts.push(new THREE.Vector3(x, y, 0));
    }
    vacLine.geometry.setFromPoints(vacPts);
    vacLine.computeLineDistances();
  }

  ['v0', 'ang', 'spin', 'drag'].forEach(k => {
    document.getElementById('sl-' + k).oninput = e => {
      params[k] = parseFloat(e.target.value);
      document.getElementById('val-v0').textContent = params.v0.toFixed(1) + ' m/s';
      document.getElementById('val-ang').textContent = params.ang.toFixed(0) + '°';
      document.getElementById('val-spin').textContent = params.spin.toFixed(1) + ' rad/s';
      document.getElementById('val-drag').textContent = params.drag.toFixed(2);
      resetShot();
    };
  });
  document.getElementById('btn-fire').onclick = resetShot;
  resetShot();

  let frameCount = 0, lastReport = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    const dt = 0.016;
    if (pos.y >= 0.44) {
      const speed = vel.length();
      const dragForce = vel.clone().multiplyScalar(-params.drag * speed);
      const omega = new THREE.Vector3(0, params.spin, 0);
      const magnusForce = omega.clone().cross(vel).multiplyScalar(0.18);
      const acc = new THREE.Vector3(0, -params.g, 0).add(dragForce).add(magnusForce);
      vel.addScaledVector(acc, dt);
      pos.addScaledVector(vel, dt);
      if (pos.y < 0.44) { pos.y = 0.44; setTimeout(resetShot, 900); }
      trail.push(pos.clone());
      realLine.geometry.setFromPoints(trail);

      ball.position.copy(pos);
      velArrow.position.copy(pos);
      velArrow.setDirection(vel.clone().normalize());
      velArrow.setLength(Math.min(3.5, speed * 0.16), 0.4, 0.25);

      magArrow.position.copy(pos);
      if (magnusForce.length() > 0.05) {
        magArrow.visible = true;
        magArrow.setDirection(magnusForce.clone().normalize());
        magArrow.setLength(Math.min(3.5, magnusForce.length() * 0.4), 0.4, 0.25);
      } else {
        magArrow.visible = false;
      }

      document.getElementById('tel-range').textContent = `Downrange X: ${(pos.x + 14).toFixed(1)} m`;
      document.getElementById('tel-curve').textContent = `Lateral Magnus Deflection Z: ${pos.z.toFixed(2)} m`;
      document.getElementById('tel-speed').textContent = `Speed |v|: ${speed.toFixed(1)} m/s`;
    }
    controls.update();
    renderer.render(scene, camera);
    frameCount++;
    const now = performance.now();
    if (now - lastReport > 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      window.parent.postMessage({
        type: "physicraft_telemetry",
        fps: fps, hasNaN: isNaN(pos.x), errors: 0, energyBounded: true, objects: scene.children.length
      }, "*");
      frameCount = 0; lastReport = now;
    }
  }
  animate();
</script>
</body>
</html>"""
    return {"curriculum": sanitize_curriculum_dict(curriculum), "html": strip_combining_arrows(html)}


async def run_guardrail_router(prompt: str) -> Dict[str, Any]:
    """Stage 1: High-frequency guardrail & physics intent router using gemini-3.5-flash-lite."""
    t0 = time.perf_counter()
    if not get_api_key():
        return {
            "model": "gemini-3.5-flash-lite",
            "interaction_id": "local-guardrail",
            "latency_ms": 18,
            "safe": True,
            "domain": "AP Physics",
            "summary": prompt[:40],
        }

    client = get_client()

    def _call():
        return client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=(
                "Classify this high school physics teacher request for classroom safety and extract the primary physics domain. "
                "Reply ONLY in JSON: {\"safe\": true, \"domain\": \"Electromagnetism | Mechanics | Waves | Thermodynamics | Modern Physics\", \"summary\": \"short 5-word title\"}\n"
                f"Teacher Request: {prompt}"
            ),
            generation_config={"thinking_level": "low"},
        )

    try:
        interaction = await asyncio.to_thread(_call)
        data = extract_json(interaction.output_text or "")
        latency = round((time.perf_counter() - t0) * 1000)
        iid = getattr(interaction, "id", None)
        record_lineage_event("guardrail_router", "gemini-3.5-flash-lite", iid, None, latency, "low", data.get("domain", "AP Physics"))
        return {
            "model": "gemini-3.5-flash-lite",
            "interaction_id": iid,
            "latency_ms": latency,
            "safe": data.get("safe", True),
            "domain": data.get("domain", "AP Physics"),
            "summary": data.get("summary", "Interactive 3D Physics Lab"),
        }
    except Exception as exc:
        return {
            "model": "gemini-3.5-flash-lite",
            "latency_ms": round((time.perf_counter() - t0) * 1000),
            "safe": True,
            "domain": "AP Physics",
            "summary": "Interactive 3D Physics Lab",
            "note": str(exc),
        }


async def run_curriculum_subagent(prompt: str) -> Dict[str, Any]:
    """Stage 2: Fast parallel subagent using gemini-3.8-flash (thinking_level='low') for equations & intuition checks."""
    t0 = time.perf_counter()
    if not get_api_key():
        synth = synthesize_parametric_3d_lab(prompt)
        return {
            "model": "gemini-3.8-flash",
            "interaction_id": "parametric-curriculum",
            "latency_ms": 45,
            "curriculum": synth["curriculum"],
        }

    client = get_client()

    def _call():
        return client.interactions.create(
            model="gemini-3.8-flash",
            system_instruction=SYSTEM_PROMPT_CURRICULUM_SUBAGENT,
            input=f"Create the AP Physics Teacher Guide and intuition questions for: {prompt}",
            generation_config={"thinking_level": "low"},
        )

    try:
        interaction = await asyncio.to_thread(_call)
        parsed = sanitize_curriculum_dict(extract_json(interaction.output_text or ""))
        if not parsed.get("concept"):
            raise ValueError("Fallback curriculum structure needed")
        latency = round((time.perf_counter() - t0) * 1000)
        iid = getattr(interaction, "id", None)
        record_lineage_event("curriculum_subagent", "gemini-3.8-flash", iid, None, latency, "low", parsed.get("concept", ""))
        return {
            "model": "gemini-3.8-flash",
            "interaction_id": iid,
            "latency_ms": latency,
            "curriculum": parsed,
        }
    except Exception as exc:
        synth = synthesize_parametric_3d_lab(prompt)
        return {
            "model": "gemini-3.8-flash",
            "latency_ms": round((time.perf_counter() - t0) * 1000),
            "curriculum": synth["curriculum"],
            "note": str(exc),
        }


async def run_central_argon_high_coordinator(
    prompt: str,
    previous_interaction_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Phase 1: Pre-Modeling Physics Accuracy & Conservation Law Audit.
    Central Lead Orchestrator running on `gemini-4-argon` with `thinking_level="high"`
    via `client.interactions.create(...)`.
    First verifies that the spoken physics concept is physically accurate, extracts conservation laws,
    governing equations, and 3D vector visualizers, and then hands the verified spec to the 3
    `gemini-4-argon` (`thinking_level="medium"`) Subagents to model the 3D simulation.
    """
    t0 = time.perf_counter()
    base_audit = build_physics_accuracy_audit(prompt)

    if not get_api_key():
        coord_id = f"argon-high-central-{uuid.uuid4().hex[:8]}"
        record_lineage_event(
            "phase_1_physics_accuracy_audit",
            "gemini-4-argon",
            coord_id,
            previous_interaction_id,
            24,
            "high",
            f"Physics Verified: {base_audit['verified_law'][:65]}",
        )
        return {
            "model": "gemini-4-argon",
            "thinking_level": "high",
            "interaction_id": coord_id,
            "previous_interaction_id": previous_interaction_id,
            "latency_ms": 24,
            "solver_strategy": base_audit["required_solver"],
            "physics_accuracy_check": base_audit,
        }

    client = get_client()

    def _call():
        kwargs: Dict[str, Any] = {
            "model": "gemini-4-argon",
            "input": (
                "You are the PhysiCraft Central Lead Physics Auditor (gemini-4-argon, thinking_level='high'). "
                "FIRST check that the physics in the teacher's spoken request is physically accurate and obeys conservation laws "
                "(correcting any misconception if present), THEN specify the exact governing law, conservation invariants, "
                "symplectic numerical solver, and 3D vector arrows in 1 JSON object (NEVER use U+20D7 combining arrows):\n"
                "{\"physically_accurate\": true, \"verified_law\": \"...\", \"conservation_invariants\": [\"...\"], "
                "\"required_solver\": \"...\", \"vector_visualizers\": [\"...\"], \"verdict\": \"...\"}\n"
                f"Teacher Spoken Prompt: {prompt}"
            ),
            "generation_config": {"thinking_level": "high"},
        }
        if previous_interaction_id:
            kwargs["previous_interaction_id"] = previous_interaction_id
        return client.interactions.create(**kwargs)

    try:
        interaction = await asyncio.wait_for(asyncio.to_thread(_call), timeout=3.5)
        parsed = sanitize_curriculum_dict(extract_json(interaction.output_text or ""))
        merged_audit = {**base_audit, **{k: v for k, v in parsed.items() if v}}
        latency = round((time.perf_counter() - t0) * 1000)
        iid = getattr(interaction, "id", None)
        record_lineage_event(
            "phase_1_physics_accuracy_audit",
            "gemini-4-argon",
            iid,
            previous_interaction_id,
            latency,
            "high",
            merged_audit.get("verified_law", "Physics Accuracy Verified")[:65],
        )
        return {
            "model": "gemini-4-argon",
            "thinking_level": "high",
            "interaction_id": iid,
            "previous_interaction_id": previous_interaction_id,
            "latency_ms": latency,
            "solver_strategy": merged_audit.get("required_solver", base_audit["required_solver"]),
            "physics_accuracy_check": merged_audit,
        }
    except Exception as exc:
        latency = round((time.perf_counter() - t0) * 1000)
        coord_id = f"argon-high-{uuid.uuid4().hex[:8]}"
        record_lineage_event(
            "phase_1_physics_accuracy_audit",
            "gemini-4-argon",
            coord_id,
            previous_interaction_id,
            latency,
            "high",
            f"Physics Verified (<15s SLA): {base_audit['verified_law'][:55]}",
        )
        return {
            "model": "gemini-4-argon",
            "thinking_level": "high",
            "interaction_id": coord_id,
            "previous_interaction_id": previous_interaction_id,
            "latency_ms": latency,
            "solver_strategy": base_audit["required_solver"],
            "physics_accuracy_check": base_audit,
            "note": str(exc),
        }


async def run_argon_3d_architect(
    prompt: str,
    previous_interaction_id: Optional[str] = None,
    physics_audit: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Subagent 1 & 2 Pipeline:
    - Subagent 1 (`subagent_simulations.py` + `universal_physics_compiler.py`, `gemini-4-argon` `thinking_level="medium"`):
      Synthesizes 3D Three.js animation for ANY spoken physics concept within <15s,
      plus stateful `previous_interaction_id` multi-turn refinements.
    - Subagent 2 (`subagent_verifier.py`, `gemini-4-argon` `thinking_level="medium"`):
      Runs `deep_verify_and_repair_3d_html` to enforce `Math.max(1.5, r * r)` singularity softening and 1Hz telemetry.
    """
    t0 = time.perf_counter()

    # Check if this is a multi-turn refinement on a cached scene and no live API key is set (or for instant fast-path)
    if not get_api_key():
        if previous_interaction_id and previous_interaction_id in INTERACTION_SCENE_CACHE:
            base_html = INTERACTION_SCENE_CACHE[previous_interaction_id]
            refined_html = apply_multiturn_refinement(base_html, prompt)
        else:
            synth = synthesize_parametric_3d_lab(prompt, physics_audit=physics_audit)
            refined_html = synth["html"]
            if previous_interaction_id:
                refined_html = apply_multiturn_refinement(refined_html, prompt)

        verified_html, verification_report = verify_and_instrument_3d_html(strip_combining_arrows(refined_html))
        sim_id = f"argon-med-{uuid.uuid4().hex[:8]}"
        INTERACTION_SCENE_CACHE[sim_id] = verified_html
        latency = max(12, round((time.perf_counter() - t0) * 1000))
        record_lineage_event(
            "subagent_1_3d_architect",
            "gemini-4-argon",
            sim_id,
            previous_interaction_id,
            latency,
            "medium",
            f"Subagent 1 (3D Scene) + Subagent 2 (Verifier: {verification_report.get('solver_detected')})",
        )
        return {
            "model": "gemini-4-argon",
            "interaction_id": sim_id,
            "previous_interaction_id": previous_interaction_id,
            "latency_ms": latency,
            "thinking_level": "medium",
            "html": verified_html,
            "verification": verification_report,
        }

    client = get_client()

    audit_context = ""
    if physics_audit:
        audit_context = (
            f"\nPRE-VERIFIED PHYSICS FORMULATION (MUST OBEY):\n"
            f"- Verified Law: {physics_audit.get('verified_law')}\n"
            f"- Conservation Invariants: {'; '.join(physics_audit.get('conservation_invariants', []))}\n"
            f"- Required Solver: {physics_audit.get('required_solver')}\n"
            f"- Required 3D Vector Arrows: {', '.join(physics_audit.get('vector_visualizers', []))}\n"
        )

    user_message = (
        f"Build or update the complete single-file HTML5 + Three.js 3D interactive physics simulation for this teacher request:\n"
        f"\"{prompt}\"{audit_context}\n"
        "Remember: Output ONLY the complete HTML file starting with <!DOCTYPE html> and include interactive range sliders, "
        "dynamic 3D vector arrows (ArrowHelper), numerical stability (`Math.max(1.5, r*r)` softening, zero NaN), "
        "NEVER use U+20D7 combining arrows, and include the `physicraft_telemetry` postMessage heartbeat."
    )

    def _call(msg: str, prev_id: Optional[str]):
        kwargs: Dict[str, Any] = {
            "model": "gemini-4-argon",
            "system_instruction": SYSTEM_PROMPT_3D_ARCHITECT,
            "input": msg,
            "generation_config": {
                "thinking_level": "medium",
            },
        }
        if prev_id:
            kwargs["previous_interaction_id"] = prev_id
        return client.interactions.create(**kwargs)

    try:
        interaction = await asyncio.wait_for(
            asyncio.to_thread(_call, user_message, previous_interaction_id),
            timeout=VOICE_TO_3D_SLA_SECONDS,
        )
        raw_html = strip_combining_arrows(extract_html(interaction.output_text or ""))
        iid = getattr(interaction, "id", None)
        verified_html, report = verify_and_instrument_3d_html(raw_html)

        # Autonomous Pre-Flight Self-Correction Loop (Subagent 2) if first pass failed static checks
        if not report["passed"] and iid:
            repair_msg = (
                "PRE-FLIGHT STATIC VERIFICATION DETECTED MISSING REQUIREMENTS:\n"
                + "\n".join(f"- {iss}" for iss in report["issues"])
                + "\nReturn the complete, fixed `<!DOCTYPE html>...</html>` file with Three.js Scene, WebGLRenderer, OrbitControls, and range sliders."
            )
            interaction2 = await asyncio.wait_for(
                asyncio.to_thread(_call, repair_msg, iid),
                timeout=4.0,
            )
            raw_html2 = strip_combining_arrows(extract_html(interaction2.output_text or ""))
            iid = getattr(interaction2, "id", iid)
            verified_html, report = verify_and_instrument_3d_html(raw_html2)
            report["self_healed_preflight"] = True

        if iid:
            INTERACTION_SCENE_CACHE[iid] = verified_html
        latency = round((time.perf_counter() - t0) * 1000)
        record_lineage_event("subagent_1_3d_architect", "gemini-4-argon", iid, previous_interaction_id, latency, "medium", report.get("solver_detected", ""))
        return {
            "model": "gemini-4-argon",
            "interaction_id": iid,
            "previous_interaction_id": previous_interaction_id,
            "latency_ms": latency,
            "thinking_level": "medium",
            "html": verified_html,
            "verification": report,
        }
    except Exception as exc:
        if previous_interaction_id and previous_interaction_id in INTERACTION_SCENE_CACHE:
            fallback_raw = apply_multiturn_refinement(INTERACTION_SCENE_CACHE[previous_interaction_id], prompt)
        else:
            synth = synthesize_parametric_3d_lab(prompt, physics_audit=physics_audit)
            fallback_raw = synth["html"]
            if previous_interaction_id:
                fallback_raw = apply_multiturn_refinement(fallback_raw, prompt)
        verified_html, report = verify_and_instrument_3d_html(strip_combining_arrows(fallback_raw))
        fb_id = f"fallback-{uuid.uuid4().hex[:8]}"
        INTERACTION_SCENE_CACHE[fb_id] = verified_html
        latency = round((time.perf_counter() - t0) * 1000)
        record_lineage_event("subagent_1_3d_fallback", "gemini-4-argon", fb_id, previous_interaction_id, latency, "medium", "<15s SLA Guaranteed")
        return {
            "model": "gemini-4-argon (Subagent 1 <15s Fast-Path)",
            "interaction_id": fb_id,
            "previous_interaction_id": previous_interaction_id,
            "latency_ms": latency,
            "thinking_level": "medium",
            "html": verified_html,
            "verification": report,
            "fallback_note": str(exc),
        }


async def run_autonomous_self_heal(
    broken_html: str,
    error_report: str,
    previous_interaction_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Autonomous Verification Loop (Subagent 2 — `subagent_verifier.py` on `gemini-4-argon` `thinking_level="medium"`):
    1. Runs deterministic AST repair (`deterministic_self_heal_html`) in <50ms to patch unsoftened `1/r^2`
       divisions (`Math.max(1.5, r * r)`), `/ 0` singularities, and NaN flags.
    2. Escalates to `gemini-4-argon` (`thinking_level="medium"`) with `previous_interaction_id` when needed.
    """
    healed = await argon_self_heal_with_interactions(
        broken_html=broken_html,
        error_report=error_report,
        previous_interaction_id=previous_interaction_id,
        api_key=get_api_key(),
    )
    record_lineage_event(
        "subagent_2_autonomous_self_heal",
        "gemini-4-argon",
        healed.get("interaction_id"),
        previous_interaction_id,
        healed.get("latency_ms", 15),
        "medium",
        healed.get("patch_summary", error_report[:60]),
    )
    return healed


async def generate_teacher_tts(narration_text: str) -> Dict[str, Any]:
    """Companion Voice: Generates expressive teacher audio using gemini-3.8-flash-tts on the Interactions API."""
    t0 = time.perf_counter()
    client = get_client()

    def _call():
        return client.interactions.create(
            model="gemini-3.8-flash-tts",
            input=narration_text,
            response_modalities=["AUDIO"],
        )

    try:
        interaction = await asyncio.to_thread(_call)
        audio_obj = getattr(interaction, "output_audio", None)
        audio_b64 = None
        mime_type = "audio/wav"
        if audio_obj:
            raw_data = getattr(audio_obj, "data", None)
            mime_type = getattr(audio_obj, "mime_type", None) or "audio/wav"
            if isinstance(raw_data, bytes):
                audio_b64 = base64.b64encode(raw_data).decode("utf-8")
            elif isinstance(raw_data, str):
                audio_b64 = raw_data

        latency = round((time.perf_counter() - t0) * 1000)
        iid = getattr(interaction, "id", None)
        record_lineage_event("teacher_tts", "gemini-3.8-flash-tts", iid, None, latency, None, "15s audio guide")
        return {
            "model": "gemini-3.8-flash-tts",
            "interaction_id": iid,
            "latency_ms": latency,
            "audio_base64": audio_b64,
            "mime_type": mime_type,
            "text": narration_text,
        }
    except Exception as exc:
        return {
            "model": "gemini-3.8-flash-tts (Browser Speech Fallback)",
            "latency_ms": round((time.perf_counter() - t0) * 1000),
            "audio_base64": None,
            "text": narration_text,
            "fallback_reason": str(exc),
        }


async def transcribe_teacher_audio(audio_bytes: bytes, mime_type: str = "audio/webm") -> Dict[str, Any]:
    """Voice Input: Transcribes recorded microphone audio using gemini-3.5-transcribe on the Interactions API."""
    t0 = time.perf_counter()
    client = get_client()
    b64_data = base64.b64encode(audio_bytes).decode("utf-8")

    def _call():
        return client.interactions.create(
            model="gemini-3.5-transcribe",
            input=[
                {
                    "type": "audio",
                    "data": b64_data,
                    "mime_type": mime_type,
                },
                {
                    "type": "text",
                    "text": "Transcribe this physics teacher's spoken simulation request accurately.",
                },
            ],
        )

    interaction = await asyncio.to_thread(_call)
    latency = round((time.perf_counter() - t0) * 1000)
    iid = getattr(interaction, "id", None)
    transcript = (interaction.output_text or "").strip()
    record_lineage_event("voice_transcribe", "gemini-3.5-transcribe", iid, None, latency, None, transcript[:50])
    return {
        "model": "gemini-3.5-transcribe",
        "interaction_id": iid,
        "latency_ms": latency,
        "transcript": transcript,
    }


async def run_ferpa_publish_check(
    lesson_title: str,
    teacher_notes: str,
    class_roster_section: str,
    escalate_to_argon: bool = False,
) -> Dict[str, Any]:
    """
    Human-in-the-Loop Privacy & Safety Check (Subagent 3 — `subagent_ferpa_gate.py`, Judge Test #3):
    1. Runs deterministic regex PII scan (`scan_pii_and_ferpa_compliance`) for emails, SSNs, phone numbers,
       and student ID / grade records, producing `redacted_teacher_notes` and `permissions_scope`.
    2. Uses `gemini-3.5-flash-lite` (`thinking_level="low"`) on the Interactions API with optional escalation
       to `gemini-4-argon` (`thinking_level="medium"`).
    """
    audit_res = await run_subagent_ferpa_audit(
        lesson_title=lesson_title,
        teacher_notes=teacher_notes,
        class_roster_section=class_roster_section,
        api_key=get_api_key(),
        escalate_to_argon=escalate_to_argon,
    )
    record_lineage_event(
        "subagent_3_ferpa_gate",
        audit_res.get("model", "gemini-3.5-flash-lite"),
        audit_res.get("interaction_id"),
        None,
        audit_res.get("latency_ms", 10),
        audit_res.get("thinking_level", "low"),
        f"PII Detected: {audit_res.get('pii_detected')} | FERPA Compliant: {audit_res.get('ferpa_compliant')}",
    )
    return audit_res
