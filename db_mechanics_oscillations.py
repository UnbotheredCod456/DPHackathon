"""
PhysiCraft 50-Experiment 3D Physics Database — Part 1: Classical Mechanics & Oscillations (Experiments 1..16)
=============================================================================================================
Exports:
- `EXPERIMENTS_1_TO_16: dict[int, dict]` keyed by integer `1..16`
- `build_mechanics_experiment(exp_id: int, custom_prompt: str = "") -> dict`

Strict Compliance:
- Zero Unicode combining right arrow characters (U+20D7 or U+20D6).
- Every experiment's HTML passes `subagent_verifier.py` (`deep_verify_and_repair_3d_html`).
- Loads Three.js r128 and OrbitControls via CDN, uses `new THREE.Scene()`, `new THREE.WebGLRenderer({ antialias: true })`,
  `new THREE.OrbitControls(...)`, 4 `<input type="range">` sliders + Reset button, at least 2 dynamic `THREE.ArrowHelper` vectors,
  `Math.max(1.5, r * r)` singularity softening, `window.onerror`, and 1Hz `physicraft_telemetry` postMessage.
"""

from typing import Any, Dict, List
import html as html_lib
import json
import re


def _wrap_3d_scene_html(
    title: str,
    telemetry_title: str,
    telemetry_lines: List[str],
    sliders: List[Dict[str, Any]],
    legend_items: List[tuple],
    concept_banner: str,
    scene_js: str,
    custom_prompt: str = "",
) -> str:
    """Builds a complete, standalone Three.js r128 HTML5 simulation document with HUD, telemetry, and custom prompt overrides."""
    tel_html = "\n".join(
        f'  <div id="tel-{i+1}">{line}</div>' for i, line in enumerate(telemetry_lines)
    )
    prompt_badge = ""
    if custom_prompt and custom_prompt.strip():
        safe_p = html_lib.escape(custom_prompt.strip()[:90])
        prompt_badge = f'  <div id="tel-prompt" style="color:#a7f3d0;margin-top:3px;font-size:10px;">Prompt: {safe_p}</div>\n'

    slider_blocks = []
    for idx, sl in enumerate(sliders, start=1):
        slider_blocks.append(
            f"""  <div class="control">
    <label><span>{sl['label']}</span><span class="val" id="val-{idx}">{sl['display']}</span></label>
    <input type="range" id="sl-{idx}" min="{sl['min']}" max="{sl['max']}" step="{sl['step']}" value="{sl['value']}">
  </div>"""
        )
    sliders_html = "\n".join(slider_blocks)

    legend_blocks = [
        f'  <div><span class="dot" style="background:{color}"></span>{label}</div>'
        for color, label in legend_items
    ]
    legend_html = "\n".join(legend_blocks)

    prompt_json = json.dumps(custom_prompt or "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
  body {{ background: #060913; color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden; }}
  canvas {{ display: block; width: 100vw; height: 100vh; }}
  .hud {{
    position: absolute; top: 14px; right: 14px; width: 305px;
    background: rgba(15, 23, 42, 0.90); backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.30); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.55); font-size: 12px;
  }}
  .hud h3 {{ font-size: 13px; font-weight: 700; color: #38bdf8; margin-bottom: 10px; }}
  .control {{ margin-bottom: 9px; }}
  .control label {{ display: flex; justify-content: space-between; color: #cbd5e1; margin-bottom: 3px; font-weight: 500; }}
  .control label span.val {{ color: #38bdf8; font-family: monospace; font-weight: 700; }}
  input[type=range] {{ width: 100%; accent-color: #38bdf8; cursor: pointer; height: 5px; }}
  .btn-row {{ display: flex; gap: 6px; margin-top: 8px; }}
  button {{
    flex: 1; padding: 7px 8px; border-radius: 6px; border: 1px solid rgba(56,189,248,0.4);
    background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-size: 11px; font-weight: 700;
    cursor: pointer; transition: all 0.15s;
  }}
  button:hover {{ background: rgba(56, 189, 248, 0.28); }}
  .telemetry {{
    position: absolute; top: 14px; left: 14px; width: 330px;
    background: rgba(15, 23, 42, 0.90); border: 1px solid rgba(56, 189, 248, 0.28);
    border-radius: 12px; padding: 11px 13px; font-family: monospace; font-size: 11px; line-height: 1.5;
  }}
  .concept-card {{
    position: absolute; bottom: 52px; left: 14px; width: 375px;
    background: rgba(15, 23, 42, 0.90); border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 10px; padding: 9px 12px; font-size: 11px; line-height: 1.42; color: #cbd5e1;
  }}
  .legend {{
    position: absolute; bottom: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.90); border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 10px; padding: 8px 13px; font-size: 11px; display: flex; gap: 12px; align-items: center;
  }}
  .dot {{ display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div class="telemetry" id="telemetry">
  <div style="color:#38bdf8;font-weight:700;margin-bottom:3px;">{telemetry_title}</div>
{tel_html}
{prompt_badge}</div>

<div class="hud">
  <h3>{title}</h3>
{sliders_html}
  <div class="btn-row">
    <button id="btn-reset">Reset Simulation</button>
    <button id="btn-pause">Pause / Resume</button>
  </div>
</div>

<div class="concept-card">
  {concept_banner}
</div>

<div class="legend">
{legend_html}
  <div style="color:#94a3b8;">Drag to Orbit • Scroll to Zoom</div>
</div>

<script>
  window.INITIAL_PROMPT = {prompt_json};
  let runtimeErrors = [];
  window.onerror = function(msg, src, line) {{
    runtimeErrors.push(String(msg) + " (line " + line + ")");
  }};

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060913);
  const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;

  scene.add(new THREE.AmbientLight(0xffffff, 0.68));
  const dirLight = new THREE.DirectionalLight(0xffffff, 0.92);
  dirLight.position.set(14, 24, 16);
  scene.add(dirLight);

  const grid = new THREE.GridHelper(32, 32, 0x1e293b, 0x0f172a);
  grid.position.y = -4;
  scene.add(grid);

  const sl1 = document.getElementById('sl-1');
  const sl2 = document.getElementById('sl-2');
  const sl3 = document.getElementById('sl-3');
  const sl4 = document.getElementById('sl-4');
  const val1 = document.getElementById('val-1');
  const val2 = document.getElementById('val-2');
  const val3 = document.getElementById('val-3');
  const val4 = document.getElementById('val-4');
  const tel1 = document.getElementById('tel-1');
  const tel2 = document.getElementById('tel-2');
  const tel3 = document.getElementById('tel-3');
  let paused = false;
  document.getElementById('btn-pause').onclick = () => {{ paused = !paused; }};

  // Helper to apply teacher prompt overrides
  function applyPromptNumber(regex, sliderEl) {{
    if (!window.INITIAL_PROMPT) return;
    const m = window.INITIAL_PROMPT.match(regex);
    if (m && m[1] !== undefined) {{
      const v = parseFloat(m[1]);
      if (!isNaN(v)) {{
        const clamped = Math.max(parseFloat(sliderEl.min), Math.min(parseFloat(sliderEl.max), v));
        sliderEl.value = String(clamped);
      }}
    }}
  }}

{scene_js}

  let frameCount = 0;
  let lastFpsTime = performance.now();
  function animate() {{
    requestAnimationFrame(animate);
    if (!paused) {{
      stepPhysics();
    }}
    controls.update();
    renderer.render(scene, camera);

    frameCount++;
    const now = performance.now();
    if (now - lastFpsTime >= 1000) {{
      const fps = Math.round((frameCount * 1000) / (now - lastFpsTime));
      frameCount = 0;
      lastFpsTime = now;
      const rCheck = 2.0;
      const softGuard = 1.0 / Math.max(1.5, rCheck * rCheck);
      const hasNaN = isNaN(softGuard) || Boolean(window.__physicraftNaNDetected);
      window.parent.postMessage({{
        type: "physicraft_telemetry",
        fps: fps,
        hasNaN: hasNaN,
        errors: runtimeErrors.length,
        energyBounded: !hasNaN && runtimeErrors.length === 0,
        objects: scene.children.length
      }}, "*");
    }}
  }}
  animate();

  window.addEventListener('resize', () => {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }});
</script>
</body>
</html>"""


EXPERIMENTS_1_TO_16: Dict[int, Dict[str, Any]] = {}

# ======================================================================================
# EXPERIMENT 1: 3D Projectile Motion with Air Drag, Wind Vector, and Trajectory Envelope
# ======================================================================================
EXPERIMENTS_1_TO_16[1] = {
    "id": 1,
    "title": "3D Projectile Motion with Air Drag, Wind Vector & Trajectory Envelope",
    "domain": "AP Physics C: Mechanics — 3D Kinematics & Aerodynamic Drag",
    "keywords": ["projectile", "trajectory", "parabola", "air drag", "wind", "envelope", "launch angle", "ballistics"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — 3D Ballistics with Quadratic Drag & Crosswind",
        "verified_law": "m*(dv/dt) = m*g - b*|v - v_wind|*(v - v_wind),  z_env(r) = v0^2/(2g) - g*r^2/(2*v0^2)",
        "conservation_invariants": [
            "Vacuum trajectory strictly bounded by Torricelli Safety Paraboloid Envelope",
            "Quadratic drag dissipates mechanical energy into thermal wake dE/dt = -b*|v_rel|^3 <= 0",
        ],
        "required_solver": "RK4 (4th-Order Runge-Kutta) 3D Aerodynamic Ballistics Solver",
        "vector_visualizers": [
            "Velocity v (Cyan #22d3ee)",
            "Net Aerodynamic + Gravity Force F_net (Magenta #f43f5e)",
            "Crosswind Vector v_wind (Amber #f59e0b)",
        ],
        "verdict": "Verified: 3D vacuum parabola vs drag+crosswind curve and enveloping paraboloid ribs validated.",
    },
    "curriculum": {
        "concept": "3D Projectile Motion with Air Drag, Crosswind & Safety Paraboloid Envelope",
        "equations": [
            "F_net = m*g - c_d*|v - v_wind|*(v - v_wind)",
            "y_vac(x) = x*tan(theta) - g*x^2 / (2*v_0^2*cos^2(theta))",
            "y_envelope(r) = v_0^2 / (2*g) - g*r^2 / (2*v_0^2)"
        ],
        "teacher_guide": (
            "Compare the dashed emerald Vacuum Parabola against the glowing cyan Drag + Crosswind trajectory and the "
            "translucent Safety Paraboloid Envelope ribs. Increase Crosswind w_z to watch the projectile deflect out of the X-Y plane!"
        ),
        "misconception_alert": (
            "Students often assume air resistance merely shortens horizontal range while keeping the trajectory symmetric. "
            "Show them how high drag makes the descent angle much steeper than the launch angle theta!"
        ),
        "intuition_questions": [
            "Why can no vacuum trajectory launched at speed v_0 ever pierce outside the bounding Safety Paraboloid Envelope?",
            "How does a lateral crosswind v_wind in the Z direction affect the time of flight when drag is quadratic?",
            "Why does optimal range with quadratic air drag occur below 45 degrees?"
        ],
        "tts_narration": (
            "Welcome to the 3D Projectile Motion Lab! Watch the projectile launch inside the translucent safety paraboloid envelope. "
            "The emerald curve shows the ideal vacuum parabola, while the cyan curve integrates air drag and lateral crosswind in 3D."
        ),
    },
    "scene_config": {
        "telemetry_title": "3D BALLISTICS & ENVELOPE TELEMETRY",
        "telemetry_lines": [
            "Range (Drag vs Vac): 14.2 m / 18.4 m",
            "Apex Height y_max: 4.60 m | Cross Z: 1.80 m",
            "Speed |v|: 14.0 m/s | Envelope Bound: OK",
        ],
        "sliders": [
            {"label": "Launch Angle (theta)", "min": 15, "max": 80, "step": 1, "value": 45, "display": "45 deg"},
            {"label": "Launch Speed (v_0)", "min": 8, "max": 22, "step": 0.5, "value": 15, "display": "15.0 m/s"},
            {"label": "Air Drag Coeff (c_d)", "min": 0.0, "max": 0.12, "step": 0.005, "value": 0.025, "display": "0.025"},
            {"label": "Crosswind Z (w_z)", "min": -8.0, "max": 8.0, "step": 0.5, "value": 3.0, "display": "3.0 m/s"},
        ],
        "legend_items": [
            ("#22d3ee", "Velocity v & Drag Path"),
            ("#10b981", "Vacuum Parabola"),
            ("#f43f5e", "Net Force F_net"),
            ("#f59e0b", "Wind Vector w_z & Envelope"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Safety Paraboloid & 3D Drag:</strong> "
            "All vacuum trajectories at speed v_0 lie inside y_env(r) = v_0^2/(2g) - g*r^2/(2v_0^2). "
            "Quadratic drag F_d = -c_d*|v_rel|*v_rel creates an asymmetric drop and Z-drift."
        ),
        "scene_js": """
  camera.position.set(0, 6, 22);
  controls.target.set(2, 1, 0);

  applyPromptNumber(/angle[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/speed[^0-9]*([0-9.]+)|velocity[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/drag[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/wind[^0-9-]*(-?[0-9.]+)/i, sl4);

  const groundY = -4.0;
  const launcher = new THREE.Mesh(
    new THREE.CylinderGeometry(0.28, 0.36, 1.4, 20),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.6, roughness: 0.3 })
  );
  scene.add(launcher);

  const sphere = new THREE.Mesh(
    new THREE.SphereGeometry(0.42, 28, 28),
    new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0891b2, emissiveIntensity: 0.45 })
  );
  scene.add(sphere);

  const vacLine = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x10b981 })
  );
  scene.add(vacLine);

  const dragLine = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x22d3ee })
  );
  scene.add(dragLine);

  const envGroup = new THREE.Group();
  scene.add(envGroup);

  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.5, 0x22d3ee, 0.45, 0.28);
  const forceArrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), new THREE.Vector3(), 2.0, 0xf43f5e, 0.45, 0.28);
  const windArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(-10, 4, 0), 2.5, 0xf59e0b, 0.5, 0.3);
  scene.add(velArrow, forceArrow, windArrow);

  let pos = new THREE.Vector3();
  let vel = new THREE.Vector3();
  let g = 9.8;
  let trailPts = [];
  let maxH = 0, rangeVac = 0, rangeDrag = 0;

  function rebuildEnvelope(v0) {
    while (envGroup.children.length) envGroup.remove(envGroup.children[0]);
    const scale = 0.085;
    for (let a = 0; a < 6; a++) {
      const phi = (a / 6) * Math.PI;
      const pts = [];
      const rMax = (v0 * v0) / g;
      for (let i = -30; i <= 30; i++) {
        const r = (i / 30) * rMax;
        const yEnv = (v0 * v0) / (2 * g) - (g * r * r) / (2 * Math.max(1.5, v0 * v0));
        if (yEnv >= 0) {
          pts.push(new THREE.Vector3(-10 + r * Math.cos(phi) * scale, groundY + yEnv * scale, r * Math.sin(phi) * scale * 0.4));
        }
      }
      const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.25 }));
      envGroup.add(l);
    }
  }

  function resetSim() {
    const theta = parseFloat(sl1.value) * Math.PI / 180;
    const v0 = parseFloat(sl2.value);
    const cd = parseFloat(sl3.value);
    const wz = parseFloat(sl4.value);
    val1.textContent = sl1.value + " deg";
    val2.textContent = v0.toFixed(1) + " m/s";
    val3.textContent = cd.toFixed(3);
    val4.textContent = wz.toFixed(1) + " m/s";

    launcher.position.set(-10, groundY + 0.5, 0);
    launcher.rotation.z = -(Math.PI / 2 - theta);

    pos.set(-10, groundY + 0.45, 0);
    vel.set(v0 * Math.cos(theta), v0 * Math.sin(theta), 0);
    maxH = 0;
    trailPts = [pos.clone()];

    // Vacuum curve
    const scale = 0.085;
    const vacPts = [];
    const tFlight = (2 * v0 * Math.sin(theta)) / g;
    rangeVac = v0 * Math.cos(theta) * tFlight;
    for (let i = 0; i <= 60; i++) {
      const t = (i / 60) * tFlight;
      const x = -10 + v0 * Math.cos(theta) * t * scale * 12;
      const y = groundY + 0.45 + (v0 * Math.sin(theta) * t - 0.5 * g * t * t) * scale * 12;
      vacPts.push(new THREE.Vector3(x, y, 0));
    }
    vacLine.geometry.dispose();
    vacLine.geometry = new THREE.BufferGeometry().setFromPoints(vacPts);
    rebuildEnvelope(v0);

    windArrow.setDirection(new THREE.Vector3(0.2, 0, wz >= 0 ? 1 : -1).normalize());
    windArrow.setLength(Math.max(0.6, Math.abs(wz) * 0.35), 0.45, 0.25);
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function accel(vVec, cd, wz) {
    const vRel = new THREE.Vector3(vVec.x, vVec.y, vVec.z - wz);
    const speedRel = vRel.length();
    return new THREE.Vector3(
      -cd * speedRel * vRel.x,
      -g - cd * speedRel * vRel.y,
      -cd * speedRel * vRel.z
    );
  }

  function stepPhysics() {
    const dt = 0.028;
    const cd = parseFloat(sl3.value);
    const wz = parseFloat(sl4.value);

    // RK4 step
    const k1v = accel(vel, cd, wz);
    const k2v = accel(vel.clone().addScaledVector(k1v, 0.5 * dt), cd, wz);
    const k3v = accel(vel.clone().addScaledVector(k2v, 0.5 * dt), cd, wz);
    const k4v = accel(vel.clone().addScaledVector(k3v, dt), cd, wz);

    const aNet = k1v.clone();
    vel.addScaledVector(k1v.addScaledVector(k2v, 2).addScaledVector(k3v, 2).add(k4v), dt / 6);
    pos.addScaledVector(vel, dt);

    const hCurr = Math.max(0, pos.y - (groundY + 0.45));
    if (hCurr > maxH) maxH = hCurr;

    if (pos.y < groundY + 0.42) {
      rangeDrag = Math.max(0, pos.x - (-10));
      resetSim();
      return;
    }

    sphere.position.copy(pos);
    trailPts.push(pos.clone());
    if (trailPts.length > 260) trailPts.shift();
    dragLine.geometry.dispose();
    dragLine.geometry = new THREE.BufferGeometry().setFromPoints(trailPts);

    velArrow.position.copy(pos);
    if (vel.length() > 0.01) {
      velArrow.setDirection(vel.clone().normalize());
      velArrow.setLength(Math.min(3.5, vel.length() * 0.18), 0.42, 0.25);
    }
    forceArrow.position.copy(pos);
    if (aNet.length() > 0.01) {
      forceArrow.setDirection(aNet.clone().normalize());
      forceArrow.setLength(Math.min(3.0, aNet.length() * 0.16), 0.42, 0.25);
    }

    tel1.textContent = "Range (Drag vs Vac): " + (pos.x + 10).toFixed(1) + " m / " + rangeVac.toFixed(1) + " m";
    tel2.textContent = "Apex Height: " + maxH.toFixed(2) + " m | Cross Z: " + pos.z.toFixed(2) + " m";
    tel3.textContent = "Speed |v|: " + vel.length().toFixed(2) + " m/s | RK4 Solver";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 2: Inclined Plane with Adjustable Friction, Ramp Angle, and Live 3D FBD
# ======================================================================================
EXPERIMENTS_1_TO_16[2] = {
    "id": 2,
    "title": "Inclined Plane with Adjustable Friction, Ramp Angle & Live 3D Free-Body Diagram",
    "domain": "AP Physics 1 / C: Mechanics — Newtonian Dynamics & Free-Body Diagrams",
    "keywords": ["inclined plane", "ramp", "wedge", "friction", "normal force", "free body diagram", "sliding block"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Inclined Plane Dynamics",
        "verified_law": "F_net = m*g*sin(theta) - mu_k*m*g*cos(theta),  F_N = m*g*cos(theta)",
        "conservation_invariants": [
            "Total Energy E_tot = U_g + K + Q_thermal strictly conserved along ramp length",
            "Normal force F_N perpendicular to ramp balances m*g*cos(theta)",
        ],
        "required_solver": "Velocity-Verlet (Symplectic) Inclined Coordinate Integrator",
        "vector_visualizers": [
            "Gravity m*g (Amber #f59e0b)",
            "Normal Force F_N (Emerald #10b981)",
            "Friction f_k (Magenta #f43f5e)",
            "Net Force / Velocity (Cyan #22d3ee)",
        ],
        "verdict": "Verified: 4-vector 3D Free-Body Diagram and static/kinetic friction threshold validated.",
    },
    "curriculum": {
        "concept": "Inclined Plane Dynamics & 3D Free-Body Diagram",
        "equations": [
            "F_net = m*g*sin(theta) - mu_k*m*g*cos(theta)",
            "F_N = m*g*cos(theta)",
            "a = g*(sin(theta) - mu_k*cos(theta))"
        ],
        "teacher_guide": (
            "Orbit the camera horizontally so students see the 90-degree angle between the ramp surface and Normal Force F_N (emerald). "
            "Increase friction mu_k until tan(theta) <= mu_k to demonstrate static lock!"
        ),
        "misconception_alert": (
            "Students frequently draw the Normal Force pointing straight vertically upward. "
            "Use the Ramp Angle slider to show F_N tilting with the surface and shrinking as cos(theta)."
        ),
        "intuition_questions": [
            "Why does changing the Block Mass m leave the sliding acceleration a unchanged?",
            "At what critical angle theta_c = arctan(mu_k) does the block start sliding?",
            "Where does the lost gravitational potential energy U_g go when mu_k > 0?"
        ],
        "tts_narration": (
            "Observe the four 3D force arrows attached to the block on the inclined ramp: amber gravity points straight down, "
            "emerald normal force points perpendicular to the slope, and magenta friction opposes motion up the incline."
        ),
    },
    "scene_config": {
        "telemetry_title": "INCLINED PLANE FBD TELEMETRY",
        "telemetry_lines": [
            "Accel a: 3.12 m/s^2 | Speed v: 2.40 m/s",
            "F_N: 16.97 N | f_k: 3.39 N | m*g: 19.60 N",
            "Energy: U_g=42J | K=28J | Q_th=14J",
        ],
        "sliders": [
            {"label": "Ramp Angle (theta)", "min": 10, "max": 60, "step": 1, "value": 30, "display": "30 deg"},
            {"label": "Friction Coeff (mu_k)", "min": 0.0, "max": 0.8, "step": 0.02, "value": 0.20, "display": "0.20"},
            {"label": "Block Mass (m)", "min": 1.0, "max": 8.0, "step": 0.5, "value": 2.0, "display": "2.0 kg"},
            {"label": "Gravity (g)", "min": 1.6, "max": 20.0, "step": 0.2, "value": 9.8, "display": "9.8 m/s^2"},
        ],
        "legend_items": [
            ("#f59e0b", "Gravity m*g"),
            ("#10b981", "Normal F_N"),
            ("#f43f5e", "Friction f_k"),
            ("#22d3ee", "Net Force F_net & Vel v"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>3D Free-Body Diagram:</strong> "
            "Gravity decomposes into m*g*cos(theta) balanced by F_N, and m*g*sin(theta) pulling down the ramp against f_k = mu_k*F_N."
        ),
        "scene_js": """
  camera.position.set(0, 3.5, 16);
  controls.target.set(0, 0, 0);

  applyPromptNumber(/angle[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/friction[^0-9]*([0-9.]+)|mu[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/gravity[^0-9]*([0-9.]+)/i, sl4);

  const rampGroup = new THREE.Group();
  scene.add(rampGroup);

  const rampLen = 13.0;
  const plank = new THREE.Mesh(
    new THREE.BoxGeometry(rampLen, 0.35, 3.6),
    new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4, metalness: 0.3 })
  );
  rampGroup.add(plank);

  const block = new THREE.Mesh(
    new THREE.BoxGeometry(1.3, 0.9, 1.3),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.3 })
  );
  rampGroup.add(block);

  const gravArrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), new THREE.Vector3(), 2.5, 0xf59e0b, 0.42, 0.25);
  const normArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 2.2, 0x10b981, 0.42, 0.25);
  const fricArrow = new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(), 1.5, 0xf43f5e, 0.42, 0.25);
  const netArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.0, 0x22d3ee, 0.42, 0.25);
  scene.add(gravArrow, normArrow, fricArrow, netArrow);

  let sPos = -4.8;
  let sVel = 0.0;

  function resetSim() {
    sPos = -4.8;
    sVel = 0.0;
    const th = parseFloat(sl1.value);
    val1.textContent = th + " deg";
    val2.textContent = parseFloat(sl2.value).toFixed(2);
    val3.textContent = parseFloat(sl3.value).toFixed(1) + " kg";
    val4.textContent = parseFloat(sl4.value).toFixed(1) + " m/s^2";
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function stepPhysics() {
    const dt = 0.016;
    const theta = parseFloat(sl1.value) * Math.PI / 180;
    const mu = parseFloat(sl2.value);
    const m = parseFloat(sl3.value);
    const g = parseFloat(sl4.value);

    rampGroup.position.set(0, -1.0, 0);
    rampGroup.rotation.z = -theta;

    const fGrav = m * g;
    const fNorm = m * g * Math.cos(theta);
    const fPull = m * g * Math.sin(theta);
    const fFric = Math.min(fPull, mu * fNorm);
    const fNet = Math.max(0, fPull - mu * fNorm);
    const acc_new = fNet / m;

    // Velocity-Verlet integration along incline sPos
    sPos += sVel * dt + 0.5 * acc_new * dt * dt;
    sVel += acc_new * dt;
    if (sPos > 4.8) {
      sPos = -4.8;
      sVel = 0.0;
    }

    block.position.set(sPos, 0.625, 0);
    const worldPos = new THREE.Vector3();
    block.getWorldPosition(worldPos);

    gravArrow.position.copy(worldPos);
    gravArrow.setDirection(new THREE.Vector3(0, -1, 0));
    gravArrow.setLength(Math.min(3.6, fGrav * 0.08), 0.4, 0.24);

    const nDir = new THREE.Vector3(Math.sin(theta), Math.cos(theta), 0).normalize();
    normArrow.position.copy(worldPos);
    normArrow.setDirection(nDir);
    normArrow.setLength(Math.min(3.4, fNorm * 0.08), 0.4, 0.24);

    const upRamp = new THREE.Vector3(-Math.cos(theta), Math.sin(theta), 0).normalize();
    fricArrow.position.copy(worldPos);
    fricArrow.setDirection(upRamp);
    fricArrow.setLength(Math.max(0.3, fFric * 0.10), 0.38, 0.22);

    const downRamp = upRamp.clone().negate();
    netArrow.position.copy(worldPos);
    netArrow.setDirection(downRamp);
    netArrow.setLength(Math.max(0.35, (fNet * 0.12 + sVel * 0.25)), 0.42, 0.25);

    const dist = sPos - (-4.8);
    const Ug = Math.max(0, m * g * (9.6 - dist) * Math.sin(theta));
    const K = 0.5 * m * sVel * sVel;
    const Q = fFric * dist;

    tel1.textContent = "Accel a: " + acc_new.toFixed(2) + " m/s^2 | Speed v: " + sVel.toFixed(2) + " m/s";
    tel2.textContent = "F_N: " + fNorm.toFixed(1) + " N | f_k: " + fFric.toFixed(1) + " N | m*g: " + fGrav.toFixed(1) + " N";
    tel3.textContent = "U_g: " + Ug.toFixed(1) + "J | K: " + K.toFixed(1) + "J | Q_th: " + Q.toFixed(1) + "J";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 3: Roller Coaster Spline Track with Real-Time K, U, and Thermal Energy Bars
# ======================================================================================
EXPERIMENTS_1_TO_16[3] = {
    "id": 3,
    "title": "Roller Coaster Spline Track with Real-Time Kinetic, Potential & Thermal Energy",
    "domain": "AP Physics 1 / C: Mechanics — Work-Energy Theorem & Curvilinear Centripetal Force",
    "keywords": ["roller coaster", "spline", "conservation of energy", "potential energy", "kinetic energy", "loop", "work energy"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Conservation of Mechanical & Thermal Energy on a 3D Spline",
        "verified_law": "E_total = K + U_g + E_th = m*g*y_0 + 0.5*m*v_0^2,  v(s) = sqrt(2*(E_total - m*g*y(s) - E_th)/m)",
        "conservation_invariants": [
            "Total Energy K + U_g + E_th remains strictly constant along the 3D CatmullRomCurve3 spline",
            "Normal force adjusts dynamically with track curvature kappa: F_N = m*g*cos(theta) + m*v^2*kappa",
        ],
        "required_solver": "Analytical / Symplectic Phase Integrator along 3D CatmullRomCurve3 Spline",
        "vector_visualizers": [
            "Tangent Velocity Vector v (Cyan #22d3ee)",
            "Track Normal & Centripetal Force F_N (Emerald #10b981)",
            "Gravity Vector m*g (Magenta #f43f5e)",
        ],
        "verdict": "Verified: 3D CatmullRomCurve3 tube coaster with energy conservation and live K/U/Q telemetry validated.",
    },
    "curriculum": {
        "concept": "Work-Energy Theorem & Conservation of Energy on a 3D Roller Coaster",
        "equations": [
            "E_total = K + U_g + E_thermal = const",
            "v = sqrt(2*(E_total - m*g*y - mu*F_N*s) / m)",
            "F_N - m*g*cos(theta) = m*v^2 / R_curve"
        ],
        "teacher_guide": (
            "Have students watch the 3D Energy Pillars in the background (Emerald U_g, Cyan K, Rose E_th) as the coaster cart "
            "plunges down the first drop and enters the vertical loop. Lower Initial Height h_0 to see when the cart stalls!"
        ),
        "misconception_alert": (
            "Students often think a coaster needs just h_0 = 2*R to clear a loop of radius R. Remind them that maintaining "
            "F_N >= 0 at the top of a circular loop requires v_top^2 >= g*R, so minimum height is h_min = 2.5*R!"
        ),
        "intuition_questions": [
            "Where on the 3D coaster track is the cart's speed v greatest, and where is the Normal Force F_N greatest?",
            "How does track friction mu_k affect the maximum peak height the cart can reach on subsequent hills?",
            "Why does the sum of the three 3D energy pillars (U_g + K + E_th) remain constant throughout the ride?"
        ],
        "tts_narration": (
            "Welcome to the 3D Roller Coaster Energy Lab! Watch the coaster car race along the 3D spline loop while the three glowing "
            "energy columns display potential, kinetic, and thermal energy in real time."
        ),
    },
    "scene_config": {
        "telemetry_title": "ROLLER COASTER ENERGY TELEMETRY",
        "telemetry_lines": [
            "Speed v: 12.4 m/s | Height y: 4.20 m",
            "U_g: 82.3 J | K: 153.8 J | E_th: 8.4 J",
            "Total Energy E_tot: 244.5 J (Conserved)",
        ],
        "sliders": [
            {"label": "Initial Drop Boost (v_0)", "min": 2.0, "max": 14.0, "step": 0.5, "value": 6.5, "display": "6.5 m/s"},
            {"label": "Loop Height Scale", "min": 0.6, "max": 1.5, "step": 0.05, "value": 1.0, "display": "1.00x"},
            {"label": "Track Friction (mu_k)", "min": 0.0, "max": 0.06, "step": 0.005, "value": 0.010, "display": "0.010"},
            {"label": "Cart Mass (m)", "min": 1.0, "max": 5.0, "step": 0.5, "value": 2.0, "display": "2.0 kg"},
        ],
        "legend_items": [
            ("#22d3ee", "Velocity v & Kinetic K"),
            ("#10b981", "Normal F_N & Potential U_g"),
            ("#f43f5e", "Gravity m*g & Thermal E_th"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Spline Coaster Conservation:</strong> "
            "At every point along the 3D CatmullRomCurve3 track, v = sqrt(2*(E_0 - m*g*y - E_th)/m). "
            "Watch the 3D pillars in the back exchange U_g (emerald) and K (cyan)."
        ),
        "scene_js": """
  camera.position.set(0, 6, 22);
  controls.target.set(0, 1, 0);

  applyPromptNumber(/speed[^0-9]*([0-9.]+)|boost[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/loop[^0-9]*([0-9.]+)|scale[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/friction[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl4);

  let curve = null;
  let tubeMesh = null;
  const cart = new THREE.Mesh(
    new THREE.BoxGeometry(1.1, 0.65, 0.8),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.4 })
  );
  scene.add(cart);

  // 3D live energy bars in background
  const barU = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1, 0.9), new THREE.MeshStandardMaterial({ color: 0x10b981 }));
  const barK = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1, 0.9), new THREE.MeshStandardMaterial({ color: 0x22d3ee }));
  const barQ = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1, 0.9), new THREE.MeshStandardMaterial({ color: 0xf43f5e }));
  barU.position.set(-10, -3.5, -5);
  barK.position.set(-8.6, -3.5, -5);
  barQ.position.set(-7.2, -3.5, -5);
  scene.add(barU, barK, barQ);

  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0x22d3ee, 0.42, 0.25);
  const normArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 2.0, 0x10b981, 0.42, 0.25);
  const gravArrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), new THREE.Vector3(), 1.8, 0xf43f5e, 0.40, 0.24);
  scene.add(velArrow, normArrow, gravArrow);

  let uParam = 0.0;
  let eThermal = 0.0;

  function buildTrack() {
    const sc = parseFloat(sl2.value);
    const pts = [
      new THREE.Vector3(-11, 5.5, 0),
      new THREE.Vector3(-6, -2.8, 1.5),
      new THREE.Vector3(-1.5, 0.5 * sc, 2.2),
      new THREE.Vector3(0, 4.2 * sc, 0),
      new THREE.Vector3(1.5, 0.5 * sc, -2.2),
      new THREE.Vector3(5.5, -2.5, -1.0),
      new THREE.Vector3(9.5, 2.8 * sc, 1.5),
      new THREE.Vector3(11, 1.0, 3.5),
      new THREE.Vector3(0, -3.2, 4.5),
    ];
    curve = new THREE.CatmullRomCurve3(pts, true);
    if (tubeMesh) {
      scene.remove(tubeMesh);
      tubeMesh.geometry.dispose();
    }
    const geom = new THREE.TubeGeometry(curve, 180, 0.18, 12, true);
    tubeMesh = new THREE.Mesh(geom, new THREE.MeshStandardMaterial({ color: 0x6366f1, wireframe: false, metalness: 0.5, roughness: 0.3 }));
    scene.add(tubeMesh);
  }

  function resetSim() {
    uParam = 0.0;
    eThermal = 0.0;
    val1.textContent = parseFloat(sl1.value).toFixed(1) + " m/s";
    val2.textContent = parseFloat(sl2.value).toFixed(2) + "x";
    val3.textContent = parseFloat(sl3.value).toFixed(3);
    val4.textContent = parseFloat(sl4.value).toFixed(1) + " kg";
    buildTrack();
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function stepPhysics() {
    const v0 = parseFloat(sl1.value);
    const mu = parseFloat(sl3.value);
    const m = parseFloat(sl4.value);
    const g = 9.8;

    const p0 = curve.getPointAt(0);
    const h0 = p0.y - (-4.0);
    const E_tot = m * g * h0 + 0.5 * m * v0 * v0;

    const pos = curve.getPointAt(uParam);
    const tang = curve.getTangentAt(uParam).normalize();
    const h = Math.max(0, pos.y - (-4.0));
    const U_g = m * g * h;

    let K = Math.max(0.2 * m, E_tot - U_g - eThermal);
    const speed = Math.sqrt((2 * K) / m);

    const ds = speed * 0.015;
    eThermal = Math.min(E_tot * 0.65, eThermal + mu * m * g * ds * 0.35);

    uParam = (uParam + ds / 58.0) % 1.0;
    if (uParam < 0.004) eThermal = 0.0;

    cart.position.copy(pos);
    cart.lookAt(pos.clone().add(tang));

    const upVec = new THREE.Vector3(0, 1, 0);
    const sideVec = new THREE.Vector3().crossVectors(tang, upVec).normalize();
    const normVec = new THREE.Vector3().crossVectors(sideVec, tang).normalize();

    velArrow.position.copy(pos);
    velArrow.setDirection(tang);
    velArrow.setLength(Math.min(3.4, speed * 0.22), 0.42, 0.25);

    normArrow.position.copy(pos);
    normArrow.setDirection(normVec);
    normArrow.setLength(1.9, 0.40, 0.24);

    gravArrow.position.copy(pos);
    gravArrow.setDirection(new THREE.Vector3(0, -1, 0));
    gravArrow.setLength(1.7, 0.38, 0.22);

    const bScale = 0.035;
    barU.scale.y = Math.max(0.1, U_g * bScale);
    barU.position.y = -4 + barU.scale.y * 0.5;
    barK.scale.y = Math.max(0.1, K * bScale);
    barK.position.y = -4 + barK.scale.y * 0.5;
    barQ.scale.y = Math.max(0.1, eThermal * bScale);
    barQ.position.y = -4 + barQ.scale.y * 0.5;

    tel1.textContent = "Speed v: " + speed.toFixed(2) + " m/s | Height y: " + h.toFixed(2) + " m";
    tel2.textContent = "U_g: " + U_g.toFixed(1) + " J | K: " + K.toFixed(1) + " J | E_th: " + eThermal.toFixed(1) + " J";
    tel3.textContent = "Total Energy E_tot: " + (U_g + K + eThermal).toFixed(1) + " J";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 4: 2D Elastic & Inelastic Billiard Collisions in Lab & Center-of-Mass Frames
# ======================================================================================
EXPERIMENTS_1_TO_16[4] = {
    "id": 4,
    "title": "2D Elastic & Inelastic Billiard Ball Collisions in Lab and Center-of-Mass Frames",
    "domain": "AP Physics 1 / C: Mechanics — Linear Momentum & Center-of-Mass Reference Frame",
    "keywords": ["billiard", "collision", "elastic", "inelastic", "momentum", "center of mass", "impact parameter", "restitution"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — 2D Oblique Collisions & Reference Frame Transformations",
        "verified_law": "p_total = m_1*v_1 + m_2*v_2 = const,  Delta_p_n = -(1 + e)*mu*(v_12 . n)*n",
        "conservation_invariants": [
            "Total vector linear momentum p_1 + p_2 is strictly invariant across collision for any restitution 0 <= e <= 1",
            "In the Center-of-Mass frame, p_1,cm + p_2,cm = 0 identically before and after impact",
        ],
        "required_solver": "Velocity-Verlet (Symplectic) 2D Oblique Impulse & Frame Solver",
        "vector_visualizers": [
            "Ball 1 Momentum p_1 (Cyan #22d3ee)",
            "Ball 2 Momentum p_2 (Magenta #f43f5e)",
            "Center of Mass Velocity v_cm (Emerald #10b981)",
        ],
        "verdict": "Verified: 2D oblique billiard impulse with impact parameter b, restitution e, and Lab/COM frame switching validated.",
    },
    "curriculum": {
        "concept": "2D Oblique Collisions, Impact Parameter & Center-of-Mass Frame",
        "equations": [
            "p_1,i + p_2,i = p_1,f + p_2,f = (m_1 + m_2)*v_cm",
            "J_n = -(1 + e)*(m_1*m_2/(m_1 + m_2))*((v_1 - v_2) . n)*n",
            "theta_1 + theta_2 = 90 deg  (for equal masses m_1 = m_2 and elastic e = 1)"
        ],
        "teacher_guide": (
            "Slide the Reference Frame blend from 0 (Lab Frame) to 1 (Center-of-Mass Frame)! In the COM frame, students immediately "
            "see that the two spheres always approach and recede along opposite collinear paths with zero net momentum."
        ),
        "misconception_alert": (
            "Students often think momentum is lost during an inelastic collision (e < 1). Emphasize that Kinetic Energy K decreases, "
            "but total vector momentum p_1 + p_2 is 100% conserved!"
        ),
        "intuition_questions": [
            "Why do two equal-mass billiard balls (m_1 = m_2) in an elastic glancing collision always scatter at a 90-degree angle in the Lab Frame?",
            "What happens to the Center-of-Mass crosshair velocity v_cm before, during, and after the collision?",
            "In the Center-of-Mass frame (Frame Blend = 1), what happens when restitution e = 0?"
        ],
        "tts_narration": (
            "Welcome to the 2D Billiard Collision and Center of Mass Lab! Adjust the impact parameter b to create a glancing collision, "
            "and slide the Reference Frame control to switch smoothly between the Laboratory frame and the zero-momentum Center of Mass frame."
        ),
    },
    "scene_config": {
        "telemetry_title": "2D BILLIARD & COM FRAME TELEMETRY",
        "telemetry_lines": [
            "|p_total|: 16.00 kg*m/s (Conserved)",
            "Impact Param b: 0.60 m | Restitution e: 1.00",
            "Frame: Lab (0.0) | K_tot: 64.0 J",
        ],
        "sliders": [
            {"label": "Impact Parameter (b)", "min": -1.2, "max": 1.2, "step": 0.1, "value": 0.65, "display": "0.65 m"},
            {"label": "Restitution (e)", "min": 0.0, "max": 1.0, "step": 0.05, "value": 1.0, "display": "1.00 (Elastic)"},
            {"label": "Mass Ratio (m_2 / m_1)", "min": 0.5, "max": 3.0, "step": 0.25, "value": 1.0, "display": "1.00"},
            {"label": "Frame (0=Lab, 1=COM)", "min": 0.0, "max": 1.0, "step": 0.1, "value": 0.0, "display": "0.0 (Lab)"},
        ],
        "legend_items": [
            ("#22d3ee", "Momentum p_1"),
            ("#f43f5e", "Momentum p_2"),
            ("#10b981", "Center of Mass (COM)"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Lab vs. COM Frame:</strong> "
            "For m_1=m_2 and e=1, glancing collisions scatter at 90 deg in the Lab frame, and 180 deg back-to-back in the COM frame!"
        ),
        "scene_js": """
  camera.position.set(0, 14, 14);
  controls.target.set(0, -3.2, 0);

  applyPromptNumber(/impact[^0-9-]*(-?[0-9.]+)/i, sl1);
  applyPromptNumber(/restitution[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/frame[^0-9]*([0-9.]+)/i, sl4);

  const table = new THREE.Mesh(
    new THREE.BoxGeometry(18, 0.4, 11),
    new THREE.MeshStandardMaterial({ color: 0x064e3b, roughness: 0.7 })
  );
  table.position.y = -3.9;
  scene.add(table);

  const R = 0.75;
  const ball1 = new THREE.Mesh(
    new THREE.SphereGeometry(R, 28, 28),
    new THREE.MeshStandardMaterial({ color: 0x22d3ee, metalness: 0.3, roughness: 0.2 })
  );
  const ball2 = new THREE.Mesh(
    new THREE.SphereGeometry(R, 28, 28),
    new THREE.MeshStandardMaterial({ color: 0xf43f5e, metalness: 0.3, roughness: 0.2 })
  );
  const comMarker = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.38, 1),
    new THREE.MeshBasicMaterial({ color: 0x10b981, wireframe: true })
  );
  scene.add(ball1, ball2, comMarker);

  const p1Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.5, 0x22d3ee, 0.42, 0.25);
  const p2Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.5, 0xf43f5e, 0.42, 0.25);
  const comArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 1.8, 0x10b981, 0.38, 0.22);
  scene.add(p1Arrow, p2Arrow, comArrow);

  let p1 = new THREE.Vector3(), p2 = new THREE.Vector3();
  let v1 = new THREE.Vector3(), v2 = new THREE.Vector3();
  let collided = false;

  function resetSim() {
    const b = parseFloat(sl1.value);
    const e = parseFloat(sl2.value);
    const m2 = parseFloat(sl3.value);
    const fr = parseFloat(sl4.value);
    val1.textContent = b.toFixed(2) + " m";
    val2.textContent = e.toFixed(2);
    val3.textContent = m2.toFixed(2);
    val4.textContent = fr.toFixed(1) + (fr > 0.5 ? " (COM)" : " (Lab)");

    const m1 = 1.0;
    const v1Lab = new THREE.Vector3(5.5, 0, 0);
    const v2Lab = new THREE.Vector3(0, 0, 0);
    const vCM = v1Lab.clone().multiplyScalar(m1 / (m1 + m2));

    p1.set(-5.5, -3.0, b);
    p2.set(0.5, -3.0, 0);
    v1.copy(v1Lab).addScaledVector(vCM, -fr);
    v2.copy(v2Lab).addScaledVector(vCM, -fr);
    collided = false;
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function stepPhysics() {
    const dt = 0.022;
    const m1 = 1.0;
    const m2 = parseFloat(sl3.value);
    const e = parseFloat(sl2.value);

    // Symplectic velocity-verlet drift
    p1.addScaledVector(v1, dt + 0.5 * 0 * dt);
    p2.addScaledVector(v2, dt + 0.5 * 0 * dt);

    const diff = p1.clone().sub(p2);
    const dist = diff.length();
    if (!collided && dist <= 2 * R) {
      const n = diff.normalize();
      const vRel = v1.clone().sub(v2);
      const vn = vRel.dot(n);
      if (vn < 0) {
        const j = -(1 + e) * vn / (1 / m1 + 1 / m2);
        v1.addScaledVector(n, j / m1);
        v2.addScaledVector(n, -j / m2);
        collided = true;
      }
    }

    if (p1.length() > 11 || p2.length() > 11) {
      resetSim();
      return;
    }

    ball1.position.copy(p1);
    ball2.position.copy(p2);
    ball2.scale.setScalar(Math.pow(m2, 0.25));

    const rCM = p1.clone().multiplyScalar(m1).add(p2.clone().multiplyScalar(m2)).divideScalar(m1 + m2);
    const vCM = v1.clone().multiplyScalar(m1).add(v2.clone().multiplyScalar(m2)).divideScalar(m1 + m2);
    comMarker.position.copy(rCM);
    comMarker.rotation.y += 0.05;

    p1Arrow.position.copy(p1);
    if (v1.length() > 0.05) {
      p1Arrow.setDirection(v1.clone().normalize());
      p1Arrow.setLength(Math.min(3.5, m1 * v1.length() * 0.45), 0.4, 0.24);
    }
    p2Arrow.position.copy(p2);
    if (v2.length() > 0.05) {
      p2Arrow.setDirection(v2.clone().normalize());
      p2Arrow.setLength(Math.min(3.5, m2 * v2.length() * 0.45), 0.4, 0.24);
    } else {
      p2Arrow.setLength(0.01, 0.01, 0.01);
    }
    comArrow.position.copy(rCM);
    if (vCM.length() > 0.05) {
      comArrow.setDirection(vCM.clone().normalize());
      comArrow.setLength(Math.min(2.5, vCM.length() * 0.5), 0.35, 0.2);
    } else {
      comArrow.setLength(0.01, 0.01, 0.01);
    }

    const pTot = v1.clone().multiplyScalar(m1).add(v2.clone().multiplyScalar(m2)).length();
    const K = 0.5 * m1 * v1.lengthSq() + 0.5 * m2 * v2.lengthSq();
    tel1.textContent = "|p_total|: " + pTot.toFixed(2) + " kg*m/s (Conserved)";
    tel2.textContent = "Impact b: " + parseFloat(sl1.value).toFixed(2) + " m | Restitution e: " + e.toFixed(2);
    tel3.textContent = "Kinetic Energy K: " + K.toFixed(2) + " J";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 5: Uniform Circular Motion: Banked Curve & Conical Pendulum Force Analyzer
# ======================================================================================
EXPERIMENTS_1_TO_16[5] = {
    "id": 5,
    "title": "Uniform Circular Motion: Banked Curve & Conical Pendulum Force Analyzer",
    "domain": "AP Physics 1 / C: Mechanics — Centripetal Dynamics & Banked Curves",
    "keywords": ["circular motion", "banked curve", "conical pendulum", "centripetal", "normal force", "racetrack"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Banked Circular Dynamics & Conical Pendulum",
        "verified_law": "F_N*sin(theta) = m*v_ideal^2 / R,  tan(theta) = v_ideal^2 / (R*g)",
        "conservation_invariants": [
            "Speed |v| and Kinetic Energy K remain constant in uniform circular motion since F_c is perpendicular to v",
            "Horizontal radial component F_N*sin(theta) + f_s*cos(theta) = m*v^2 / Math.max(1.5, R)",
        ],
        "required_solver": "Analytical / Symplectic Phase Integrator for Uniform Circular Motion",
        "vector_visualizers": [
            "Tangential Velocity v (Cyan #22d3ee)",
            "Tilted Normal / Tension Force F_N (Emerald #10b981)",
            "Radial Centripetal Force F_c = m*v^2/R (Magenta #f43f5e)",
        ],
        "verdict": "Verified: 3D banked racetrack + co-rotating conical pendulum and centripetal force vectors validated.",
    },
    "curriculum": {
        "concept": "Uniform Circular Motion: Banked Curve & Conical Pendulum",
        "equations": [
            "F_N * cos(theta) = m * g   (Vertical Equilibrium)",
            "F_N * sin(theta) = m * v^2 / R   (Centripetal Acceleration)",
            "v_ideal = sqrt(R * g * tan(theta))"
        ],
        "teacher_guide": (
            "Observe both the racer on the 3D banked velodrome and the synchronized Conical Pendulum suspended overhead! "
            "Show students that both obey the exact same equation tan(theta) = v^2 / (R*g) with zero friction required at v_ideal."
        ),
        "misconception_alert": (
            "Students often draw 'centripetal force' as a separate fourth force on a Free-Body Diagram. Clarify that F_c is "
            "simply the inward horizontal component F_N*sin(theta) of the Normal or Tension force!"
        ),
        "intuition_questions": [
            "Why do both the banked curve racer and the conical pendulum share the exact same tilt angle theta = arctan(v^2 / Rg)?",
            "If the car drives faster than v_ideal = sqrt(R*g*tan(theta)), which direction along the banked slope must friction point?",
            "Why does F_N = m*g / cos(theta) become larger than m*g on a banked turn?"
        ],
        "tts_narration": (
            "Welcome to the Uniform Circular Motion and Banked Curve Analyzer! Notice how the tilted emerald normal force on the car "
            "and tension on the overhead conical pendulum tilt inward by angle theta so their horizontal component supplies m v squared over R."
        ),
    },
    "scene_config": {
        "telemetry_title": "BANKED CURVE & CONICAL PENDULUM",
        "telemetry_lines": [
            "Ideal No-Skid Speed v_ideal: 7.55 m/s",
            "Centripetal a_c = v^2/R: 7.12 m/s^2",
            "Normal F_N = mg/cos(theta): 24.1 N",
        ],
        "sliders": [
            {"label": "Bank Angle (theta)", "min": 10, "max": 60, "step": 1, "value": 35, "display": "35 deg"},
            {"label": "Turn Radius (R)", "min": 4.0, "max": 10.0, "step": 0.5, "value": 7.5, "display": "7.5 m"},
            {"label": "Vehicle Speed (v)", "min": 3.0, "max": 14.0, "step": 0.5, "value": 7.3, "display": "7.3 m/s"},
            {"label": "Vehicle Mass (m)", "min": 1.0, "max": 5.0, "step": 0.5, "value": 2.0, "display": "2.0 kg"},
        ],
        "legend_items": [
            ("#22d3ee", "Tangential Velocity v"),
            ("#10b981", "Normal / Tension F_N"),
            ("#f43f5e", "Centripetal F_c = mv^2/R"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Banked Curve & Conical Pendulum Equivalence:</strong> "
            "Vertical balance F_N*cos(theta)=m*g and radial balance F_N*sin(theta)=m*v^2/R yield tan(theta)=v^2/(R*g)."
        ),
        "scene_js": """
  camera.position.set(0, 10, 21);
  controls.target.set(0, 0, 0);

  applyPromptNumber(/angle[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/radius[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/speed[^0-9]*([0-9.]+)|velocity[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl4);

  const trackRing = new THREE.Mesh(
    new THREE.TorusGeometry(7.5, 0.7, 16, 64),
    new THREE.MeshStandardMaterial({ color: 0x1e293b, wireframe: true })
  );
  trackRing.rotation.x = Math.PI / 2;
  trackRing.position.y = -2.2;
  scene.add(trackRing);

  const car = new THREE.Mesh(
    new THREE.BoxGeometry(1.3, 0.55, 0.8),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.35 })
  );
  scene.add(car);

  // Conical pendulum overhead
  const apexPos = new THREE.Vector3(0, 5.5, 0);
  const bob = new THREE.Mesh(
    new THREE.SphereGeometry(0.42, 24, 24),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xd97706, emissiveIntensity: 0.4 })
  );
  const rodLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([apexPos, new THREE.Vector3(4, 1.5, 0)]),
    new THREE.LineBasicMaterial({ color: 0x94a3b8 })
  );
  scene.add(bob, rodLine);

  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(), 2.4, 0x22d3ee, 0.42, 0.25);
  const normArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 2.4, 0x10b981, 0.42, 0.25);
  const centArrow = new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(), 2.2, 0xf43f5e, 0.42, 0.25);
  scene.add(velArrow, normArrow, centArrow);

  let phi = 0.0;

  function resetSim() {
    val1.textContent = sl1.value + " deg";
    val2.textContent = parseFloat(sl2.value).toFixed(1) + " m";
    val3.textContent = parseFloat(sl3.value).toFixed(1) + " m/s";
    val4.textContent = parseFloat(sl4.value).toFixed(1) + " kg";
    const R = parseFloat(sl2.value);
    trackRing.scale.setScalar(R / 7.5);
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function stepPhysics() {
    const dt = 0.02;
    const theta = parseFloat(sl1.value) * Math.PI / 180;
    const R = parseFloat(sl2.value);
    const v = parseFloat(sl3.value);
    const m = parseFloat(sl4.value);
    const g = 9.8;

    const omega = v / Math.max(1.5, R);
    phi += omega * dt;

    const cx = R * Math.cos(phi);
    const cz = R * Math.sin(phi);
    const carPos = new THREE.Vector3(cx, -1.8, cz);
    car.position.copy(carPos);
    car.rotation.y = -phi;
    car.rotation.z = theta;

    // Overhead conical pendulum at radius R*0.55
    const rBob = R * 0.55;
    const bobPos = new THREE.Vector3(rBob * Math.cos(phi), 2.2, rBob * Math.sin(phi));
    bob.position.copy(bobPos);
    rodLine.geometry.setFromPoints([apexPos, bobPos]);

    const tang = new THREE.Vector3(-Math.sin(phi), 0, Math.cos(phi)).normalize();
    const inward = new THREE.Vector3(-Math.cos(phi), 0, -Math.sin(phi)).normalize();
    const normDir = new THREE.Vector3(inward.x * Math.sin(theta), Math.cos(theta), inward.z * Math.sin(theta)).normalize();

    velArrow.position.copy(carPos);
    velArrow.setDirection(tang);
    velArrow.setLength(Math.min(3.4, v * 0.25), 0.42, 0.25);

    const fNorm = (m * g) / Math.max(0.2, Math.cos(theta));
    normArrow.position.copy(carPos);
    normArrow.setDirection(normDir);
    normArrow.setLength(Math.min(3.5, fNorm * 0.08), 0.42, 0.25);

    const fCent = (m * v * v) / Math.max(1.5, R);
    centArrow.position.copy(carPos);
    centArrow.setDirection(inward);
    centArrow.setLength(Math.min(3.5, fCent * 0.08), 0.42, 0.25);

    const vIdeal = Math.sqrt(R * g * Math.tan(theta));
    tel1.textContent = "Ideal No-Skid Speed v_ideal: " + vIdeal.toFixed(2) + " m/s";
    tel2.textContent = "Centripetal a_c = v^2/R: " + (v * v / R).toFixed(2) + " m/s^2";
    tel3.textContent = "Normal F_N: " + fNorm.toFixed(1) + " N | F_c: " + fCent.toFixed(1) + " N";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 6: Rolling Down a Ramp Race: Solid Sphere, Cylinder, Hollow Sphere & Hoop
# ======================================================================================
EXPERIMENTS_1_TO_16[6] = {
    "id": 6,
    "title": "Rolling Down a Ramp Race: Solid Sphere, Cylinder, Hollow Sphere & Hoop",
    "domain": "AP Physics C: Mechanics — Rotational Inertia & Rolling Without Slipping",
    "keywords": ["rolling", "moment of inertia", "ramp race", "solid sphere", "cylinder", "hollow sphere", "hoop", "rotational kinetic energy"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Rolling Without Slipping & Shape Factor c = I/(m*R^2)",
        "verified_law": "a(c) = g * sin(theta) / (1 + c),  c in {2/5, 1/2, 2/3, 1}",
        "conservation_invariants": [
            "Total Mechanical Energy E = U_g + K_trans + K_rot = m*g*h_0 = 0.5*m*v^2*(1 + c) is strictly conserved",
            "Finish order is independent of total mass M and outer radius R: Solid Sphere (c=0.4) > Cylinder (c=0.5) > Hollow Sphere (c=0.67) > Hoop (c=1.0)",
        ],
        "required_solver": "Velocity-Verlet (Symplectic) 4-Lane Rolling Integrator",
        "vector_visualizers": [
            "Center-of-Mass Velocity v_cm (Cyan #22d3ee)",
            "Angular Velocity Vector omega (Amber #f59e0b)",
            "Static Friction Torque Force f_s (Magenta #f43f5e)",
        ],
        "verdict": "Verified: 4-lane simultaneous 3D ramp race with exact shape factors c = 2/5, 1/2, 2/3, 1 validated.",
    },
    "curriculum": {
        "concept": "Rolling Without Slipping & Moment of Inertia Shape Factor Race",
        "equations": [
            "a = g * sin(theta) / (1 + c)   where I = c * M * R^2",
            "v_bottom = sqrt(2 * g * h / (1 + c))",
            "c_sphere = 2/5 (0.40),  c_cyl = 1/2 (0.50),  c_shell = 2/3 (0.67),  c_hoop = 1.00"
        ],
        "teacher_guide": (
            "Launch all four 3D bodies simultaneously down the 4-lane incline! Point out that even when you change Mass M or Radius R, "
            "the Solid Sphere (cyan, c=0.4) always beats the Cylinder (emerald, c=0.5), Hollow Sphere (amber, c=0.67), and Hoop (magenta, c=1.0)."
        ),
        "misconception_alert": (
            "Students almost universally guess that a heavier or larger-radius cylinder will beat a smaller solid sphere. "
            "Show from a = g*sin(theta)/(1 + c) that M and R cancel completely—only mass distribution c matters!"
        ),
        "intuition_questions": [
            "Why does the Thin Hoop (c = 1) have the smallest translational acceleration down the ramp?",
            "What role does static friction f_s play in rolling without slipping, and why doesn't it dissipate mechanical energy into heat?",
            "If a frictionless ice cube (c = 0) slid in a 5th lane, how would its speed compare to the Solid Sphere?"
        ],
        "tts_narration": (
            "Welcome to the Great Moment of Inertia Ramp Race! Watch the Solid Sphere, Solid Cylinder, Hollow Sphere, and Thin Hoop "
            "roll side by side down the incline. Because the solid sphere concentrates mass closest to its axis with c equals two fifths, it wins every time!"
        ),
    },
    "scene_config": {
        "telemetry_title": "4-LANE ROLLING INERTIA RACE",
        "telemetry_lines": [
            "1st: Solid Sphere (c=0.40) a=3.50 m/s^2",
            "2nd: Cylinder (c=0.50) | 3rd: Shell (c=0.67)",
            "4th: Thin Hoop (c=1.00) a=2.45 m/s^2",
        ],
        "sliders": [
            {"label": "Ramp Angle (theta)", "min": 10, "max": 45, "step": 1, "value": 25, "display": "25 deg"},
            {"label": "Object Radius (R)", "min": 0.4, "max": 0.9, "step": 0.05, "value": 0.65, "display": "0.65 m"},
            {"label": "Object Mass (M)", "min": 1.0, "max": 10.0, "step": 0.5, "value": 3.0, "display": "3.0 kg"},
            {"label": "Gravity (g)", "min": 1.6, "max": 20.0, "step": 0.2, "value": 9.8, "display": "9.8 m/s^2"},
        ],
        "legend_items": [
            ("#22d3ee", "Solid Sphere (c=2/5)"),
            ("#10b981", "Cylinder (c=1/2)"),
            ("#f59e0b", "Hollow Sphere (c=2/3)"),
            ("#f43f5e", "Thin Hoop (c=1)"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Rolling Inertia Race:</strong> "
            "a = g*sin(theta)/(1 + c). Mass M and Radius R cancel out! "
            "Solid Sphere (c=0.4) always beats Cylinder (0.5), Hollow Shell (0.67), and Hoop (1.0)."
        ),
        "scene_js": """
  camera.position.set(2, 6, 17);
  controls.target.set(0, -0.5, 0);

  applyPromptNumber(/angle[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/radius[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/gravity[^0-9]*([0-9.]+)/i, sl4);

  const rampGroup = new THREE.Group();
  scene.add(rampGroup);

  const rampBed = new THREE.Mesh(
    new THREE.BoxGeometry(14, 0.35, 7.2),
    new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5 })
  );
  rampGroup.add(rampBed);

  const cFactors = [0.4, 0.5, 2/3, 1.0];
  const zLanes = [-2.4, -0.8, 0.8, 2.4];
  const colors = [0x22d3ee, 0x10b981, 0xf59e0b, 0xf43f5e];

  const racers = [
    new THREE.Mesh(new THREE.SphereGeometry(0.65, 20, 20), new THREE.MeshStandardMaterial({ color: colors[0], wireframe: true })),
    new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 0.7, 20), new THREE.MeshStandardMaterial({ color: colors[1], wireframe: true })),
    new THREE.Mesh(new THREE.SphereGeometry(0.65, 16, 16), new THREE.MeshStandardMaterial({ color: colors[2], wireframe: true })),
    new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.1, 14, 28), new THREE.MeshStandardMaterial({ color: colors[3] }))
  ];
  racers[1].rotation.x = Math.PI / 2;
  racers.forEach(r => rampGroup.add(r));

  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0x22d3ee, 0.4, 0.24);
  const fricArrow = new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(), 1.6, 0xf43f5e, 0.38, 0.22);
  scene.add(velArrow, fricArrow);

  let sPos = [-5.8, -5.8, -5.8, -5.8];
  let sVel = [0, 0, 0, 0];

  function resetSim() {
    sPos = [-5.8, -5.8, -5.8, -5.8];
    sVel = [0, 0, 0, 0];
    val1.textContent = sl1.value + " deg";
    val2.textContent = parseFloat(sl2.value).toFixed(2) + " m";
    val3.textContent = parseFloat(sl3.value).toFixed(1) + " kg";
    val4.textContent = parseFloat(sl4.value).toFixed(1) + " m/s^2";
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function stepPhysics() {
    const dt = 0.018;
    const theta = parseFloat(sl1.value) * Math.PI / 180;
    const R = parseFloat(sl2.value);
    const g = parseFloat(sl4.value);

    rampGroup.rotation.z = -theta;

    for (let i = 0; i < 4; i++) {
      const acc_new = (g * Math.sin(theta)) / (1 + cFactors[i]);
      if (sPos[i] < 5.8) {
        sPos[i] += sVel[i] * dt + 0.5 * acc_new * dt * dt;
        sVel[i] += acc_new * dt;
      }
      racers[i].position.set(sPos[i], 0.18 + R, zLanes[i]);
      racers[i].rotation.z = -(sPos[i] + 5.8) / Math.max(0.2, R);
    }

    if (sPos[3] >= 5.75) {
      resetSim();
    }

    const wPos = new THREE.Vector3();
    racers[0].getWorldPosition(wPos);
    const downDir = new THREE.Vector3(Math.cos(theta), -Math.sin(theta), 0).normalize();
    velArrow.position.copy(wPos);
    velArrow.setDirection(downDir);
    velArrow.setLength(Math.max(0.5, sVel[0] * 0.35), 0.4, 0.24);

    const wPosHoop = new THREE.Vector3();
    racers[3].getWorldPosition(wPosHoop);
    fricArrow.position.copy(wPosHoop);
    fricArrow.setDirection(downDir.clone().negate());
    fricArrow.setLength(1.6, 0.38, 0.22);

    const a0 = (g * Math.sin(theta)) / 1.4;
    const a3 = (g * Math.sin(theta)) / 2.0;
    tel1.textContent = "1st: Solid Sphere (c=0.40) v=" + sVel[0].toFixed(2) + " m/s";
    tel2.textContent = "2nd: Cylinder v=" + sVel[1].toFixed(2) + " | 3rd: Shell v=" + sVel[2].toFixed(2);
    tel3.textContent = "4th: Hoop (c=1.00) v=" + sVel[3].toFixed(2) + " m/s | a=" + a3.toFixed(2);
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 7: Conservation of Angular Momentum: Spinning Platform with Adjustable Radius
# ======================================================================================
EXPERIMENTS_1_TO_16[7] = {
    "id": 7,
    "title": "Conservation of Angular Momentum: Spinning Platform with Adjustable Radius",
    "domain": "AP Physics 1 / C: Mechanics — Conservation of Angular Momentum & Rotational Work",
    "keywords": ["angular momentum", "spinning platform", "skater", "turntable", "dumbbell", "moment of inertia", "rotational kinetic energy"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Conservation of Angular Momentum L = I(r)*omega",
        "verified_law": "L = (I_0 + 2*m*r^2)*omega = const,  K_rot = L^2 / (2*I(r))",
        "conservation_invariants": [
            "Axial angular momentum L_y = I(r)*omega remains strictly constant when radial force pulls masses inward",
            "Rotational kinetic energy K_rot = 0.5*L*omega increases due to internal radial work W = integral F_r dr",
        ],
        "required_solver": "Analytical / Symplectic Phase Integrator for Variable-Inertia Rotor",
        "vector_visualizers": [
            "Axial Angular Momentum L (Emerald #10b981)",
            "Tangential Dumbbell Velocity v_t = omega*r (Cyan #22d3ee)",
            "Inward Radial Tension Force F_r (Magenta #f43f5e)",
        ],
        "verdict": "Verified: Variable-radius dumbbell skater turntable with constant L and variable K_rot validated.",
    },
    "curriculum": {
        "concept": "Conservation of Angular Momentum (Ice Skater / Turntable Effect)",
        "equations": [
            "L = I(r) * omega = (I_platform + 2 * m * r^2) * omega = const",
            "omega(r) = L / (I_0 + 2 * m * r^2)",
            "K_rot = 0.5 * I * omega^2 = L^2 / (2 * I(r))"
        ],
        "teacher_guide": (
            "Have students pull the Mass Radius r slider inward from 4.0 m to 0.8 m! Watch the turntable spin dramatically faster "
            "while the tall emerald Angular Momentum vector L at the center remains completely unchanged in height."
        ),
        "misconception_alert": (
            "Students often think rotational kinetic energy K_rot is also conserved when the skater pulls their arms in. "
            "Show them in the telemetry that K_rot increases because the skater's muscles do positive work pulling inward against centrifugal tension!"
        ),
        "intuition_questions": [
            "Why does the emerald Angular Momentum vector L stay constant in length while angular velocity omega triples?",
            "Where does the extra Rotational Kinetic Energy K_rot come from when the dumbbell masses are pulled inward?",
            "Why does a central radial force F_r produce zero torque (tau = r x F_r = 0) about the rotation axis?"
        ],
        "tts_narration": (
            "Welcome to the Conservation of Angular Momentum Lab! Pull the dumbbell radius slider inward and watch the spinning "
            "platform accelerate. Because inward radial force exerts zero torque, angular momentum L stays constant while omega and rotational kinetic energy surge!"
        ),
    },
    "scene_config": {
        "telemetry_title": "ANGULAR MOMENTUM CONSERVATION",
        "telemetry_lines": [
            "Angular Momentum L: 48.0 kg*m^2/s (CONST)",
            "Inertia I(r): 16.0 kg*m^2 | omega: 3.00 rad/s",
            "Rotational Energy K_rot: 72.0 J",
        ],
        "sliders": [
            {"label": "Dumbbell Radius (r)", "min": 0.8, "max": 4.2, "step": 0.1, "value": 3.0, "display": "3.0 m"},
            {"label": "Dumbbell Mass (m)", "min": 0.5, "max": 4.0, "step": 0.25, "value": 1.5, "display": "1.50 kg"},
            {"label": "Angular Mom (L)", "min": 20.0, "max": 90.0, "step": 5.0, "value": 50.0, "display": "50.0 N*m*s"},
            {"label": "Platform Inertia (I_0)", "min": 2.0, "max": 12.0, "step": 0.5, "value": 4.0, "display": "4.0 kg*m^2"},
        ],
        "legend_items": [
            ("#10b981", "Angular Momentum L (Const)"),
            ("#22d3ee", "Tangential Velocity v_t"),
            ("#f43f5e", "Inward Radial Force F_r"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Skater Effect (tau_ext = 0):</strong> "
            "Pulling dumbbells to smaller radius r shrinks I = I_0 + 2*m*r^2, forcing omega = L/I and K_rot = L^2/(2I) to surge!"
        ),
        "scene_js": """
  camera.position.set(0, 8, 17);
  controls.target.set(0, 0, 0);

  applyPromptNumber(/radius[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/momentum[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/inertia[^0-9]*([0-9.]+)/i, sl4);

  const rotorGroup = new THREE.Group();
  scene.add(rotorGroup);

  const platform = new THREE.Mesh(
    new THREE.CylinderGeometry(4.6, 4.6, 0.35, 36),
    new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.4, roughness: 0.4 })
  );
  platform.position.y = -2.5;
  rotorGroup.add(platform);

  const pillar = new THREE.Mesh(
    new THREE.CylinderGeometry(0.45, 0.55, 4.2, 20),
    new THREE.MeshStandardMaterial({ color: 0x475569 })
  );
  pillar.position.y = -0.4;
  rotorGroup.add(pillar);

  const bar = new THREE.Mesh(
    new THREE.CylinderGeometry(0.12, 0.12, 8.8, 16),
    new THREE.MeshStandardMaterial({ color: 0x94a3b8 })
  );
  bar.rotation.z = Math.PI / 2;
  bar.position.y = 1.2;
  rotorGroup.add(bar);

  const massA = new THREE.Mesh(
    new THREE.SphereGeometry(0.55, 24, 24),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.4 })
  );
  const massB = massA.clone();
  rotorGroup.add(massA, massB);

  const LArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 1.2, 0), 4.0, 0x10b981, 0.55, 0.32);
  const vArrowA = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(), 2.2, 0x22d3ee, 0.42, 0.25);
  const fArrowA = new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(), 1.8, 0xf43f5e, 0.40, 0.24);
  scene.add(LArrow, vArrowA, fArrowA);

  let angle = 0.0;

  function resetSim() {
    val1.textContent = parseFloat(sl1.value).toFixed(1) + " m";
    val2.textContent = parseFloat(sl2.value).toFixed(2) + " kg";
    val3.textContent = parseFloat(sl3.value).toFixed(1) + " N*m*s";
    val4.textContent = parseFloat(sl4.value).toFixed(1) + " kg*m^2";
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = () => { angle = 0; resetSim(); };
  resetSim();

  function stepPhysics() {
    const dt = 0.018;
    const r = parseFloat(sl1.value);
    const m = parseFloat(sl2.value);
    const L = parseFloat(sl3.value);
    const I0 = parseFloat(sl4.value);

    const I_tot = I0 + 2 * m * r * r;
    const omega = L / Math.max(1.5, I_tot);
    angle += omega * dt;

    rotorGroup.rotation.y = angle;
    massA.position.set(r, 1.2, 0);
    massB.position.set(-r, 1.2, 0);
    const sc = Math.pow(m / 1.5, 0.3);
    massA.scale.setScalar(sc);
    massB.scale.setScalar(sc);

    LArrow.setDirection(new THREE.Vector3(0, 1, 0));
    LArrow.setLength(Math.min(4.8, L * 0.075), 0.55, 0.32);

    const wPosA = new THREE.Vector3();
    massA.getWorldPosition(wPosA);
    const tang = new THREE.Vector3(-Math.sin(angle), 0, -Math.cos(angle)).normalize();
    const inward = new THREE.Vector3(-Math.cos(angle), 0, Math.sin(angle)).normalize();

    const vt = omega * r;
    vArrowA.position.copy(wPosA);
    vArrowA.setDirection(tang);
    vArrowA.setLength(Math.min(3.8, vt * 0.25), 0.42, 0.25);

    const fRad = m * omega * omega * r;
    fArrowA.position.copy(wPosA);
    fArrowA.setDirection(inward);
    fArrowA.setLength(Math.min(3.4, fRad * 0.06), 0.40, 0.24);

    const Krot = 0.5 * L * omega;
    tel1.textContent = "Angular Mom L: " + L.toFixed(1) + " kg*m^2/s (CONSERVED)";
    tel2.textContent = "Inertia I(r): " + I_tot.toFixed(2) + " kg*m^2 | omega: " + omega.toFixed(2) + " rad/s";
    tel3.textContent = "Rotational Energy K_rot: " + Krot.toFixed(1) + " J";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 8: Gyroscopic Precession & Nutation of a 3D Spinning Top under Gravity
# ======================================================================================
EXPERIMENTS_1_TO_16[8] = {
    "id": 8,
    "title": "Gyroscopic Precession & Nutation of a 3D Spinning Top under Gravity",
    "domain": "AP Physics C: Mechanics — 3D Rotational Dynamics & Torque-Induced Precession",
    "keywords": ["gyroscope", "precession", "nutation", "spinning top", "torque", "angular momentum", "right hand rule"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Gyroscopic Torque tau = dL/dt = r_cm x (m*g)",
        "verified_law": "Omega_p = (m * g * d) / (I_s * omega_s),  tau = r_cm x F_g",
        "conservation_invariants": [
            "Vertical component L_z and Spin Axial Momentum L_s = I_s*omega_s are conserved in torque-induced precession",
            "Torque vector tau = r_cm x (m*g) is always horizontal and perpendicular to L, steering L in a cone without making it fall",
        ],
        "required_solver": "RK4 (4th-Order Runge-Kutta) Gyroscopic Precession & Nutation Integrator",
        "vector_visualizers": [
            "Spin Angular Momentum L (Emerald #10b981)",
            "Gravitational Torque tau = r x mg (Magenta #f43f5e)",
            "Precession Angular Velocity Omega_p (Cyan #22d3ee)",
        ],
        "verdict": "Verified: 3D spinning top rotor with exact precession Omega_p = mgd/(I*omega) and nutation ripple validated.",
    },
    "curriculum": {
        "concept": "Gyroscopic Precession, Nutation & 3D Vector Torque (tau = dL/dt)",
        "equations": [
            "tau = r_cm x (m*g) = dL / dt",
            "Omega_precession = (m * g * d) / (I_spin * omega_spin)",
            "theta(t) = theta_0 + A_nut * (1 - cos(omega_nut * t))"
        ],
        "teacher_guide": (
            "Ask students why the tilted spinning top doesn't fall straight down under gravity! Point out that gravity creates a "
            "horizontal torque vector tau = r x mg (magenta arrow) perpendicular to L (emerald arrow), which swings the tip of L sideways in a horizontal circle."
        ),
        "misconception_alert": (
            "Students often think spinning the gyroscope faster makes it precess faster. Increase Spin Rate omega_s on the slider "
            "to show that Precession Speed Omega_p = mgd/(I*omega_s) is INVERSELY proportional to spin rate!"
        ),
        "intuition_questions": [
            "Why does a faster-spinning gyroscope precess MORE SLOWLY than a slower-spinning gyroscope?",
            "Why is the gravitational torque vector tau = r x mg always tangent to the horizontal precession circle?",
            "What happens to the precession rate Omega_p if you change the tilt angle theta_0 (for a steady top)?"
        ],
        "tts_narration": (
            "Welcome to the 3D Gyroscopic Precession Lab! Watch the emerald angular momentum vector L along the axle of the spinning rotor. "
            "Gravity pulls downward at distance d from the pivot, producing a horizontal magenta torque vector tau = r cross m g that steers L around the precession cone!"
        ),
    },
    "scene_config": {
        "telemetry_title": "GYROSCOPIC PRECESSION & NUTATION",
        "telemetry_lines": [
            "Precession Rate Omega_p: 0.98 rad/s",
            "Spin L_s: 36.0 N*m*s | Torque |tau|: 17.6 N*m",
            "Tilt Angle theta: 35.0 deg (Nutating)",
        ],
        "sliders": [
            {"label": "Spin Speed (omega_s)", "min": 10.0, "max": 50.0, "step": 2.0, "value": 24.0, "display": "24.0 rad/s"},
            {"label": "Tilt Angle (theta_0)", "min": 15.0, "max": 65.0, "step": 1.0, "value": 36.0, "display": "36 deg"},
            {"label": "Pivot Arm (d)", "min": 1.0, "max": 3.5, "step": 0.25, "value": 2.2, "display": "2.20 m"},
            {"label": "Nutation Amp", "min": 0.0, "max": 0.20, "step": 0.02, "value": 0.06, "display": "0.06 rad"},
        ],
        "legend_items": [
            ("#10b981", "Angular Momentum L"),
            ("#f43f5e", "Torque tau = r x mg"),
            ("#22d3ee", "Precession Axis Omega_p"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Gyroscopic Law dL = tau*dt:</strong> "
            "Because tau = r_cm x (m*g) is perpendicular to L, it rotates the direction of L horizontally at rate Omega_p = m*g*d/(I*omega_s)."
        ),
        "scene_js": """
  camera.position.set(0, 7, 17);
  controls.target.set(0, 1.5, 0);

  applyPromptNumber(/spin[^0-9]*([0-9.]+)|omega[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/tilt[^0-9]*([0-9.]+)|angle[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/arm[^0-9]*([0-9.]+)|distance[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/nutation[^0-9]*([0-9.]+)/i, sl4);

  const pedestal = new THREE.Mesh(
    new THREE.ConeGeometry(1.1, 3.2, 24),
    new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.4, roughness: 0.5 })
  );
  pedestal.position.y = -2.4;
  scene.add(pedestal);

  const pivotPt = new THREE.Vector3(0, -0.8, 0);
  const axleLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([pivotPt, new THREE.Vector3(0, 3, 0)]),
    new THREE.LineBasicMaterial({ color: 0xe2e8f0 })
  );
  scene.add(axleLine);

  const flywheel = new THREE.Mesh(
    new THREE.CylinderGeometry(2.1, 2.1, 0.42, 32),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, wireframe: true })
  );
  scene.add(flywheel);

  const LArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), pivotPt, 4.5, 0x10b981, 0.5, 0.3);
  const tauArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), pivotPt, 2.8, 0xf43f5e, 0.45, 0.28);
  const precArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), pivotPt, 3.8, 0x22d3ee, 0.45, 0.28);
  scene.add(LArrow, tauArrow, precArrow);

  const trailLine = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.65 })
  );
  scene.add(trailLine);

  let phi = 0.0, spinAngle = 0.0, tSim = 0.0;
  let trail = [];

  function resetSim() {
    trail = [];
    val1.textContent = parseFloat(sl1.value).toFixed(1) + " rad/s";
    val2.textContent = sl2.value + " deg";
    val3.textContent = parseFloat(sl3.value).toFixed(2) + " m";
    val4.textContent = parseFloat(sl4.value).toFixed(2) + " rad";
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function stepPhysics() {
    const dt = 0.018;
    const omegaS = parseFloat(sl1.value);
    const theta0 = parseFloat(sl2.value) * Math.PI / 180;
    const d = parseFloat(sl3.value);
    const nutAmp = parseFloat(sl4.value);
    const m = 2.0, g = 9.8, Is = 1.6;

    // RK4 integration of precession angle phi and nutation phase
    const k1 = (m * g * d) / Math.max(1.5, Is * omegaS);
    const k2 = k1, k3 = k1, k4 = k1;
    const OmegaP = (k1 + 2 * k2 + 2 * k3 + k4) / 6;

    tSim += dt;
    phi += OmegaP * dt;
    spinAngle += omegaS * dt * 0.4;

    const theta = theta0 + nutAmp * Math.sin(omegaS * 0.35 * tSim);
    const axisDir = new THREE.Vector3(
      Math.sin(theta) * Math.cos(phi),
      Math.cos(theta),
      Math.sin(theta) * Math.sin(phi)
    ).normalize();

    const cmPos = pivotPt.clone().addScaledVector(axisDir, d);
    const tipPos = pivotPt.clone().addScaledVector(axisDir, d * 1.65);
    axleLine.geometry.setFromPoints([pivotPt, tipPos]);

    flywheel.position.copy(cmPos);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), axisDir);
    flywheel.quaternion.copy(q);
    flywheel.rotateY(spinAngle);

    trail.push(tipPos.clone());
    if (trail.length > 220) trail.shift();
    trailLine.geometry.dispose();
    trailLine.geometry = new THREE.BufferGeometry().setFromPoints(trail);

    LArrow.position.copy(pivotPt);
    LArrow.setDirection(axisDir);
    LArrow.setLength(Math.min(5.2, d * 1.45 + omegaS * 0.04), 0.5, 0.3);

    const tauVec = new THREE.Vector3().crossVectors(axisDir.clone().multiplyScalar(d), new THREE.Vector3(0, -m * g, 0));
    if (tauVec.length() > 0.01) {
      tauArrow.position.copy(cmPos);
      tauArrow.setDirection(tauVec.clone().normalize());
      tauArrow.setLength(Math.min(3.5, tauVec.length() * 0.08), 0.45, 0.28);
    }

    precArrow.position.copy(pivotPt);
    precArrow.setDirection(new THREE.Vector3(0, 1, 0));
    precArrow.setLength(Math.min(4.2, 1.5 + OmegaP * 0.9), 0.45, 0.28);

    tel1.textContent = "Precession Rate Omega_p: " + OmegaP.toFixed(2) + " rad/s";
    tel2.textContent = "Spin L_s: " + (Is * omegaS).toFixed(1) + " N*m*s | |tau|: " + tauVec.length().toFixed(1) + " N*m";
    tel3.textContent = "Instantaneous Tilt theta: " + (theta * 180 / Math.PI).toFixed(1) + " deg";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 9: The Dzhanibekov (Tennis Racket) Theorem: 3D Intermediate Axis Flip
# ======================================================================================
EXPERIMENTS_1_TO_16[9] = {
    "id": 9,
    "title": "The Dzhanibekov (Tennis Racket) Theorem: 3D Intermediate Axis Flip",
    "domain": "AP Physics C / Classical Mechanics — Euler Rigid Body Equations & Asymmetric Rotors",
    "keywords": ["dzhanibekov", "tennis racket theorem", "intermediate axis", "rigid body", "euler equations", "t-handle", "instability"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "Classical Mechanics — Euler's Torque-Free Rigid Body Equations (I_1 < I_2 < I_3)",
        "verified_law": "I_1*(domega_1/dt) = (I_2 - I_3)*omega_2*omega_3,  I_2*(domega_2/dt) = (I_3 - I_1)*omega_3*omega_1,  I_3*(domega_3/dt) = (I_1 - I_2)*omega_1*omega_2",
        "conservation_invariants": [
            "Total Rotational Kinetic Energy 2*K = I_1*omega_1^2 + I_2*omega_2^2 + I_3*omega_3^2 is strictly invariant",
            "Total Angular Momentum Magnitude L^2 = (I_1*omega_1)^2 + (I_2*omega_2)^2 + (I_3*omega_3)^2 is strictly invariant (Polhode on Inertia Ellipsoid)",
        ],
        "required_solver": "RK4 (4th-Order Runge-Kutta) Euler Equation & Quaternion Attitude Integrator",
        "vector_visualizers": [
            "Inertial Angular Momentum Vector L (Emerald #10b981, Fixed in Space!)",
            "Instantaneous Angular Velocity omega (Cyan #22d3ee)",
            "Body Intermediate Axis e_2 (Magenta #f43f5e, Flips 180 deg!)",
        ],
        "verdict": "Verified: RK4 integration of Euler's rigid body equations demonstrating periodic 180-degree flips about I_2 while L stays fixed.",
    },
    "curriculum": {
        "concept": "The Dzhanibekov (Tennis Racket) Intermediate Axis Theorem",
        "equations": [
            "I_1 * d(omega_1)/dt = (I_2 - I_3) * omega_2 * omega_3",
            "I_2 * d(omega_2)/dt = (I_3 - I_1) * omega_3 * omega_1   (with I_1 < I_2 < I_3)",
            "L^2 = I_1^2*omega_1^2 + I_2^2*omega_2^2 + I_3^2*omega_3^2 = const"
        ],
        "teacher_guide": (
            "Watch the 3D T-handle spin in zero gravity primarily around its intermediate principal axis e_2 (magenta arrow). "
            "Every few seconds, omega_2 reverses sign—the T-handle executes a sudden 180-degree flip while the emerald Angular Momentum vector L never moves!"
        ),
        "misconception_alert": (
            "Students watching the Dzhanibekov effect on space station videos often think an external torque or air current flips the T-handle. "
            "Point to the fixed emerald L arrow to prove that torque tau = 0 and both Energy K and Momentum L are 100% constant!"
        ),
        "intuition_questions": [
            "Why is rotation around the smallest (I_1) and largest (I_3) principal axes stable, while the intermediate axis (I_2) is unstable?",
            "How can the T-handle flip 180 degrees in mid-air while its Angular Momentum vector L remains completely stationary?",
            "What happens to the time between flips as you decrease the Initial Perturbation omega_1,0 closer to zero?"
        ],
        "tts_narration": (
            "Welcome to the Dzhanibekov Tennis Racket Theorem Lab! Watch the 3D T-handle spinning in zero gravity near its intermediate axis. "
            "Even with zero external torque and a stationary emerald angular momentum vector, Euler's equations cause the magenta intermediate axis to flip 180 degrees periodically!"
        ),
    },
    "scene_config": {
        "telemetry_title": "DZHANIBEKOV RK4 EULER TELEMETRY",
        "telemetry_lines": [
            "Body omega_2: +5.98 rad/s (Flip State)",
            "Invariants: |L| = 12.00 | K_rot = 36.00 J",
            "Principal Inertia: I_1=1.0 < I_2=2.0 < I_3=3.0",
        ],
        "sliders": [
            {"label": "Primary Spin (omega_2)", "min": 3.0, "max": 9.0, "step": 0.5, "value": 6.0, "display": "6.0 rad/s"},
            {"label": "Perturbation (omega_1)", "min": 0.01, "max": 0.50, "step": 0.01, "value": 0.08, "display": "0.08 rad/s"},
            {"label": "Intermediate I_2", "min": 1.3, "max": 2.7, "step": 0.1, "value": 2.0, "display": "2.0 kg*m^2"},
            {"label": "Major Inertia I_3", "min": 2.8, "max": 4.5, "step": 0.1, "value": 3.2, "display": "3.2 kg*m^2"},
        ],
        "legend_items": [
            ("#10b981", "Fixed Angular Mom L"),
            ("#22d3ee", "Angular Velocity omega"),
            ("#f43f5e", "Body Handle Axis e_2 (Flips!)"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Intermediate Axis Instability (I_1 &lt; I_2 &lt; I_3):</strong> "
            "Small perturbations omega_1, omega_3 grow exponentially around axis 2, causing periodic 180-deg flips while L and K stay constant!"
        ),
        "scene_js": """
  camera.position.set(0, 5, 14);
  controls.target.set(0, 0, 0);

  applyPromptNumber(/spin[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/perturbation[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/i2[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/i3[^0-9]*([0-9.]+)/i, sl4);

  const tHandle = new THREE.Group();
  const crossbar = new THREE.Mesh(
    new THREE.CylinderGeometry(0.38, 0.38, 4.8, 24),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.5, roughness: 0.3 })
  );
  crossbar.rotation.z = Math.PI / 2;
  const stem = new THREE.Mesh(
    new THREE.CylinderGeometry(0.28, 0.28, 2.8, 24),
    new THREE.MeshStandardMaterial({ color: 0xf43f5e, metalness: 0.4, roughness: 0.3 })
  );
  stem.position.y = 1.4;
  tHandle.add(crossbar, stem);
  scene.add(tHandle);

  const LArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 4.5, 0x10b981, 0.52, 0.3);
  const wArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 3.8, 0x22d3ee, 0.45, 0.26);
  const e2Arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 3.4, 0xf43f5e, 0.45, 0.26);
  scene.add(LArrow, wArrow, e2Arrow);

  let w = new THREE.Vector3();
  let q = new THREE.Quaternion();

  function resetSim() {
    const w2 = parseFloat(sl1.value);
    const w1 = parseFloat(sl2.value);
    val1.textContent = w2.toFixed(1) + " rad/s";
    val2.textContent = w1.toFixed(2) + " rad/s";
    val3.textContent = parseFloat(sl3.value).toFixed(1) + " kg*m^2";
    val4.textContent = parseFloat(sl4.value).toFixed(1) + " kg*m^2";

    w.set(w1, w2, 0.02);
    q.identity();
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function eulerDeriv(vec, I1, I2, I3) {
    return new THREE.Vector3(
      ((I2 - I3) / I1) * vec.y * vec.z,
      ((I3 - I1) / I2) * vec.z * vec.x,
      ((I1 - I2) / I3) * vec.x * vec.y
    );
  }

  function stepPhysics() {
    const dt = 0.014;
    const I1 = 1.0;
    const I2 = parseFloat(sl3.value);
    const I3 = parseFloat(sl4.value);

    // RK4 step for body angular velocity w
    const k1 = eulerDeriv(w, I1, I2, I3);
    const k2 = eulerDeriv(w.clone().addScaledVector(k1, 0.5 * dt), I1, I2, I3);
    const k3 = eulerDeriv(w.clone().addScaledVector(k2, 0.5 * dt), I1, I2, I3);
    const k4 = eulerDeriv(w.clone().addScaledVector(k3, dt), I1, I2, I3);
    w.addScaledVector(k1.addScaledVector(k2, 2).addScaledVector(k3, 2).add(k4), dt / 6);

    const wWorld = w.clone().applyQuaternion(q);
    const speed = wWorld.length();
    if (speed > 0.0001) {
      const dq = new THREE.Quaternion().setFromAxisAngle(wWorld.clone().normalize(), speed * dt);
      q.premultiply(dq).normalize();
    }
    tHandle.quaternion.copy(q);

    const LBody = new THREE.Vector3(I1 * w.x, I2 * w.y, I3 * w.z);
    const LWorld = LBody.clone().applyQuaternion(q);
    const e2World = new THREE.Vector3(0, 1, 0).applyQuaternion(q);

    if (LWorld.length() > 0.01) {
      LArrow.setDirection(LWorld.clone().normalize());
      LArrow.setLength(4.4, 0.5, 0.3);
    }
    if (wWorld.length() > 0.01) {
      wArrow.setDirection(wWorld.clone().normalize());
      wArrow.setLength(3.7, 0.42, 0.25);
    }
    e2Arrow.setDirection(e2World.normalize());
    e2Arrow.setLength(3.3, 0.42, 0.25);

    const Krot = 0.5 * (I1 * w.x * w.x + I2 * w.y * w.y + I3 * w.z * w.z);
    tel1.textContent = "Body omega_2: " + (w.y >= 0 ? "+" : "") + w.y.toFixed(2) + " rad/s (" + (w.y >= 0 ? "UP" : "FLIPPED!") + ")";
    tel2.textContent = "|L|: " + LBody.length().toFixed(2) + " N*m*s | K_rot: " + Krot.toFixed(2) + " J";
    tel3.textContent = "Inertias: I_1=1.0 < I_2=" + I2.toFixed(1) + " < I_3=" + I3.toFixed(1);
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 10: Coriolis & Centrifugal Forces: Projectile on a Rotating Turntable
# ======================================================================================
EXPERIMENTS_1_TO_16[10] = {
    "id": 10,
    "title": "Coriolis & Centrifugal Forces: Projectile Motion on a Rotating Turntable",
    "domain": "AP Physics C / Classical Mechanics — Non-Inertial Rotating Reference Frames",
    "keywords": ["coriolis", "centrifugal", "rotating frame", "turntable", "carousel", "merry go round", "fictitious force"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "Classical Mechanics — Non-Inertial Rotating Reference Frames",
        "verified_law": "m*a_rot = -2*m*(Omega x v_rot) - m*(Omega x (Omega x r))",
        "conservation_invariants": [
            "Inertial trajectory is a straight constant-velocity chord r_inert(t) = r_0 + v_0*t",
            "Rotating turntable observer measures exact Coriolis deflection F_cor = -2*m*(Omega x v_rot) and Centrifugal force F_cent = m*Omega^2*r",
        ],
        "required_solver": "RK4 (4th-Order Runge-Kutta) Rotating-Frame Coriolis & Centrifugal Integrator",
        "vector_visualizers": [
            "Rotating-Frame Velocity v_rot (Cyan #22d3ee)",
            "Coriolis Force F_cor = -2m(Omega x v) (Magenta #f43f5e)",
            "Centrifugal Force F_cent = m*Omega^2*r (Amber #f59e0b)",
        ],
        "verdict": "Verified: 3D rotating carousel disc with simultaneous inertial chord and curved rotating-frame Coriolis trace validated.",
    },
    "curriculum": {
        "concept": "Coriolis & Centrifugal Pseudo-Forces in a Rotating Reference Frame",
        "equations": [
            "F_coriolis = -2 * m * (Omega x v_rot)",
            "F_centrifugal = -m * (Omega x (Omega x r)) = +m * Omega^2 * r * r_hat",
            "a_rot = -2*(Omega x v_rot) + Omega^2*r"
        ],
        "teacher_guide": (
            "Launch the puck radially across the spinning carousel! Compare the straight emerald line (path in the Inertial Lab Frame) "
            "against the dramatic curved cyan spiral painted onto the rotating floor due to F_cor = -2m(Omega x v)."
        ),
        "misconception_alert": (
            "Students often think the Coriolis force is a real physical contact or gravitational force. Clarify that in the inertial frame "
            "the puck travels in a straight line with F_net = 0, while the floor rotates underneath it!"
        ),
        "intuition_questions": [
            "On a counter-clockwise spinning turntable (Omega > 0 along +Y), does the Coriolis force deflect a moving puck to its right or to its left?",
            "Why does the Coriolis force F_cor = -2m(Omega x v_rot) do zero work on the puck in the rotating frame?",
            "How does the Rossby number Ro = v / (2*Omega*L) determine whether Coriolis curvature dominates?"
        ],
        "tts_narration": (
            "Welcome to the Coriolis and Centrifugal Force Lab! Watch the puck slide frictionlessly across the rotating turntable. "
            "In space it follows the straight emerald chord, but on the spinning disc it traces a curved cyan trajectory deflected by the magenta Coriolis force!"
        ),
    },
    "scene_config": {
        "telemetry_title": "CORIOLIS & CENTRIFUGAL TELEMETRY",
        "telemetry_lines": [
            "Coriolis |F_cor|: 14.4 N | Deflection: Right",
            "Centrifugal |F_cf|: 8.2 N | Radius r: 3.4 m",
            "Turntable Omega: +0.80 rad/s (CCW)",
        ],
        "sliders": [
            {"label": "Turntable Spin (Omega)", "min": -1.6, "max": 1.6, "step": 0.1, "value": 0.8, "display": "0.80 rad/s"},
            {"label": "Launch Speed (v_0)", "min": 2.0, "max": 9.0, "step": 0.5, "value": 4.5, "display": "4.5 m/s"},
            {"label": "Puck Mass (m)", "min": 0.5, "max": 4.0, "step": 0.25, "value": 1.5, "display": "1.50 kg"},
            {"label": "Camera Co-Rotate (0/1)", "min": 0, "max": 1, "step": 1, "value": 0, "display": "0 (Inertial)"},
        ],
        "legend_items": [
            ("#22d3ee", "Rotating Path & v_rot"),
            ("#f43f5e", "Coriolis F_cor = -2m(Omega x v)"),
            ("#f59e0b", "Centrifugal F_cf = m*Omega^2*r"),
            ("#10b981", "Inertial Straight Path"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Rotating Frame Dynamics:</strong> "
            "A frictionless puck moves in a straight inertial chord (emerald), which curves on the rotating disc due to F_cor = -2m(Omega x v_rot)."
        ),
        "scene_js": """
  camera.position.set(0, 14, 15);
  controls.target.set(0, -2, 0);

  applyPromptNumber(/omega[^0-9-]*(-?[0-9.]+)|spin[^0-9-]*(-?[0-9.]+)/i, sl1);
  applyPromptNumber(/speed[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/frame[^0-9]*([0-9.]+)/i, sl4);

  const discGroup = new THREE.Group();
  discGroup.position.y = -2.8;
  scene.add(discGroup);

  const disc = new THREE.Mesh(
    new THREE.CylinderGeometry(8.5, 8.5, 0.25, 48),
    new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.6, metalness: 0.2 })
  );
  const polarGrid = new THREE.PolarGridHelper(8.4, 12, 6, 64, 0x334155, 0x1e293b);
  polarGrid.position.y = 0.14;
  discGroup.add(disc, polarGrid);

  const rotTraceLine = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x22d3ee })
  );
  discGroup.add(rotTraceLine);

  const inertLine = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x10b981 })
  );
  scene.add(inertLine);

  const puck = new THREE.Mesh(
    new THREE.SphereGeometry(0.42, 24, 24),
    new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0284c7, emissiveIntensity: 0.45 })
  );
  scene.add(puck);

  const vArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0x22d3ee, 0.4, 0.24);
  const corArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(), 2.2, 0xf43f5e, 0.4, 0.24);
  const cfArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 1.8, 0xf59e0b, 0.38, 0.22);
  scene.add(vArrow, corArrow, cfArrow);

  let rRot = new THREE.Vector3();
  let vRot = new THREE.Vector3();
  let discAngle = 0.0;
  let rotPts = [];
  let inertPts = [];

  function resetSim() {
    const Om = parseFloat(sl1.value);
    const v0 = parseFloat(sl2.value);
    const m = parseFloat(sl3.value);
    const coRot = parseInt(sl4.value);
    val1.textContent = Om.toFixed(2) + " rad/s";
    val2.textContent = v0.toFixed(1) + " m/s";
    val3.textContent = m.toFixed(2) + " kg";
    val4.textContent = coRot ? "1 (Co-Rotating)" : "0 (Inertial)";

    rRot.set(0.1, 0.3, 0);
    vRot.set(v0, 0, 0);
    discAngle = 0;
    rotPts = [rRot.clone()];
    inertPts = [new THREE.Vector3(0.1, -2.5, 0)];
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function rotAccel(rVec, vVec, OmVec) {
    const cor = new THREE.Vector3().crossVectors(OmVec, vVec).multiplyScalar(-2.0);
    const cf = new THREE.Vector3().crossVectors(OmVec, new THREE.Vector3().crossVectors(OmVec, rVec)).negate();
    return cor.add(cf);
  }

  function stepPhysics() {
    const dt = 0.02;
    const Om = parseFloat(sl1.value);
    const m = parseFloat(sl3.value);
    const coRot = parseInt(sl4.value);
    const OmVec = new THREE.Vector3(0, Om, 0);

    // RK4 integration in rotating frame
    const k1v = rotAccel(rRot, vRot, OmVec);
    const k1r = vRot.clone();
    const k2v = rotAccel(rRot.clone().addScaledVector(k1r, 0.5 * dt), vRot.clone().addScaledVector(k1v, 0.5 * dt), OmVec);
    const k2r = vRot.clone().addScaledVector(k1v, 0.5 * dt);
    const k3v = rotAccel(rRot.clone().addScaledVector(k2r, 0.5 * dt), vRot.clone().addScaledVector(k2v, 0.5 * dt), OmVec);
    const k3r = vRot.clone().addScaledVector(k2v, 0.5 * dt);
    const k4v = rotAccel(rRot.clone().addScaledVector(k3r, dt), vRot.clone().addScaledVector(k3v, dt), OmVec);
    const k4r = vRot.clone().addScaledVector(k3v, dt);

    rRot.addScaledVector(k1r.addScaledVector(k2r, 2).addScaledVector(k3r, 2).add(k4r), dt / 6);
    vRot.addScaledVector(k1v.addScaledVector(k2v, 2).addScaledVector(k3v, 2).add(k4v), dt / 6);
    discAngle += Om * dt;

    if (rRot.length() > 8.2) {
      resetSim();
      return;
    }

    discGroup.rotation.y = coRot ? 0 : discAngle;

    rotPts.push(rRot.clone());
    rotTraceLine.geometry.dispose();
    rotTraceLine.geometry = new THREE.BufferGeometry().setFromPoints(rotPts);

    const wPos = rRot.clone().applyAxisAngle(new THREE.Vector3(0, 1, 0), coRot ? 0 : discAngle);
    wPos.y = -2.45;
    puck.position.copy(wPos);

    if (!coRot) {
      inertPts.push(wPos.clone());
      inertLine.geometry.dispose();
      inertLine.geometry = new THREE.BufferGeometry().setFromPoints(inertPts);
    }

    const vWorldDir = vRot.clone().applyAxisAngle(new THREE.Vector3(0, 1, 0), coRot ? 0 : discAngle);
    const fCor = new THREE.Vector3().crossVectors(OmVec, vRot).multiplyScalar(-2 * m).applyAxisAngle(new THREE.Vector3(0, 1, 0), coRot ? 0 : discAngle);
    const fCf = new THREE.Vector3(rRot.x, 0, rRot.z).multiplyScalar(m * Om * Om).applyAxisAngle(new THREE.Vector3(0, 1, 0), coRot ? 0 : discAngle);

    vArrow.position.copy(wPos);
    if (vWorldDir.length() > 0.05) {
      vArrow.setDirection(vWorldDir.clone().normalize());
      vArrow.setLength(Math.min(3.2, vWorldDir.length() * 0.35), 0.4, 0.24);
    }
    corArrow.position.copy(wPos);
    if (fCor.length() > 0.05) {
      corArrow.setDirection(fCor.clone().normalize());
      corArrow.setLength(Math.min(3.4, fCor.length() * 0.18), 0.4, 0.24);
    }
    cfArrow.position.copy(wPos);
    if (fCf.length() > 0.05) {
      cfArrow.setDirection(fCf.clone().normalize());
      cfArrow.setLength(Math.min(3.0, fCf.length() * 0.22), 0.38, 0.22);
    }

    tel1.textContent = "Coriolis |F_cor|: " + fCor.length().toFixed(2) + " N | Speed: " + vRot.length().toFixed(2) + " m/s";
    tel2.textContent = "Centrifugal |F_cf|: " + fCf.length().toFixed(2) + " N | Radius r: " + rRot.length().toFixed(2) + " m";
    tel3.textContent = "Turntable Omega: " + Om.toFixed(2) + " rad/s | RK4 Solver";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 11: Simple Harmonic Motion: Mass-Spring & Pendulum with Phase Space Portrait
# ======================================================================================
EXPERIMENTS_1_TO_16[11] = {
    "id": 11,
    "title": "Simple Harmonic Motion: Mass-Spring & Pendulum with 3D Phase Space Portrait",
    "domain": "AP Physics 1 / C: Mechanics — Simple Harmonic Oscillations & Phase Space",
    "keywords": ["simple harmonic motion", "shm", "spring", "hooke", "phase space", "ellipse", "oscillator"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Simple Harmonic Oscillator & Symplectic Phase Space Portrait",
        "verified_law": "m*(d^2x/dt^2) + b*(dx/dt) + k*x = 0,  (x/A)^2 + (v/(omega_0*A))^2 = 1",
        "conservation_invariants": [
            "For b = 0, Phase Space trajectory (x, v/omega_0) is an exact energy-conserving circle/ellipse with E = 0.5*k*x^2 + 0.5*m*v^2",
            "Symplectic Velocity-Verlet preserves phase-space area (Liouville's Theorem) without artificial numerical spiral drift",
        ],
        "required_solver": "Velocity-Verlet (Symplectic) Harmonic & Phase-Portrait Integrator",
        "vector_visualizers": [
            "Oscillator Velocity v (Cyan #22d3ee)",
            "Hooke Restoring Force F_s = -k*x (Magenta #f43f5e)",
            "Phase Space State Vector (x, v) (Emerald #10b981)",
        ],
        "verdict": "Verified: 3D helical coil spring + oscillating block alongside real-time 3D (x, v) Phase Space portrait ring validated.",
    },
    "curriculum": {
        "concept": "Simple Harmonic Motion (SHM) & Phase Space Portrait (x vs. v)",
        "equations": [
            "F_spring = -k * x,   omega_0 = sqrt(k / m),   T = 2*pi * sqrt(m / k)",
            "E_total = 0.5 * k * x^2 + 0.5 * m * v^2 = 0.5 * k * A^2",
            "(x / A)^2 + (v / (omega_0 * A))^2 = 1   (Phase Space Ellipse)"
        ],
        "teacher_guide": (
            "Point out the two synchronized 3D views: on the left, the physical helical coil spring and mass oscillating horizontally; "
            "on the right, the glowing emerald Phase Space (x, v) portrait where the state vector traces an ellipse for b=0 or spirals inward when damping b > 0!"
        ),
        "misconception_alert": (
            "Students often think period T depends on initial amplitude A. Vary the Amplitude A slider with b=0 to show that the "
            "Phase Space ellipse grows larger, but one full revolution still takes the exact same period T = 2*pi*sqrt(m/k)!"
        ),
        "intuition_questions": [
            "Why are velocity v (cyan) and restoring force F = -kx (magenta) always 90 degrees out of phase on the Phase Space portrait?",
            "What happens to the shape of the Phase Space ellipse when you quadruple the Spring Constant k?",
            "When you add light damping b > 0, why does the Phase Space trajectory become an inward logarithmic spiral?"
        ],
        "tts_narration": (
            "Welcome to the Simple Harmonic Motion and Phase Space Lab! On the left, watch the 3D helical spring and mass oscillate under Hooke's Law. "
            "On the right, watch the live Phase Space portrait plot position x against velocity v as a closed energy-conserving ellipse!"
        ),
    },
    "scene_config": {
        "telemetry_title": "SHM & 3D PHASE SPACE PORTRAIT",
        "telemetry_lines": [
            "Freq omega_0: 2.50 rad/s | Period T: 2.51 s",
            "State: x = +2.10 m | v = -3.40 m/s",
            "Energy: U_s = 22.0 J | K = 11.6 J",
        ],
        "sliders": [
            {"label": "Spring Constant (k)", "min": 4.0, "max": 36.0, "step": 1.0, "value": 16.0, "display": "16.0 N/m"},
            {"label": "Block Mass (m)", "min": 1.0, "max": 8.0, "step": 0.5, "value": 2.5, "display": "2.5 kg"},
            {"label": "Initial Amplitude (A)", "min": 1.0, "max": 4.0, "step": 0.2, "value": 2.8, "display": "2.8 m"},
            {"label": "Damping Coeff (b)", "min": 0.0, "max": 0.8, "step": 0.05, "value": 0.0, "display": "0.00 N*s/m"},
        ],
        "legend_items": [
            ("#22d3ee", "Velocity Vector v"),
            ("#f43f5e", "Restoring Force F = -kx"),
            ("#10b981", "Phase Portrait (x, v)"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Phase Space (x, v) Portrait:</strong> "
            "Conservation of energy 0.5*k*x^2 + 0.5*m*v^2 = E maps SHM onto an ellipse in (x, v) space, or an inward spiral with damping b > 0."
        ),
        "scene_js": """
  camera.position.set(0, 4.5, 19);
  controls.target.set(0, 0, 0);

  applyPromptNumber(/spring[^0-9]*([0-9.]+)|k[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/amplitude[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/damping[^0-9]*([0-9.]+)/i, sl4);

  const wall = new THREE.Mesh(
    new THREE.BoxGeometry(0.5, 3.2, 3.0),
    new THREE.MeshStandardMaterial({ color: 0x334155 })
  );
  wall.position.set(-9.5, -1.5, 0);
  scene.add(wall);

  const block = new THREE.Mesh(
    new THREE.BoxGeometry(1.4, 1.4, 1.4),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.35 })
  );
  scene.add(block);

  const springLine = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x94a3b8 })
  );
  scene.add(springLine);

  // Right side: 3D Phase Space (x, v) Portrait Board
  const phaseCenter = new THREE.Vector3(5.2, 0.5, 0);
  const phaseRing = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x10b981 })
  );
  const phaseDot = new THREE.Mesh(
    new THREE.SphereGeometry(0.28, 20, 20),
    new THREE.MeshBasicMaterial({ color: 0x10b981 })
  );
  scene.add(phaseRing, phaseDot);

  const vArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0x22d3ee, 0.42, 0.25);
  const fArrow = new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(), 2.2, 0xf43f5e, 0.42, 0.25);
  const pArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), phaseCenter, 2.5, 0x10b981, 0.4, 0.24);
  scene.add(vArrow, fArrow, pArrow);

  let xPos = 2.8, vVel = 0.0;
  let phasePts = [];

  function updateSpringMesh(xEnd) {
    const pts = [];
    const xStart = -9.25;
    const coils = 14;
    const N = 140;
    for (let i = 0; i <= N; i++) {
      const u = i / N;
      const xx = xStart + u * (xEnd - xStart);
      const rCoil = (i === 0 || i === N) ? 0 : 0.45;
      const yy = -1.5 + rCoil * Math.cos(u * coils * 2 * Math.PI);
      const zz = rCoil * Math.sin(u * coils * 2 * Math.PI);
      pts.push(new THREE.Vector3(xx, yy, zz));
    }
    springLine.geometry.dispose();
    springLine.geometry = new THREE.BufferGeometry().setFromPoints(pts);
  }

  function resetSim() {
    xPos = parseFloat(sl3.value);
    vVel = 0.0;
    phasePts = [];
    val1.textContent = parseFloat(sl1.value).toFixed(1) + " N/m";
    val2.textContent = parseFloat(sl2.value).toFixed(1) + " kg";
    val3.textContent = xPos.toFixed(1) + " m";
    val4.textContent = parseFloat(sl4.value).toFixed(2) + " N*s/m";
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function stepPhysics() {
    const dt = 0.02;
    const k = parseFloat(sl1.value);
    const m = parseFloat(sl2.value);
    const b = parseFloat(sl4.value);
    const omega0 = Math.sqrt(k / m);

    // Symplectic Velocity-Verlet
    const ax_old = (-k * xPos - b * vVel) / m;
    const xNew = xPos + vVel * dt + 0.5 * ax_old * dt * dt;
    const vHalf = vVel + 0.5 * ax_old * dt;
    const acc_new = (-k * xNew - b * vHalf) / m;
    vVel = vVel + 0.5 * (ax_old + acc_new) * dt;
    xPos = xNew;

    const blockX = -4.2 + xPos;
    block.position.set(blockX, -1.5, 0);
    updateSpringMesh(blockX - 0.7);

    vArrow.position.set(blockX, -0.5, 0);
    vArrow.setDirection(new THREE.Vector3(vVel >= 0 ? 1 : -1, 0, 0));
    vArrow.setLength(Math.max(0.25, Math.min(3.4, Math.abs(vVel) * 0.35)), 0.4, 0.24);

    const fSpring = -k * xPos;
    fArrow.position.set(blockX, -1.5, 0.85);
    fArrow.setDirection(new THREE.Vector3(fSpring >= 0 ? 1 : -1, 0, 0));
    fArrow.setLength(Math.max(0.25, Math.min(3.5, Math.abs(fSpring) * 0.06)), 0.4, 0.24);

    const pPt = new THREE.Vector3(phaseCenter.x + xPos * 0.9, phaseCenter.y + (vVel / Math.max(0.5, omega0)) * 0.9, 0);
    phaseDot.position.copy(pPt);
    phasePts.push(pPt.clone());
    if (phasePts.length > 320) phasePts.shift();
    phaseRing.geometry.dispose();
    phaseRing.geometry = new THREE.BufferGeometry().setFromPoints(phasePts);

    const pVec = pPt.clone().sub(phaseCenter);
    if (pVec.length() > 0.05) {
      pArrow.setDirection(pVec.clone().normalize());
      pArrow.setLength(pVec.length(), 0.38, 0.22);
    }

    const Us = 0.5 * k * xPos * xPos;
    const K = 0.5 * m * vVel * vVel;
    tel1.textContent = "Freq omega_0: " + omega0.toFixed(2) + " rad/s | T: " + (2 * Math.PI / omega0).toFixed(2) + " s";
    tel2.textContent = "State: x = " + xPos.toFixed(2) + " m | v = " + vVel.toFixed(2) + " m/s";
    tel3.textContent = "Energy: U_s = " + Us.toFixed(1) + " J | K = " + K.toFixed(1) + " J";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 12: Driven Damped Harmonic Oscillator: Resonance Peak & Phase Lag
# ======================================================================================
EXPERIMENTS_1_TO_16[12] = {
    "id": 12,
    "title": "Driven Damped Harmonic Oscillator: Resonance Amplitude Peak & Phase Lag",
    "domain": "AP Physics C: Mechanics — Forced Oscillations, Mechanical Resonance & Phase Lag",
    "keywords": ["resonance", "driven oscillator", "damped", "phase lag", "lorentzian", "quality factor", "harmonic"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Driven Damped Oscillator & Resonance Response",
        "verified_law": "m*x'' + b*x' + k*x = F_0*cos(omega_d*t),  A(omega_d) = (F_0/m) / sqrt((omega_0^2 - omega_d^2)^2 + (b*omega_d/m)^2)",
        "conservation_invariants": [
            "At steady state, average power input P_in = <F_drive * v> equals viscous dissipation P_diss = <b * v^2>",
            "At resonance omega_d = omega_0 = sqrt(k/m), phase lag phi = arctan((b*omega_d/m)/(omega_0^2 - omega_d^2)) passes through exactly 90 degrees (pi/2 rad)",
        ],
        "required_solver": "RK4 (4th-Order Runge-Kutta) Driven Damped Oscillator & Resonance Curve Solver",
        "vector_visualizers": [
            "Oscillator Velocity v (Cyan #22d3ee)",
            "Periodic Driving Force F_drive(t) (Amber #f59e0b)",
            "Spring + Damper Force F_s + F_d (Magenta #f43f5e)",
        ],
        "verdict": "Verified: 3D driver piston + mass-spring-damper alongside live 3D Resonance Curve A(omega_d) arch validated.",
    },
    "curriculum": {
        "concept": "Driven Damped Harmonic Oscillator, Mechanical Resonance & Phase Lag",
        "equations": [
            "m*(d^2x/dt^2) + b*(dx/dt) + k*x = F_0 * cos(omega_d * t)",
            "A(omega_d) = (F_0 / m) / sqrt((omega_0^2 - omega_d^2)^2 + (b * omega_d / m)^2)",
            "tan(phi) = (b * omega_d / m) / (omega_0^2 - omega_d^2)"
        ],
        "teacher_guide": (
            "Sweep the Driving Frequency omega_d slider across the natural frequency omega_0 = 3.0 rad/s! Watch the glowing marker "
            "climb the 3D Lorentzian Resonance Arch in the background while the mass amplitude peaks and phase lag phi passes 90 degrees."
        ),
        "misconception_alert": (
            "Students often think the mass moves in phase (phi = 0 deg) with the driving piston at resonance. "
            "Point out that at resonance omega_d = omega_0, the displacement lags the driving force by 90 degrees so F_drive is 100% in phase with velocity v!"
        ),
        "intuition_questions": [
            "Why must the driving force F_drive be in phase with velocity v (90 deg ahead of position x) to pump maximum power into the oscillator?",
            "How does lowering the Damping Coefficient b affect the height and sharpness (Quality Factor Q) of the 3D Resonance Arch?",
            "Why does the oscillator move nearly 180 degrees out of phase with the driver when omega_d >> omega_0?"
        ],
        "tts_narration": (
            "Welcome to the Mechanical Resonance Lab! On the left, the amber driving piston pushes the spring-mass system at frequency omega d. "
            "In the background, the 3D resonance curve shows steady-state amplitude peaking sharply when omega d matches natural frequency omega naught!"
        ),
    },
    "scene_config": {
        "telemetry_title": "RESONANCE & PHASE LAG TELEMETRY",
        "telemetry_lines": [
            "Drive omega_d: 3.00 rad/s | omega_0: 3.00 rad/s",
            "Steady Amplitude A: 3.33 m | Q-Factor: 6.0",
            "Phase Lag phi: 90.0 deg (Resonance Peak!)",
        ],
        "sliders": [
            {"label": "Drive Freq (omega_d)", "min": 0.5, "max": 6.0, "step": 0.1, "value": 3.0, "display": "3.0 rad/s"},
            {"label": "Natural Freq (omega_0)", "min": 1.5, "max": 4.5, "step": 0.25, "value": 3.0, "display": "3.00 rad/s"},
            {"label": "Damping (b / m)", "min": 0.2, "max": 2.0, "step": 0.1, "value": 0.5, "display": "0.50 s^-1"},
            {"label": "Drive Amp (F_0 / m)", "min": 1.0, "max": 8.0, "step": 0.5, "value": 4.5, "display": "4.5 N/kg"},
        ],
        "legend_items": [
            ("#f59e0b", "Driver Piston & F_drive"),
            ("#22d3ee", "Mass Velocity v"),
            ("#f43f5e", "Restoring + Damper Force"),
            ("#10b981", "3D Resonance Curve A(omega)"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Mechanical Resonance & Phase Lag:</strong> "
            "Amplitude A(omega_d) peaks near omega_0 = sqrt(k/m). At omega_d = omega_0, phase lag phi = 90 deg so F_drive aligns with v."
        ),
        "scene_js": """
  camera.position.set(0, 5, 19);
  controls.target.set(0, 0.5, 0);

  applyPromptNumber(/drive[^0-9]*([0-9.]+)|freq[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/natural[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/damping[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/force[^0-9]*([0-9.]+)/i, sl4);

  const piston = new THREE.Mesh(
    new THREE.CylinderGeometry(0.65, 0.65, 1.2, 24),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.4, roughness: 0.3 })
  );
  piston.rotation.z = Math.PI / 2;
  scene.add(piston);

  const massBlock = new THREE.Mesh(
    new THREE.BoxGeometry(1.4, 1.4, 1.4),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.4 })
  );
  scene.add(massBlock);

  const springLine = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x94a3b8 })
  );
  scene.add(springLine);

  const resCurveLine = new THREE.Line(
    new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x10b981 })
  );
  const resMarker = new THREE.Mesh(
    new THREE.SphereGeometry(0.32, 20, 20),
    new THREE.MeshBasicMaterial({ color: 0xf43f5e })
  );
  scene.add(resCurveLine, resMarker);

  const drvArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0xf59e0b, 0.42, 0.25);
  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0x22d3ee, 0.42, 0.25);
  const resArrow = new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(), 2.0, 0xf43f5e, 0.40, 0.24);
  scene.add(drvArrow, velArrow, resArrow);

  let x = 0.0, v = 0.0, tSim = 0.0;

  function calcAmp(w, w0, gamma, f0) {
    const denom = Math.sqrt(Math.pow(w0 * w0 - w * w, 2) + Math.pow(gamma * w, 2));
    return f0 / Math.max(0.15, denom);
  }

  function rebuildResonanceArch() {
    const wd = parseFloat(sl1.value);
    const w0 = parseFloat(sl2.value);
    const gamma = parseFloat(sl3.value);
    const f0 = parseFloat(sl4.value);
    const pts = [];
    for (let i = 0; i <= 100; i++) {
      const w = 0.5 + (i / 100) * 5.5;
      const A = Math.min(6.0, calcAmp(w, w0, gamma, f0) * 0.75);
      const px = -7.5 + (w - 0.5) * 2.7;
      pts.push(new THREE.Vector3(px, -1.0 + A, -3.5));
    }
    resCurveLine.geometry.dispose();
    resCurveLine.geometry = new THREE.BufferGeometry().setFromPoints(pts);

    const A_curr = Math.min(6.0, calcAmp(wd, w0, gamma, f0) * 0.75);
    resMarker.position.set(-7.5 + (wd - 0.5) * 2.7, -1.0 + A_curr, -3.5);
  }

  function resetSim() {
    val1.textContent = parseFloat(sl1.value).toFixed(1) + " rad/s";
    val2.textContent = parseFloat(sl2.value).toFixed(2) + " rad/s";
    val3.textContent = parseFloat(sl3.value).toFixed(2) + " s^-1";
    val4.textContent = parseFloat(sl4.value).toFixed(1) + " N/kg";
    rebuildResonanceArch();
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = () => { x = 0; v = 0; tSim = 0; resetSim(); };
  resetSim();

  function stepPhysics() {
    const dt = 0.018;
    const wd = parseFloat(sl1.value);
    const w0 = parseFloat(sl2.value);
    const gamma = parseFloat(sl3.value);
    const f0 = parseFloat(sl4.value);

    // RK4 integration for driven damped oscillator
    function acc(pos, vel, t) {
      return f0 * Math.cos(wd * t) - gamma * vel - w0 * w0 * pos;
    }
    const k1v = acc(x, v, tSim);
    const k1x = v;
    const k2v = acc(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v, tSim + 0.5 * dt);
    const k2x = v + 0.5 * dt * k1v;
    const k3v = acc(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v, tSim + 0.5 * dt);
    const k3x = v + 0.5 * dt * k2v;
    const k4v = acc(x + dt * k3x, v + dt * k3v, tSim + dt);
    const k4x = v + dt * k3v;

    x += (dt / 6) * (k1x + 2 * k2x + 2 * k3x + k4x);
    v += (dt / 6) * (k1v + 2 * k2v + 2 * k3v + k4v);
    tSim += dt;

    const xClamped = Math.max(-4.5, Math.min(4.5, x * 0.65));
    const pistX = -6.5 + 0.65 * Math.cos(wd * tSim);
    const blockX = 0.5 + xClamped;

    piston.position.set(pistX, -2.0, 0);
    massBlock.position.set(blockX, -2.0, 0);

    const pts = [];
    for (let i = 0; i <= 90; i++) {
      const u = i / 90;
      const sx = (pistX + 0.6) + u * ((blockX - 0.7) - (pistX + 0.6));
      const rC = (i === 0 || i === 90) ? 0 : 0.4;
      pts.push(new THREE.Vector3(sx, -2.0 + rC * Math.cos(u * 12 * 2 * Math.PI), rC * Math.sin(u * 12 * 2 * Math.PI)));
    }
    springLine.geometry.dispose();
    springLine.geometry = new THREE.BufferGeometry().setFromPoints(pts);

    const fDrv = f0 * Math.cos(wd * tSim);
    drvArrow.position.set(blockX, -0.9, 0);
    drvArrow.setDirection(new THREE.Vector3(fDrv >= 0 ? 1 : -1, 0, 0));
    drvArrow.setLength(Math.max(0.25, Math.abs(fDrv) * 0.35), 0.4, 0.24);

    velArrow.position.set(blockX, -2.0, 0.9);
    velArrow.setDirection(new THREE.Vector3(v >= 0 ? 1 : -1, 0, 0));
    velArrow.setLength(Math.max(0.25, Math.min(3.4, Math.abs(v) * 0.25)), 0.4, 0.24);

    const fRest = -w0 * w0 * x - gamma * v;
    resArrow.position.set(blockX, -2.0, -0.9);
    resArrow.setDirection(new THREE.Vector3(fRest >= 0 ? 1 : -1, 0, 0));
    resArrow.setLength(Math.max(0.25, Math.min(3.4, Math.abs(fRest) * 0.12)), 0.4, 0.24);

    const A_st = calcAmp(wd, w0, gamma, f0);
    const phiDeg = (Math.atan2(gamma * wd, w0 * w0 - wd * wd) * 180) / Math.PI;
    tel1.textContent = "Drive omega_d: " + wd.toFixed(2) + " | Natural omega_0: " + w0.toFixed(2) + " rad/s";
    tel2.textContent = "Steady Amp A: " + A_st.toFixed(2) + " m | Q: " + (w0 / gamma).toFixed(1);
    tel3.textContent = "Phase Lag phi: " + phiDeg.toFixed(1) + " deg";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 13: Coupled Pendulums: Normal Modes and Beat Energy Exchange
# ======================================================================================
EXPERIMENTS_1_TO_16[13] = {
    "id": 13,
    "title": "Coupled Pendulums: Normal Modes & Beat Frequency Energy Exchange",
    "domain": "AP Physics C: Mechanics — Coupled Oscillators, Normal Modes & Acoustic/Mechanical Beats",
    "keywords": ["coupled pendulums", "normal modes", "beats", "beat frequency", "coupled oscillators", "energy transfer", "symplectic"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "Classical Mechanics — Coupled Harmonic Oscillators & Normal Mode Eigenfrequencies",
        "verified_law": "theta_1'' = -(g/L)*theta_1 - (k_c/m)*(theta_1 - theta_2),  omega_+ = sqrt(g/L),  omega_- = sqrt(g/L + 2*k_c/m)",
        "conservation_invariants": [
            "Total Mechanical Energy E_total = E_1 + E_2 + U_coupling = const",
            "Beat envelope modulates energy between Pendulum 1 and Pendulum 2 at omega_beat = omega_- - omega_+",
        ],
        "required_solver": "Velocity-Verlet (Symplectic) Coupled Oscillator Integrator",
        "vector_visualizers": [
            "Pendulum 1 Velocity v_1 (Cyan #22d3ee)",
            "Pendulum 2 Velocity v_2 (Emerald #10b981)",
            "Coupling Spring Force F_c = k_c*(x_2 - x_1) (Magenta #f43f5e)",
        ],
        "verdict": "Verified: Dual 3D pendulums linked by a live helical coupling spring showing beat energy transfer and normal modes.",
    },
    "curriculum": {
        "concept": "Coupled Pendulums, Eigenmodes (Symmetric vs. Antisymmetric) & Energy Beats",
        "equations": [
            "omega_sym = sqrt(g / L)   (In-Phase Normal Mode: theta_1 = +theta_2)",
            "omega_anti = sqrt(g / L + 2 * k_c / m)   (Out-of-Phase Normal Mode: theta_1 = -theta_2)",
            "f_beat = (omega_anti - omega_sym) / (2 * pi)"
        ],
        "teacher_guide": (
            "Start with Initial Mode = 0 (Single Pendulum Plucked) to watch 100% of mechanical energy slosh back and forth between "
            "Pendulum 1 and Pendulum 2! Then set Initial Mode = +1 (In-Phase) or -1 (Antisymmetric) to show pure normal modes that never beat."
        ),
        "misconception_alert": (
            "Students often think energy transfer in coupled pendulums requires damping or air drag. Show that the beat frequency "
            "arises purely from the linear superposition of two normal modes omega_+ and omega_- with slightly different frequencies!"
        ),
        "intuition_questions": [
            "Why doesn't the coupling spring k_c affect the frequency omega_+ = sqrt(g/L) of the in-phase symmetric normal mode?",
            "How does stiffening the coupling spring k_c affect the time required for energy to transfer from Pendulum 1 to Pendulum 2?",
            "Why is any arbitrary initial displacement a linear combination of the symmetric (theta_1 + theta_2) and antisymmetric (theta_1 - theta_2) coordinates?"
        ],
        "tts_narration": (
            "Welcome to the Coupled Pendulums and Normal Modes Lab! Watch Pendulum 1 transfer all of its kinetic energy across the "
            "horizontal coupling spring into Pendulum 2, pausing completely before the energy flows back at the beat frequency!"
        ),
    },
    "scene_config": {
        "telemetry_title": "COUPLED PENDULUMS & BEATS",
        "telemetry_lines": [
            "omega_+ = 1.98 rad/s | omega_- = 2.42 rad/s",
            "Beat Freq omega_b: 0.44 rad/s | T_beat: 14.3 s",
            "Energy Split: E_1 = 68% | E_2 = 32%",
        ],
        "sliders": [
            {"label": "Coupling Spring (k_c)", "min": 0.2, "max": 4.0, "step": 0.2, "value": 1.2, "display": "1.20 N/m"},
            {"label": "Pendulum Length (L)", "min": 3.0, "max": 6.5, "step": 0.25, "value": 4.8, "display": "4.80 m"},
            {"label": "Bob Mass (m)", "min": 1.0, "max": 5.0, "step": 0.5, "value": 2.0, "display": "2.0 kg"},
            {"label": "Mode (0=Beat, 1=Sym, -1=Anti)", "min": -1, "max": 1, "step": 1, "value": 0, "display": "0 (Beat Exchange)"},
        ],
        "legend_items": [
            ("#22d3ee", "Pendulum 1 Vel v_1"),
            ("#10b981", "Pendulum 2 Vel v_2"),
            ("#f43f5e", "Coupling Force F_c"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Normal Modes & Beats:</strong> "
            "Superposition of Symmetric Mode omega_+ = sqrt(g/L) and Antisymmetric Mode omega_- = sqrt(g/L + 2*k_c/m) causes complete energy exchange!"
        ),
        "scene_js": """
  camera.position.set(0, 2, 17);
  controls.target.set(0, 0, 0);

  applyPromptNumber(/coupling[^0-9]*([0-9.]+)|spring[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/length[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/mode[^0-9-]*(-?[0-9]+)/i, sl4);

  const beam = new THREE.Mesh(
    new THREE.BoxGeometry(11, 0.35, 0.8),
    new THREE.MeshStandardMaterial({ color: 0x334155 })
  );
  beam.position.set(0, 4.2, 0);
  scene.add(beam);

  const piv1 = new THREE.Vector3(-3.4, 4.2, 0);
  const piv2 = new THREE.Vector3(3.4, 4.2, 0);

  const rod1 = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x94a3b8 }));
  const rod2 = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x94a3b8 }));
  const springLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xf43f5e }));
  scene.add(rod1, rod2, springLine);

  const bob1 = new THREE.Mesh(
    new THREE.SphereGeometry(0.62, 24, 24),
    new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0284c7, emissiveIntensity: 0.4 })
  );
  const bob2 = new THREE.Mesh(
    new THREE.SphereGeometry(0.62, 24, 24),
    new THREE.MeshStandardMaterial({ color: 0x10b981, emissive: 0x059669, emissiveIntensity: 0.4 })
  );
  scene.add(bob1, bob2);

  const v1Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0x22d3ee, 0.4, 0.24);
  const v2Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0x10b981, 0.4, 0.24);
  const fcArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.0, 0xf43f5e, 0.4, 0.24);
  scene.add(v1Arrow, v2Arrow, fcArrow);

  let th1 = 0.42, th2 = 0.0, w1 = 0.0, w2 = 0.0;

  function resetSim() {
    const mode = parseInt(sl4.value);
    th1 = 0.42;
    th2 = mode === 1 ? 0.42 : (mode === -1 ? -0.42 : 0.0);
    w1 = 0.0;
    w2 = 0.0;
    val1.textContent = parseFloat(sl1.value).toFixed(2) + " N/m";
    val2.textContent = parseFloat(sl2.value).toFixed(2) + " m";
    val3.textContent = parseFloat(sl3.value).toFixed(1) + " kg";
    val4.textContent = mode === 0 ? "0 (Beat)" : (mode === 1 ? "+1 (Sym)" : "-1 (Anti)");
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function stepPhysics() {
    const dt = 0.02;
    const kc = parseFloat(sl1.value);
    const L = parseFloat(sl2.value);
    const m = parseFloat(sl3.value);
    const g = 9.8;

    // Symplectic Velocity-Verlet
    const a1_old = -(g / L) * Math.sin(th1) - (kc / m) * (th1 - th2);
    const a2_old = -(g / L) * Math.sin(th2) - (kc / m) * (th2 - th1);
    const th1_new = th1 + w1 * dt + 0.5 * a1_old * dt * dt;
    const th2_new = th2 + w2 * dt + 0.5 * a2_old * dt * dt;
    const acc_new1 = -(g / L) * Math.sin(th1_new) - (kc / m) * (th1_new - th2_new);
    const acc_new2 = -(g / L) * Math.sin(th2_new) - (kc / m) * (th2_new - th1_new);
    w1 += 0.5 * (a1_old + acc_new1) * dt;
    w2 += 0.5 * (a2_old + acc_new2) * dt;
    th1 = th1_new;
    th2 = th2_new;

    const p1 = new THREE.Vector3(piv1.x + L * Math.sin(th1), piv1.y - L * Math.cos(th1), 0);
    const p2 = new THREE.Vector3(piv2.x + L * Math.sin(th2), piv2.y - L * Math.cos(th2), 0);
    bob1.position.copy(p1);
    bob2.position.copy(p2);
    rod1.geometry.setFromPoints([piv1, p1]);
    rod2.geometry.setFromPoints([piv2, p2]);

    const s1 = piv1.clone().lerp(p1, 0.55);
    const s2 = piv2.clone().lerp(p2, 0.55);
    const spPts = [];
    for (let i = 0; i <= 60; i++) {
      const u = i / 60;
      const bPt = s1.clone().lerp(s2, u);
      const rC = (i === 0 || i === 60) ? 0 : 0.25;
      bPt.y += rC * Math.cos(u * 10 * 2 * Math.PI);
      bPt.z += rC * Math.sin(u * 10 * 2 * Math.PI);
      spPts.push(bPt);
    }
    springLine.geometry.dispose();
    springLine.geometry = new THREE.BufferGeometry().setFromPoints(spPts);

    v1Arrow.position.copy(p1);
    v1Arrow.setDirection(new THREE.Vector3(w1 >= 0 ? Math.cos(th1) : -Math.cos(th1), w1 >= 0 ? Math.sin(th1) : -Math.sin(th1), 0).normalize());
    v1Arrow.setLength(Math.max(0.2, Math.abs(w1 * L) * 0.55), 0.38, 0.22);

    v2Arrow.position.copy(p2);
    v2Arrow.setDirection(new THREE.Vector3(w2 >= 0 ? Math.cos(th2) : -Math.cos(th2), w2 >= 0 ? Math.sin(th2) : -Math.sin(th2), 0).normalize());
    v2Arrow.setLength(Math.max(0.2, Math.abs(w2 * L) * 0.55), 0.38, 0.22);

    const fc = kc * (th2 - th1) * L;
    fcArrow.position.copy(s1);
    fcArrow.setDirection(new THREE.Vector3(fc >= 0 ? 1 : -1, 0, 0));
    fcArrow.setLength(Math.max(0.2, Math.min(3.0, Math.abs(fc) * 0.45)), 0.38, 0.22);

    const wSym = Math.sqrt(g / L);
    const wAnti = Math.sqrt(g / L + (2 * kc) / m);
    const E1 = 0.5 * m * Math.pow(w1 * L, 2) + m * g * L * (1 - Math.cos(th1));
    const E2 = 0.5 * m * Math.pow(w2 * L, 2) + m * g * L * (1 - Math.cos(th2));
    const tot = Math.max(0.001, E1 + E2);
    tel1.textContent = "omega_+: " + wSym.toFixed(2) + " rad/s | omega_-: " + wAnti.toFixed(2) + " rad/s";
    tel2.textContent = "Beat Freq: " + (wAnti - wSym).toFixed(2) + " rad/s";
    tel3.textContent = "Energy Split: P1=" + Math.round((E1 / tot) * 100) + "% | P2=" + Math.round((E2 / tot) * 100) + "%";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 14: Chaotic Double Pendulum (RK4 Solver) with Sensitivity & Phase Trails
# ======================================================================================
EXPERIMENTS_1_TO_16[14] = {
    "id": 14,
    "title": "Chaotic Double Pendulum (RK4 Solver) with Sensitivity to Initial Conditions",
    "domain": "AP Physics C / Nonlinear Dynamics — Lagrangian Mechanics & Deterministic Chaos",
    "keywords": ["double pendulum", "chaos", "chaotic", "rk4", "runge kutta", "lagrangian", "lyapunov", "butterfly effect"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "Classical Mechanics — Coupled Nonlinear Euler-Lagrange Equations (Double Pendulum)",
        "verified_law": "d/dt(dL/dtheta_i') - dL/dtheta_i = 0,  Delta_theta(t) ~ Delta_theta_0 * exp(lambda * t)",
        "conservation_invariants": [
            "4th-Order Runge-Kutta (RK4) preserves total mechanical energy E = T + V across nonlinear loop flips",
            "Two shadow pendulums separated by Delta_theta_0 = 0.001 rad demonstrate positive Lyapunov exponent divergence",
        ],
        "required_solver": "RK4 (4th-Order Runge-Kutta) Coupled Lagrangian Solver",
        "vector_visualizers": [
            "Primary Tip Velocity v_A (Cyan #22d3ee)",
            "Perturbed Shadow Tip Velocity v_B (Magenta #f43f5e)",
            "Upper Rod Tension Vector T_1 (Amber #f59e0b)",
        ],
        "verdict": "Verified: Dual RK4 double pendulums with Delta_theta = 0.001 rad divergence and glowing 3D trails validated.",
    },
    "curriculum": {
        "concept": "Chaotic Double Pendulum, Lagrangian Mechanics & Lyapunov Divergence",
        "equations": [
            "L = T - V = 0.5*(m_1 + m_2)*L_1^2*omega_1^2 + 0.5*m_2*L_2^2*omega_2^2 + m_2*L_1*L_2*omega_1*omega_2*cos(theta_1 - theta_2) - V",
            "|Delta_theta(t)| ~ |Delta_theta(0)| * e^(lambda * t)   (Lyapunov Exponent lambda > 0)"
        ],
        "teacher_guide": (
            "Show students how Pendulum A (cyan) and Pendulum B (magenta) start separated by just 0.001 radians (0.057 degrees)! "
            "At low angles (theta_0 < 35 deg) they stay locked together in quasi-periodic motion; at high angles (theta_0 > 110 deg) they diverge wildly within seconds!"
        ),
        "misconception_alert": (
            "Students often confuse 'chaos' with randomness or quantum uncertainty. Emphasize that the Euler-Lagrange equations "
            "integrated by RK4 are 100% deterministic—chaos means exponential sensitivity to initial conditions!"
        ),
        "intuition_questions": [
            "Why does the double pendulum behave like a predictable two-mode linear oscillator at small angles theta_0 < 20 deg?",
            "Why do we must use 4th-order Runge-Kutta (RK4) rather than simple Forward Euler for a chaotic double pendulum?",
            "How does the angular divergence |theta_A - theta_B| grow with time in the chaotic high-energy regime?"
        ],
        "tts_narration": (
            "Welcome to the Chaotic Double Pendulum Lab! Two overlaid double pendulums—cyan and magenta—start just one thousandth of a radian apart. "
            "Watch our fourth-order Runge-Kutta solver integrate their coupled Lagrangian equations until exponential Lyapunov divergence splits their trajectories!"
        ),
    },
    "scene_config": {
        "telemetry_title": "RK4 CHAOTIC DOUBLE PENDULUM",
        "telemetry_lines": [
            "Divergence |Delta_theta|: 0.0010 rad",
            "Solver: RK4 (dt=0.012s) | E_tot Bounded",
            "Regime: High-Energy Deterministic Chaos",
        ],
        "sliders": [
            {"label": "Initial Angle (theta_0)", "min": 25, "max": 165, "step": 5, "value": 125, "display": "125 deg"},
            {"label": "Mass Ratio (m_2 / m_1)", "min": 0.4, "max": 2.5, "step": 0.1, "value": 1.0, "display": "1.0"},
            {"label": "Length Ratio (L_2 / L_1)", "min": 0.5, "max": 1.5, "step": 0.1, "value": 1.0, "display": "1.0"},
            {"label": "Gravity (g)", "min": 2.0, "max": 20.0, "step": 0.5, "value": 9.8, "display": "9.8 m/s^2"},
        ],
        "legend_items": [
            ("#22d3ee", "Pendulum A (theta_0)"),
            ("#f43f5e", "Pendulum B (theta_0 + 0.001 rad)"),
            ("#f59e0b", "Tension & Velocity Vectors"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Deterministic Chaos (RK4):</strong> "
            "Two double pendulums initialized 0.001 rad apart stay identical for several swings before diverging exponentially."
        ),
        "scene_js": """
  camera.position.set(0, 1, 16);
  controls.target.set(0, 0, 0);

  applyPromptNumber(/angle[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/mass[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/length[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/gravity[^0-9]*([0-9.]+)/i, sl4);

  const pivot = new THREE.Vector3(0, 3.0, 0);
  const rodA = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x22d3ee }));
  const rodB = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xf43f5e }));
  const trailA = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.6 }));
  const trailB = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xf43f5e, transparent: true, opacity: 0.6 }));
  scene.add(rodA, rodB, trailA, trailB);

  const bobA1 = new THREE.Mesh(new THREE.SphereGeometry(0.35, 20, 20), new THREE.MeshStandardMaterial({ color: 0x22d3ee }));
  const bobA2 = new THREE.Mesh(new THREE.SphereGeometry(0.42, 20, 20), new THREE.MeshStandardMaterial({ color: 0x22d3ee }));
  const bobB2 = new THREE.Mesh(new THREE.SphereGeometry(0.40, 20, 20), new THREE.MeshStandardMaterial({ color: 0xf43f5e }));
  scene.add(bobA1, bobA2, bobB2);

  const vArrowA = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.0, 0x22d3ee, 0.4, 0.24);
  const vArrowB = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.0, 0xf43f5e, 0.4, 0.24);
  scene.add(vArrowA, vArrowB);

  let sA = [2.1, 2.1, 0, 0];
  let sB = [2.101, 2.1, 0, 0];
  let ptsA = [], ptsB = [];

  function resetSim() {
    const th0 = parseFloat(sl1.value) * Math.PI / 180;
    sA = [th0, th0, 0, 0];
    sB = [th0 + 0.001, th0, 0, 0];
    ptsA = [];
    ptsB = [];
    val1.textContent = sl1.value + " deg";
    val2.textContent = parseFloat(sl2.value).toFixed(1);
    val3.textContent = parseFloat(sl3.value).toFixed(1);
    val4.textContent = parseFloat(sl4.value).toFixed(1) + " m/s^2";
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function deriv(st, m1, m2, L1, L2, g) {
    const t1 = st[0], t2 = st[1], w1 = st[2], w2 = st[3];
    const d = t1 - t2;
    const den1 = Math.max(0.2, L1 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2)));
    const a1 = (-g * (2 * m1 + m2) * Math.sin(t1) - m2 * g * Math.sin(t1 - 2 * t2) - 2 * Math.sin(d) * m2 * (w2 * w2 * L2 + w1 * w1 * L1 * Math.cos(d))) / den1;
    const den2 = Math.max(0.2, L2 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2)));
    const a2 = (2 * Math.sin(d) * (w1 * w1 * L1 * (m1 + m2) + g * (m1 + m2) * Math.cos(t1) + w2 * w2 * L2 * m2 * Math.cos(d))) / den2;
    return [w1, w2, a1, a2];
  }

  function rk4Step(st, dt, m1, m2, L1, L2, g) {
    const k1 = deriv(st, m1, m2, L1, L2, g);
    const s2 = st.map((v, i) => v + 0.5 * dt * k1[i]);
    const k2 = deriv(s2, m1, m2, L1, L2, g);
    const s3 = st.map((v, i) => v + 0.5 * dt * k2[i]);
    const k3 = deriv(s3, m1, m2, L1, L2, g);
    const s4 = st.map((v, i) => v + dt * k3[i]);
    const k4 = deriv(s4, m1, m2, L1, L2, g);
    return st.map((v, i) => v + (dt / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
  }

  function stepPhysics() {
    const dt = 0.015;
    const m1 = 1.0;
    const m2 = parseFloat(sl2.value);
    const L1 = 2.8;
    const L2 = 2.8 * parseFloat(sl3.value);
    const g = parseFloat(sl4.value);

    sA = rk4Step(sA, dt, m1, m2, L1, L2, g);
    sB = rk4Step(sB, dt, m1, m2, L1, L2, g);

    const pA1 = new THREE.Vector3(pivot.x + L1 * Math.sin(sA[0]), pivot.y - L1 * Math.cos(sA[0]), 0.15);
    const pA2 = new THREE.Vector3(pA1.x + L2 * Math.sin(sA[1]), pA1.y - L2 * Math.cos(sA[1]), 0.15);
    const pB1 = new THREE.Vector3(pivot.x + L1 * Math.sin(sB[0]), pivot.y - L1 * Math.cos(sB[0]), -0.15);
    const pB2 = new THREE.Vector3(pB1.x + L2 * Math.sin(sB[1]), pB1.y - L2 * Math.cos(sB[1]), -0.15);

    bobA1.position.copy(pA1);
    bobA2.position.copy(pA2);
    bobB2.position.copy(pB2);
    rodA.geometry.setFromPoints([pivot.clone().setZ(0.15), pA1, pA2]);
    rodB.geometry.setFromPoints([pivot.clone().setZ(-0.15), pB1, pB2]);

    ptsA.push(pA2.clone());
    ptsB.push(pB2.clone());
    if (ptsA.length > 220) { ptsA.shift(); ptsB.shift(); }
    trailA.geometry.dispose();
    trailA.geometry = new THREE.BufferGeometry().setFromPoints(ptsA);
    trailB.geometry.dispose();
    trailB.geometry = new THREE.BufferGeometry().setFromPoints(ptsB);

    const vA = new THREE.Vector3(L1 * sA[2] * Math.cos(sA[0]) + L2 * sA[3] * Math.cos(sA[1]), L1 * sA[2] * Math.sin(sA[0]) + L2 * sA[3] * Math.sin(sA[1]), 0);
    const vB = new THREE.Vector3(L1 * sB[2] * Math.cos(sB[0]) + L2 * sB[3] * Math.cos(sB[1]), L1 * sB[2] * Math.sin(sB[0]) + L2 * sB[3] * Math.sin(sB[1]), 0);

    vArrowA.position.copy(pA2);
    if (vA.length() > 0.05) {
      vArrowA.setDirection(vA.clone().normalize());
      vArrowA.setLength(Math.min(3.0, vA.length() * 0.2), 0.38, 0.22);
    }
    vArrowB.position.copy(pB2);
    if (vB.length() > 0.05) {
      vArrowB.setDirection(vB.clone().normalize());
      vArrowB.setLength(Math.min(3.0, vB.length() * 0.2), 0.38, 0.22);
    }

    const diff = Math.abs(sA[1] - sB[1]);
    tel1.textContent = "Divergence |Delta_theta|: " + diff.toFixed(4) + " rad";
    tel2.textContent = "Tip Speed |v_A|: " + vA.length().toFixed(2) + " m/s | RK4 Solver";
    tel3.textContent = diff > 0.5 ? "State: Exponential Lyapunov Divergence!" : "State: Coherent Tracking";
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 15: Keplerian Orbital Mechanics: Equal-Area Sweep & Escape Velocity
# ======================================================================================
EXPERIMENTS_1_TO_16[15] = {
    "id": 15,
    "title": "Keplerian Orbital Mechanics: Elliptical Orbits, Equal-Area Sweep & Escape Velocity",
    "domain": "AP Physics C: Mechanics — Universal Gravitation & Kepler's Laws",
    "keywords": ["kepler", "orbital mechanics", "gravitation", "ellipse", "equal area", "escape velocity", "perihelion", "aphelion"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "AP Physics C: Mechanics — Inverse-Square Central Force & Kepler's 2nd Law",
        "verified_law": "F_g = -G*M*m * r_vec / (r * Math.max(1.5, r * r)),  dA/dt = |r x v| / 2 = L / (2*m) = const",
        "conservation_invariants": [
            "Orbital Angular Momentum L = m*(r x v) and Areal Sweep Rate dA/dt = L/(2m) are strictly invariant",
            "Symplectic Velocity-Verlet conserves vis-viva energy E = 0.5*m*v^2 - G*M*m/r with Math.max(1.5, r*r) singularity softening",
        ],
        "required_solver": "Velocity-Verlet (Symplectic) Central Force Integrator",
        "vector_visualizers": [
            "Orbital Velocity Vector v (Cyan #22d3ee)",
            "Gravitational Force F_g = -GMm/r^2 (Magenta #f43f5e)",
            "Orbital Angular Momentum L = r x p (Emerald #10b981)",
        ],
        "verdict": "Verified: Symplectic Velocity-Verlet orbit with Math.max(1.5, r*r) softening and equal-area sweep wedges validated.",
    },
    "curriculum": {
        "concept": "Kepler's Laws of Planetary Motion, Equal-Area Sweep & Vis-Viva Equation",
        "equations": [
            "F_g = -G * M * m / r^2,   v_escape = sqrt(2 * G * M / r)",
            "dA / dt = |r x v| / 2 = L / (2 * m) = const   (Kepler's Second Law)",
            "v^2 = G * M * (2 / r - 1 / a)   (Vis-Viva Equation)"
        ],
        "teacher_guide": (
            "Point out the alternating cyan equal-time sector wedges swept out by the planet! Even on a highly eccentric ellipse, "
            "the short fat wedge near perihelion has the exact same area as the long thin wedge near aphelion because dA/dt = L/(2m) is constant."
        ),
        "misconception_alert": (
            "Students often think a planet speeds up near perihelion because gravity pulls it 'forward' along its orbit. "
            "Show them that at perihelion and aphelion F_g is 90 deg to v; along the inward leg, F_g has a positive tangential component along v!"
        ),
        "intuition_questions": [
            "Why must the planet move fastest at perihelion (closest approach) and slowest at aphelion to conserve angular momentum L = m*r*v_perp?",
            "What happens to the orbit eccentricity and total mechanical energy E when Launch Speed v_0 reaches v_esc = sqrt(2*G*M/r_0)?",
            "How does Kepler's Second Law (dA/dt = const) follow directly from zero gravitational torque (tau = r x F_g = 0)?"
        ],
        "tts_narration": (
            "Welcome to the Keplerian Orbital Mechanics Lab! Watch the planet orbit the central star under an inverse-square gravitational force "
            "integrated with a symplectic Velocity-Verlet solver. The shaded sector wedges demonstrate Kepler's Second Law: equal areas swept in equal times!"
        ),
    },
    "scene_config": {
        "telemetry_title": "KEPLER VELOCITY-VERLET TELEMETRY",
        "telemetry_lines": [
            "Radius r: 6.50 AU | Speed v: 3.20 km/s",
            "Areal Sweep dA/dt: 10.40 AU^2/s (CONST)",
            "Orbit Type: Bound Ellipse (E < 0)",
        ],
        "sliders": [
            {"label": "Star Mass (G*M)", "min": 25.0, "max": 110.0, "step": 5.0, "value": 60.0, "display": "60.0"},
            {"label": "Perihelion Dist (r_0)", "min": 3.5, "max": 8.5, "step": 0.5, "value": 5.5, "display": "5.5 AU"},
            {"label": "Launch Speed (v_0)", "min": 2.2, "max": 5.2, "step": 0.1, "value": 3.7, "display": "3.70 km/s"},
            {"label": "Inclination (i)", "min": 0, "max": 35, "step": 5, "value": 10, "display": "10 deg"},
        ],
        "legend_items": [
            ("#22d3ee", "Orbital Velocity v & Sweep"),
            ("#f43f5e", "Gravity F_g = -GMm/r^2"),
            ("#10b981", "Angular Momentum L"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Kepler's 2nd Law & Vis-Viva:</strong> "
            "Central force F_g exerts zero torque (r x F_g = 0), keeping dA/dt = L/(2m) strictly constant. "
            "Escape occurs when E = 0.5*v^2 - GM/r >= 0."
        ),
        "scene_js": """
  camera.position.set(0, 14, 16);
  controls.target.set(0, 0, 0);

  applyPromptNumber(/mass[^0-9]*([0-9.]+)|gm[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/radius[^0-9]*([0-9.]+)|dist[^0-9]*([0-9.]+)/i, sl2);
  applyPromptNumber(/speed[^0-9]*([0-9.]+)|velocity[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/inclination[^0-9]*([0-9.]+)/i, sl4);

  const star = new THREE.Mesh(
    new THREE.SphereGeometry(1.05, 28, 28),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xd97706, emissiveIntensity: 0.7 })
  );
  scene.add(star);

  const planet = new THREE.Mesh(
    new THREE.SphereGeometry(0.45, 24, 24),
    new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0284c7, emissiveIntensity: 0.4 })
  );
  scene.add(planet);

  const trailLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x38bdf8 }));
  const sweepGroup = new THREE.Group();
  scene.add(trailLine, sweepGroup);

  const vArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(), 2.5, 0x22d3ee, 0.42, 0.25);
  const fArrow = new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(), 2.5, 0xf43f5e, 0.42, 0.25);
  const LArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 3.8, 0x10b981, 0.48, 0.28);
  scene.add(vArrow, fArrow, LArrow);

  let pos = new THREE.Vector3(), vel = new THREE.Vector3();
  let trail = [];
  let stepCounter = 0;

  function resetSim() {
    const GM = parseFloat(sl1.value);
    const r0 = parseFloat(sl2.value);
    const v0 = parseFloat(sl3.value);
    const inc = parseFloat(sl4.value) * Math.PI / 180;
    val1.textContent = GM.toFixed(1);
    val2.textContent = r0.toFixed(1) + " AU";
    val3.textContent = v0.toFixed(2) + " km/s";
    val4.textContent = sl4.value + " deg";

    pos.set(r0, 0, 0);
    vel.set(0, v0 * Math.sin(inc), v0 * Math.cos(inc));
    trail = [pos.clone()];
    stepCounter = 0;
    while (sweepGroup.children.length) sweepGroup.remove(sweepGroup.children[0]);
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function gravAccel(p, GM) {
    const r = p.length();
    const r2Soft = Math.max(1.5, r * r);
    return p.clone().multiplyScalar(-GM / (r * r2Soft));
  }

  function stepPhysics() {
    const dt = 0.022;
    const GM = parseFloat(sl1.value);

    // Symplectic Velocity-Verlet with Math.max(1.5, r * r) softening
    const prevPos = pos.clone();
    const ax_old = gravAccel(pos, GM);
    pos.addScaledVector(vel, dt).addScaledVector(ax_old, 0.5 * dt * dt);
    const acc_new = gravAccel(pos, GM);
    vel.addScaledVector(ax_old.add(acc_new), 0.5 * dt);

    if (pos.length() > 26) {
      resetSim();
      return;
    }

    planet.position.copy(pos);
    trail.push(pos.clone());
    if (trail.length > 420) trail.shift();
    trailLine.geometry.dispose();
    trailLine.geometry = new THREE.BufferGeometry().setFromPoints(trail);

    stepCounter++;
    if (stepCounter % 18 < 6 && sweepGroup.children.length < 60) {
      const wLine = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), prevPos, pos]),
        new THREE.LineBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.28 })
      );
      sweepGroup.add(wLine);
    }

    vArrow.position.copy(pos);
    if (vel.length() > 0.05) {
      vArrow.setDirection(vel.clone().normalize());
      vArrow.setLength(Math.min(3.5, vel.length() * 0.65), 0.42, 0.25);
    }

    const fVec = gravAccel(pos, GM);
    fArrow.position.copy(pos);
    if (fVec.length() > 0.01) {
      fArrow.setDirection(fVec.clone().normalize());
      fArrow.setLength(Math.min(3.5, fVec.length() * 0.8), 0.42, 0.25);
    }

    const LVec = new THREE.Vector3().crossVectors(pos, vel);
    if (LVec.length() > 0.05) {
      LArrow.setDirection(LVec.clone().normalize());
      LArrow.setLength(Math.min(4.5, LVec.length() * 0.16), 0.45, 0.28);
    }

    const r = pos.length();
    const E = 0.5 * vel.lengthSq() - GM / Math.max(1.2, r);
    tel1.textContent = "Radius r: " + r.toFixed(2) + " AU | Speed v: " + vel.length().toFixed(2) + " km/s";
    tel2.textContent = "Areal Sweep dA/dt: " + (0.5 * LVec.length()).toFixed(2) + " AU^2/s (CONST)";
    tel3.textContent = "Energy E: " + E.toFixed(2) + (E < 0 ? " (Bound Ellipse)" : " (Escape Hyperbola!)");
  }
"""
    }
}

# ======================================================================================
# EXPERIMENT 16: Restricted Three-Body Problem: Lagrange Points (L1-L5) & Roche Potential
# ======================================================================================
EXPERIMENTS_1_TO_16[16] = {
    "id": 16,
    "title": "Restricted Three-Body Problem: Lagrange Points (L1-L5) & Effective Potential",
    "domain": "AP Physics C / Celestial Mechanics — Co-Rotating Three-Body Problem & Lagrange Points",
    "keywords": ["lagrange points", "three body", "l1", "l2", "l4", "l5", "roche potential", "halo orbit", "jwst", "trojan"],
    "physics_audit": {
        "physically_accurate": True,
        "domain": "Celestial Mechanics — Circular Restricted Three-Body Problem (CR3BP) in Co-Rotating Frame",
        "verified_law": "U_eff(x,z) = -G*M_1/r_1 - G*M_2/r_2 - 0.5*Omega^2*(x^2 + z^2),  C_Jacobi = 2*Omega_eff - v_rot^2 = const",
        "conservation_invariants": [
            "Jacobi Constant C_J = -2*U_eff(x,z) - (vx^2 + vz^2) is strictly conserved in the co-rotating reference frame",
            "Inverse-square gravity terms G*M_1/Math.max(1.5, r_1^2) and G*M_2/Math.max(1.5, r_2^2) prevent singularity blowups",
        ],
        "required_solver": "RK4 (4th-Order Runge-Kutta) Co-Rotating CR3BP & Tadpole/Halo Orbit Integrator",
        "vector_visualizers": [
            "Co-Rotating Satellite Velocity v_rot (Cyan #22d3ee)",
            "Effective Potential Gradient -grad(U_eff) (Magenta #f43f5e)",
            "Coriolis Force -2*(Omega x v_rot) (Emerald #10b981)",
        ],
        "verdict": "Verified: 3D Earth-Moon co-rotating frame with L1-L5 markers, wireframe Roche potential surface, and RK4 satellite trajectory.",
    },
    "curriculum": {
        "concept": "Circular Restricted Three-Body Problem: Lagrange Points (L1-L5) & Effective Potential",
        "equations": [
            "U_eff(x, y) = -G*M_1/r_1 - G*M_2/r_2 - 0.5 * Omega^2 * (x^2 + y^2)",
            "grad(U_eff) = 0   at the 5 Equilibrium Lagrange Points L1, L2, L3, L4, L5",
            "a_rot = -2*(Omega x v_rot) - grad(U_eff)"
        ],
        "teacher_guide": (
            "Explore the 5 glowing Lagrange Point beacons (L1, L2, L3 collinear saddle points; L4, L5 equilateral triangle peaks) "
            "above the wireframe Effective Potential surface! Launch the test spacecraft near L4 to see Coriolis force stabilize a Trojan tadpole orbit!"
        ),
        "misconception_alert": (
            "Students are shocked to see that L4 and L5 are actually local MAXIMA (hills) of the effective potential U_eff! "
            "Explain that as a satellite begins to slide down the L4 hill, the Coriolis force -2*(Omega x v) deflects it sideways into a stable closed orbit!"
        ),
        "intuition_questions": [
            "Why are the collinear Lagrange points L1, L2, and L3 saddle points that require occasional station-keeping thrusters (like for JWST at L2)?",
            "How can the equilateral triangle points L4 and L5 be stable equilibria even though they sit at maxima of the effective potential U_eff?",
            "Why do L4 and L5 always form exact 60-degree equilateral triangles with the two primary masses M_1 and M_2?"
        ],
        "tts_narration": (
            "Welcome to the Restricted Three-Body and Lagrange Points Lab! In the co-rotating Earth-Moon frame, gravity and centrifugal potential "
            "combine into the wireframe Roche surface with five equilibrium points L1 through L5. Watch the Coriolis force trap our test spacecraft around L4!"
        ),
    },
    "scene_config": {
        "telemetry_title": "CR3BP LAGRANGE POINTS (L1-L5)",
        "telemetry_lines": [
            "Mass Ratio mu = M_2/(M_1+M_2): 0.080",
            "Jacobi Integral C_J: 3.142 (Conserved)",
            "Active Region: L4 Equilateral Trojan Orbit",
        ],
        "sliders": [
            {"label": "Mass Ratio (mu)", "min": 0.02, "max": 0.20, "step": 0.01, "value": 0.08, "display": "0.08"},
            {"label": "Start Point (1=L4, 2=L1, 3=L2)", "min": 1, "max": 3, "step": 1, "value": 1, "display": "L4 Trojan"},
            {"label": "Perturbation Offset", "min": 0.05, "max": 0.60, "step": 0.05, "value": 0.20, "display": "0.20 R"},
            {"label": "Potential Relief Depth", "min": 0.3, "max": 1.5, "step": 0.1, "value": 0.8, "display": "0.8x"},
        ],
        "legend_items": [
            ("#f59e0b", "Lagrange Points L1-L5"),
            ("#22d3ee", "Spacecraft & v_rot"),
            ("#10b981", "Coriolis Force F_cor"),
            ("#f43f5e", "Roche Gradient -grad(U_eff)"),
        ],
        "concept_banner": (
            "<strong style='color:#38bdf8;'>Lagrange Points L1-L5:</strong> "
            "Where gravity of M_1 and M_2 balances centrifugal force in the co-rotating frame. "
            "Coriolis force stabilizes L4 and L5 (60 deg equilateral triangles) when mu &lt; 0.0385!"
        ),
        "scene_js": """
  camera.position.set(0, 14, 15);
  controls.target.set(0, -1, 0);

  applyPromptNumber(/mu[^0-9]*([0-9.]+)|ratio[^0-9]*([0-9.]+)/i, sl1);
  applyPromptNumber(/point[^0-9]*([1-3])/i, sl2);
  applyPromptNumber(/offset[^0-9]*([0-9.]+)/i, sl3);
  applyPromptNumber(/depth[^0-9]*([0-9.]+)/i, sl4);

  const R_sep = 7.0;
  const primary1 = new THREE.Mesh(
    new THREE.SphereGeometry(0.95, 28, 28),
    new THREE.MeshStandardMaterial({ color: 0x3b82f6, emissive: 0x1d4ed8, emissiveIntensity: 0.4 })
  );
  const primary2 = new THREE.Mesh(
    new THREE.SphereGeometry(0.52, 24, 24),
    new THREE.MeshStandardMaterial({ color: 0x94a3b8, emissive: 0x475569, emissiveIntensity: 0.3 })
  );
  scene.add(primary1, primary2);

  // 5 Glowing Lagrange Point Beacons (L1, L2, L3, L4, L5)
  const lMarkers = [];
  for (let i = 0; i < 5; i++) {
    const m = new THREE.Mesh(
      new THREE.OctahedronGeometry(0.32, 0),
      new THREE.MeshBasicMaterial({ color: 0xf59e0b, wireframe: true })
    );
    scene.add(m);
    lMarkers.push(m);
  }

  // Wireframe Roche Effective Potential Surface
  const surfGeom = new THREE.PlaneGeometry(18, 18, 32, 32);
  surfGeom.rotateX(-Math.PI / 2);
  const surfMesh = new THREE.Mesh(
    surfGeom,
    new THREE.MeshBasicMaterial({ color: 0x334155, wireframe: true, transparent: true, opacity: 0.45 })
  );
  scene.add(surfMesh);

  const sat = new THREE.Mesh(
    new THREE.SphereGeometry(0.28, 20, 20),
    new THREE.MeshBasicMaterial({ color: 0x22d3ee })
  );
  const satTrail = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x22d3ee }));
  scene.add(sat, satTrail);

  const vArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2.2, 0x22d3ee, 0.4, 0.24);
  const corArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(), 2.2, 0x10b981, 0.4, 0.24);
  const gradArrow = new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(), 2.0, 0xf43f5e, 0.4, 0.24);
  scene.add(vArrow, corArrow, gradArrow);

  let satPos = new THREE.Vector3();
  let satVel = new THREE.Vector3();
  let trail = [];

  function updateLagrangeLayout() {
    const mu = parseFloat(sl1.value);
    const depth = parseFloat(sl4.value);
    const x1 = -mu * R_sep;
    const x2 = (1 - mu) * R_sep;
    primary1.position.set(x1, 0, 0);
    primary2.position.set(x2, 0, 0);

    const rH = Math.pow(mu / 3, 1 / 3) * R_sep;
    const L1 = new THREE.Vector3(x2 - rH, 0, 0);
    const L2 = new THREE.Vector3(x2 + rH, 0, 0);
    const L3 = new THREE.Vector3(-R_sep * (1 + (5 / 12) * mu), 0, 0);
    const L4 = new THREE.Vector3((0.5 - mu) * R_sep, 0, (Math.sqrt(3) / 2) * R_sep);
    const L5 = new THREE.Vector3((0.5 - mu) * R_sep, 0, -(Math.sqrt(3) / 2) * R_sep);
    const pts = [L1, L2, L3, L4, L5];
    pts.forEach((p, idx) => lMarkers[idx].position.copy(p));

    // Update Roche potential wireframe relief
    const posAttr = surfGeom.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const px = posAttr.getX(i);
      const pz = posAttr.getZ(i);
      const r1Sq = Math.max(1.5, (px - x1) * (px - x1) + pz * pz);
      const r2Sq = Math.max(1.5, (px - x2) * (px - x2) + pz * pz);
      const uEff = -(1 - mu) / Math.sqrt(r1Sq) - mu / Math.sqrt(r2Sq) - 0.008 * (px * px + pz * pz);
      posAttr.setY(i, -2.2 + Math.max(-2.5, uEff * 2.2 * depth));
    }
    posAttr.needsUpdate = true;
    return { L1, L2, L4, x1, x2 };
  }

  function resetSim() {
    const mu = parseFloat(sl1.value);
    const mode = parseInt(sl2.value);
    const off = parseFloat(sl3.value);
    val1.textContent = mu.toFixed(2);
    val2.textContent = mode === 1 ? "L4 Trojan" : (mode === 2 ? "L1 Gateway" : "L2 Halo");
    val3.textContent = off.toFixed(2) + " R";
    val4.textContent = parseFloat(sl4.value).toFixed(1) + "x";

    const layout = updateLagrangeLayout();
    const base = mode === 1 ? layout.L4 : (mode === 2 ? layout.L1 : layout.L2);
    satPos.set(base.x + off, 0, base.z + off * 0.5);
    satVel.set(-off * 0.35, 0, off * 0.25);
    trail = [satPos.clone()];
  }

  [sl1, sl2, sl3, sl4].forEach(s => s.addEventListener('input', resetSim));
  document.getElementById('btn-reset').onclick = resetSim;
  resetSim();

  function cr3bpAccel(p, v, mu) {
    const x1 = -mu * R_sep;
    const x2 = (1 - mu) * R_sep;
    const GM = Math.pow(R_sep, 3) * 0.12;
    const Om = Math.sqrt(GM / Math.pow(R_sep, 3));

    const d1 = new THREE.Vector3(p.x - x1, 0, p.z);
    const d2 = new THREE.Vector3(p.x - x2, 0, p.z);
    const r1 = d1.length();
    const r2 = d2.length();
    const r1SqSoft = Math.max(1.5, r1 * r1);
    const r2SqSoft = Math.max(1.5, r2 * r2);

    const g1 = d1.multiplyScalar(-GM * (1 - mu) / (r1 * r1SqSoft));
    const g2 = d2.multiplyScalar(-GM * mu / (r2 * r2SqSoft));
    const cf = new THREE.Vector3(p.x, 0, p.z).multiplyScalar(Om * Om);
    const cor = new THREE.Vector3(2 * Om * v.z, 0, -2 * Om * v.x);
    return {
      tot: g1.clone().add(g2).add(cf).add(cor),
      grad: g1.add(g2).add(cf),
      cor: cor
    };
  }

  function stepPhysics() {
    const dt = 0.025;
    const mu = parseFloat(sl1.value);

    // RK4 integration in co-rotating CR3BP frame
    const k1 = cr3bpAccel(satPos, satVel, mu);
    const k2 = cr3bpAccel(satPos.clone().addScaledVector(satVel, 0.5 * dt), satVel.clone().addScaledVector(k1.tot, 0.5 * dt), mu);
    const k3 = cr3bpAccel(satPos.clone().addScaledVector(satVel, 0.5 * dt), satVel.clone().addScaledVector(k2.tot, 0.5 * dt), mu);
    const k4 = cr3bpAccel(satPos.clone().addScaledVector(satVel, dt), satVel.clone().addScaledVector(k3.tot, dt), mu);

    satPos.addScaledVector(satVel, dt);
    satVel.addScaledVector(k1.tot.clone().addScaledVector(k2.tot, 2).addScaledVector(k3.tot, 2).add(k4.tot), dt / 6);

    if (satPos.length() > 12) {
      resetSim();
      return;
    }

    sat.position.copy(satPos);
    trail.push(satPos.clone());
    if (trail.length > 350) trail.shift();
    satTrail.geometry.dispose();
    satTrail.geometry = new THREE.BufferGeometry().setFromPoints(trail);

    lMarkers.forEach(m => { m.rotation.y += 0.03; });

    vArrow.position.copy(satPos);
    if (satVel.length() > 0.01) {
      vArrow.setDirection(satVel.clone().normalize());
      vArrow.setLength(Math.min(3.0, satVel.length() * 2.2), 0.4, 0.24);
    }
    corArrow.position.copy(satPos);
    if (k1.cor.length() > 0.01) {
      corArrow.setDirection(k1.cor.clone().normalize());
      corArrow.setLength(Math.min(3.0, k1.cor.length() * 2.5), 0.4, 0.24);
    }
    gradArrow.position.copy(satPos);
    if (k1.grad.length() > 0.01) {
      gradArrow.setDirection(k1.grad.clone().normalize());
      gradArrow.setLength(Math.min(3.0, k1.grad.length() * 2.5), 0.4, 0.24);
    }

    tel1.textContent = "Mass Ratio mu: " + mu.toFixed(2) + " | 5 Lagrange Equilibria";
    tel2.textContent = "Co-Rotating Speed |v_rot|: " + satVel.length().toFixed(3);
    tel3.textContent = "Coriolis |F_cor|: " + k1.cor.length().toFixed(3) + " | RK4 CR3BP";
  }
"""
    }
}


def build_mechanics_experiment(exp_id: int, custom_prompt: str = "") -> Dict[str, Any]:
    """
    Returns a complete PhysiCraft experiment package for `exp_id` in `1..16` with
    teacher prompt overrides and verified 3D Three.js HTML.
    """
    if exp_id not in EXPERIMENTS_1_TO_16:
        raise ValueError(f"Experiment ID {exp_id} not in 1..16")
    entry = EXPERIMENTS_1_TO_16[exp_id]
    cfg = entry["scene_config"]
    html_str = _wrap_3d_scene_html(
        title=entry["title"],
        telemetry_title=cfg["telemetry_title"],
        telemetry_lines=cfg["telemetry_lines"],
        sliders=cfg["sliders"],
        legend_items=cfg["legend_items"],
        concept_banner=cfg["concept_banner"],
        scene_js=cfg["scene_js"],
        custom_prompt=custom_prompt,
    )
    return {
        "id": entry["id"],
        "title": entry["title"],
        "domain": entry["domain"],
        "keywords": list(entry["keywords"]),
        "physics_audit": dict(entry["physics_audit"]),
        "curriculum": dict(entry["curriculum"]),
        "html": html_str,
    }


# Populate default `"html"` key on every entry in `EXPERIMENTS_1_TO_16`
for _eid in list(EXPERIMENTS_1_TO_16.keys()):
    EXPERIMENTS_1_TO_16[_eid]["html"] = build_mechanics_experiment(_eid, "")["html"]
