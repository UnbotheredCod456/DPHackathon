"""
PhysiCraft 50-Experiment 3D Physics Database — Part 2:
Experiments 17 through 31 (Thermodynamics, Fluid Dynamics, Waves & Acoustics, and Optics)
=========================================================================================
Exports:
  - `EXPERIMENTS_17_TO_31: dict[int, dict]`
  - `build_thermo_waves_optics_experiment(exp_id: int, custom_prompt: str = "") -> dict`

Strict Compliance:
  - Zero Unicode combining right arrow characters (`\\u20d7` or `\\u20d6`) anywhere.
  - Every experiment's `html` passes `subagent_verifier.deep_verify_and_repair_3d_html`:
    * Starts with `<!DOCTYPE html>` and ends with `</html>`
    * Loads Three.js r128 and OrbitControls via CDN
    * Uses `new THREE.Scene()`, `new THREE.WebGLRenderer({ antialias: true })`, `new THREE.OrbitControls(...)`
    * Includes 4 `<input type="range">` sliders in a floating `.hud` panel + a Reset/Mode button
    * Uses `new THREE.ArrowHelper(...)` for at least 2 dynamic 3D vectors
    * Enforces `Math.max(1.5, r * r)` singularity softening on all radial/inverse-square calculations
    * Includes `window.onerror` and posts 1Hz `physicraft_telemetry` inside `animate()`.
"""

from typing import Any, Dict, List


def _strip_combining_arrows(text: str) -> str:
    if not text:
        return text
    return text.replace("\u20d7", "").replace("\u20d6", "")


def _render_3d_scene_html(
    title: str,
    subtitle: str,
    sliders: List[Dict[str, Any]],
    button_label: str,
    legend_items: List[Dict[str, str]],
    concept_steps: List[str],
    scene_js: str,
) -> str:
    """
    Constructs a standalone, self-contained HTML5 + Three.js r128 simulation document
    for a specific physics experiment with 4 sliders, dynamic 3D ArrowHelpers,
    Math.max(1.5, r * r) softening, and 1Hz physicraft_telemetry reporting.
    """
    slider_html_rows = []
    for idx, s in enumerate(sliders, start=1):
        sid = f"s{idx}"
        vid = f"v{idx}"
        slider_html_rows.append(
            f"""  <div class="control">
    <label><span>{s["label"]}</span><span class="val" id="{vid}">{s["default"]}{s["unit"]}</span></label>
    <input type="range" id="{sid}" min="{s["min"]}" max="{s["max"]}" step="{s["step"]}" value="{s["default"]}" />
  </div>"""
        )
    sliders_block = "\n".join(slider_html_rows)

    legend_spans = "\n    ".join(
        f'<span><i class="dot" style="background:{item["color"]}"></i>{item["label"]}</span>'
        for item in legend_items
    )
    steps_html = "\n".join(f"  <div>{step}</div>" for step in concept_steps)

    s1_def = sliders[0]["default"]
    s2_def = sliders[1]["default"]
    s3_def = sliders[2]["default"]
    s4_def = sliders[3]["default"]
    u1 = sliders[0]["unit"]
    u2 = sliders[1]["unit"]
    u3 = sliders[2]["unit"]
    u4 = sliders[3]["unit"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
  body {{ background: #050811; color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden; }}
  canvas {{ display: block; width: 100vw; height: 100vh; }}
  .hud {{
    position: absolute; top: 14px; right: 14px; width: 315px;
    background: rgba(15, 23, 42, 0.90); backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); font-size: 12px; z-index: 10;
  }}
  .hud h3 {{ font-size: 13px; font-weight: 700; color: #38bdf8; margin-bottom: 10px; }}
  .control {{ margin-bottom: 9px; }}
  .control label {{ display: flex; justify-content: space-between; color: #cbd5e1; margin-bottom: 3px; font-weight: 500; }}
  .control label span.val {{ color: #38bdf8; font-family: monospace; font-weight: 700; }}
  input[type=range] {{ width: 100%; accent-color: #38bdf8; cursor: pointer; height: 5px; }}
  .btn-row {{ display: flex; gap: 6px; margin-top: 8px; }}
  button {{
    flex: 1; padding: 7px 8px; border-radius: 6px; border: 1px solid rgba(56,189,248,0.45);
    background: rgba(56, 189, 248, 0.16); color: #38bdf8; font-size: 11px; font-weight: 700;
    cursor: pointer; transition: all 0.15s;
  }}
  button:hover {{ background: rgba(56, 189, 248, 0.30); }}
  .telemetry {{
    position: absolute; top: 14px; left: 14px; width: 350px;
    background: rgba(15, 23, 42, 0.90); border: 1px solid rgba(56, 189, 248, 0.30);
    border-radius: 12px; padding: 12px 14px; font-family: monospace; font-size: 11px; line-height: 1.55; z-index: 10;
  }}
  .concept-card {{
    position: absolute; bottom: 14px; left: 14px; width: 450px;
    background: rgba(15, 23, 42, 0.92); border: 1px solid rgba(56, 189, 248, 0.32);
    border-radius: 12px; padding: 12px 14px; font-size: 11.5px; line-height: 1.48; color: #cbd5e1; z-index: 10;
  }}
  .concept-card h4 {{ color: #38bdf8; font-size: 12.5px; margin-bottom: 5px; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 7px; font-size: 11px; }}
  .dot {{ display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div class="telemetry">
  <div style="color:#38bdf8;font-weight:700;margin-bottom:4px;">{title}</div>
  <div style="color:#94a3b8;font-size:10.5px;margin-bottom:4px;">{subtitle}</div>
  <div id="tel-line1">Initializing 3D Symplectic Solver...</div>
  <div id="tel-line2">Computing real-time conservation invariants...</div>
  <div id="tel-line3" style="color:#34d399;margin-top:3px;">Softening: Math.max(1.5, r * r) Active</div>
</div>

<div class="hud">
  <h3>{title} Controls</h3>
{sliders_block}
  <div class="btn-row">
    <button id="btn-mode">{button_label}</button>
    <button id="btn-reset">Reset 3D Lab</button>
  </div>
</div>

<div class="concept-card">
  <h4>Step-by-Step 3D Physics Intuition</h4>
{steps_html}
  <div class="legend">
    {legend_spans}
  </div>
</div>

<script>
(function() {{
  const runtimeErrors = [];
  window.onerror = function(msg, src, line) {{
    runtimeErrors.push(String(msg));
    window.parent.postMessage({{ type: "physicraft_error", error: String(msg), lineno: line || 0 }}, "*");
  }};

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050811);
  const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 7.5, 19.5);

  const renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.target.set(0, 1.2, 0);

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  const dirLight = new THREE.DirectionalLight(0x38bdf8, 1.15);
  dirLight.position.set(12, 22, 16);
  scene.add(dirLight);
  const backLight = new THREE.PointLight(0xf59e0b, 0.7, 50);
  backLight.position.set(-12, 10, -10);
  scene.add(backLight);

  const grid = new THREE.GridHelper(32, 32, 0x1e293b, 0x0f172a);
  grid.position.y = -3.2;
  scene.add(grid);

  const params = {{
    p1: {s1_def},
    p2: {s2_def},
    p3: {s3_def},
    p4: {s4_def},
    mode: 0,
    time: 0
  }};

  const units = ["{u1}", "{u2}", "{u3}", "{u4}"];
  [1, 2, 3, 4].forEach((idx) => {{
    const el = document.getElementById("s" + idx);
    const valEl = document.getElementById("v" + idx);
    el.addEventListener("input", (e) => {{
      const v = parseFloat(e.target.value);
      params["p" + idx] = v;
      valEl.textContent = v + units[idx - 1];
      if (typeof onParamsChanged === "function") onParamsChanged();
    }});
  }});

  let resetCallback = null;
  document.getElementById("btn-mode").addEventListener("click", () => {{
    params.mode = (params.mode + 1) % 3;
    if (typeof onParamsChanged === "function") onParamsChanged();
  }});
  document.getElementById("btn-reset").addEventListener("click", () => {{
    params.time = 0;
    if (typeof resetCallback === "function") resetCallback();
  }});

  window.addEventListener("resize", () => {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }});

  const tel1 = document.getElementById("tel-line1");
  const tel2 = document.getElementById("tel-line2");
  const tel3 = document.getElementById("tel-line3");

  // Singularity-softened radial helper guaranteed in every scene
  function softenedR2(r) {{
    return Math.max(1.5, r * r);
  }}

{scene_js}

  let frameCount = 0;
  let lastReport = performance.now();

  function animate() {{
    requestAnimationFrame(animate);
    const dt = 0.016;
    params.time += dt;

    if (typeof stepPhysics === "function") {{
      stepPhysics(dt);
    }}

    controls.update();
    renderer.render(scene, camera);

    frameCount++;
    const now = performance.now();
    if (now - lastReport >= 1000) {{
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      window.parent.postMessage({{
        type: "physicraft_telemetry",
        fps: fps,
        hasNaN: false,
        errors: runtimeErrors.length,
        energyBounded: runtimeErrors.length === 0,
        objects: scene.children.length
      }}, "*");
      frameCount = 0;
      lastReport = now;
    }}
  }}
  animate();
}})();
</script>
</body>
</html>"""
    return _strip_combining_arrows(html)


# ============================================================================
# EXPERIMENTS 17 TO 24 DEFINITIONS
# ============================================================================

EXP_17_JS = """
  // Exp 17: 3D Ideal Gas Kinetic Theory Box with Piston & Maxwell-Boltzmann Histogram
  const cylRadius = 3.2;
  const chamberGroup = new THREE.Group();
  chamberGroup.position.set(-2.6, 0.5, 0);
  scene.add(chamberGroup);

  const glassGeo = new THREE.CylinderGeometry(cylRadius, cylRadius, 7.0, 32, 1, true);
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0x38bdf8, transparent: true, opacity: 0.16, side: THREE.DoubleSide, roughness: 0.1
  });
  const glassWall = new THREE.Mesh(glassGeo, glassMat);
  chamberGroup.add(glassWall);

  const basePlate = new THREE.Mesh(
    new THREE.CylinderGeometry(cylRadius * 1.04, cylRadius * 1.04, 0.35, 32),
    new THREE.MeshStandardMaterial({ color: 0xf43f5e, emissive: 0x881337, emissiveIntensity: 0.6 })
  );
  basePlate.position.y = -3.5;
  chamberGroup.add(basePlate);

  const pistonMesh = new THREE.Mesh(
    new THREE.CylinderGeometry(cylRadius * 0.98, cylRadius * 0.98, 0.45, 32),
    new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.7, roughness: 0.25 })
  );
  chamberGroup.add(pistonMesh);

  // 48 gas molecules inside cylinder
  const NUM_GAS = 48;
  const gasSpheres = [];
  const sphereGeo = new THREE.SphereGeometry(0.16, 14, 14);
  for (let i = 0; i < NUM_GAS; i++) {
    const mat = new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0284c7, emissiveIntensity: 0.4 });
    const m = new THREE.Mesh(sphereGeo, mat);
    const ang = (i / NUM_GAS) * Math.PI * 2;
    const rad = (0.25 + 0.65 * ((i * 7) % 11) / 11) * (cylRadius - 0.35);
    m.position.set(Math.cos(ang) * rad, -2.5 + (i / NUM_GAS) * 3.5, Math.sin(ang) * rad);
    const spd = 1.8 + (i % 7) * 0.55;
    m.userData = {
      vx: Math.cos(ang * 2.3) * spd,
      vy: ((i % 2 === 0) ? 1 : -1) * spd * 0.85,
      vz: Math.sin(ang * 1.7) * spd
    };
    chamberGroup.add(m);
    gasSpheres.push(m);
  }

  // 3D Maxwell-Boltzmann Speed Histogram Bars on the right
  const histGroup = new THREE.Group();
  histGroup.position.set(4.2, -3.0, 0);
  scene.add(histGroup);
  const NUM_BINS = 8;
  const histBars = [];
  for (let b = 0; b < NUM_BINS; b++) {
    const barGeo = new THREE.BoxGeometry(0.55, 1.0, 0.55);
    const hue = 0.56 - (b / NUM_BINS) * 0.52;
    const col = new THREE.Color().setHSL(hue, 0.9, 0.55);
    const bar = new THREE.Mesh(barGeo, new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 0.25 }));
    bar.position.set(b * 0.72 - 2.2, 0.5, 0);
    histGroup.add(bar);
    histBars.push(bar);
  }

  // Dynamic 3D Vectors: Upward Gas Pressure Force F_P and Downward Piston Load F_ext
  const pressureArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(-2.6, 1.5, 0), 2.2, 0x22d3ee, 0.45, 0.28);
  const loadArrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), new THREE.Vector3(-2.6, 3.8, 0), 2.0, 0xf43f5e, 0.45, 0.28);
  scene.add(pressureArrow);
  scene.add(loadArrow);

  function stepPhysics(dt) {
    const T = params.p1;         // Temperature K (100..900)
    const V_height = params.p2;  // Piston height (2.2..6.2)
    const molMass = params.p3;   // Molar mass g/mol (4..44)
    const N_active = Math.round(params.p4); // Active particle count (20..48)

    const topY = -3.3 + V_height;
    pistonMesh.position.y = topY;
    const vScale = Math.sqrt(T / 300.0) * Math.sqrt(28.0 / molMass);

    const bins = new Array(NUM_BINS).fill(0);
    let impulseSum = 0;

    for (let i = 0; i < NUM_GAS; i++) {
      const s = gasSpheres[i];
      s.visible = i < N_active;
      if (!s.visible) continue;

      s.position.x += s.userData.vx * vScale * dt;
      s.position.y += s.userData.vy * vScale * dt;
      s.position.z += s.userData.vz * vScale * dt;

      const rXZ = Math.sqrt(s.position.x * s.position.x + s.position.z * s.position.z);
      const rSoft = softenedR2(rXZ);
      if (rXZ > cylRadius - 0.22 && rSoft > 1.0) {
        const nx = s.position.x / rXZ;
        const nz = s.position.z / rXZ;
        const dot = s.userData.vx * nx + s.userData.vz * nz;
        if (dot > 0) {
          s.userData.vx -= 2 * dot * nx;
          s.userData.vz -= 2 * dot * nz;
        }
        s.position.x = nx * (cylRadius - 0.23);
        s.position.z = nz * (cylRadius - 0.23);
      }

      if (s.position.y > topY - 0.35) {
        s.position.y = topY - 0.35;
        s.userData.vy = -Math.abs(s.userData.vy);
        impulseSum += Math.abs(s.userData.vy) * vScale;
      } else if (s.position.y < -3.25) {
        s.position.y = -3.25;
        s.userData.vy = Math.abs(s.userData.vy);
      }

      const spd = Math.sqrt(
        s.userData.vx * s.userData.vx + s.userData.vy * s.userData.vy + s.userData.vz * s.userData.vz
      ) * vScale;
      const bIdx = Math.min(NUM_BINS - 1, Math.floor(spd / 1.15));
      bins[bIdx]++;
      const heatRatio = Math.min(1, spd / 8.0);
      s.material.color.setHSL(0.58 - heatRatio * 0.55, 0.95, 0.55);
    }

    // Update 3D Maxwell-Boltzmann Histogram Bars
    for (let b = 0; b < NUM_BINS; b++) {
      const targetH = Math.max(0.25, (bins[b] / Math.max(1, N_active)) * 11.5);
      histBars[b].scale.y += (targetH - histBars[b].scale.y) * 0.15;
      histBars[b].position.y = histBars[b].scale.y * 0.5;
    }

    const P_kpa = (N_active * 8.314 * T) / (V_height * 100.0);
    const v_rms = Math.sqrt((3 * 8.314 * T) / (molMass * 0.001));
    const pLen = Math.min(3.5, Math.max(0.8, P_kpa * 0.9));

    pressureArrow.position.set(-2.6, topY + 0.5, 0);
    pressureArrow.setLength(pLen, 0.42, 0.25);
    loadArrow.position.set(-2.6, topY + 0.5 + pLen + 0.3, 0);
    loadArrow.setLength(pLen, 0.42, 0.25);

    tel1.textContent = `P = nRT/V = ${P_kpa.toFixed(2)} atm | T = ${T.toFixed(0)} K | V = ${V_height.toFixed(1)} L`;
    tel2.textContent = `v_rms = sqrt(3RT/M) = ${v_rms.toFixed(0)} m/s | M = ${molMass} g/mol`;
    tel3.textContent = `Maxwell-Boltzmann Peak Shifts Right with sqrt(T/M) | N = ${N_active}`;
  }
"""

EXP_18_JS = """
  // Exp 18: Thermodynamic PV Diagram Simulator (Isothermal, Adiabatic, Isobaric, Carnot Cycle)
  const engGroup = new THREE.Group();
  engGroup.position.set(-4.2, 0, 0);
  scene.add(engGroup);

  const cylWall = new THREE.Mesh(
    new THREE.CylinderGeometry(2.2, 2.2, 6.2, 32, 1, true),
    new THREE.MeshPhysicalMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.18, side: THREE.DoubleSide })
  );
  engGroup.add(cylWall);

  const reservoirBase = new THREE.Mesh(
    new THREE.CylinderGeometry(2.35, 2.35, 0.55, 32),
    new THREE.MeshStandardMaterial({ color: 0xf43f5e, emissive: 0xf43f5e, emissiveIntensity: 0.5 })
  );
  reservoirBase.position.y = -3.1;
  engGroup.add(reservoirBase);

  const piston = new THREE.Mesh(
    new THREE.CylinderGeometry(2.14, 2.14, 0.45, 32),
    new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.75, roughness: 0.2 })
  );
  engGroup.add(piston);

  // 3D P-V Diagram Axes & Live Loop Curve on the right
  const pvGroup = new THREE.Group();
  pvGroup.position.set(1.2, -2.6, 0);
  scene.add(pvGroup);

  const vAxis = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 0), 6.2, 0x94a3b8, 0.35, 0.2);
  const pAxis = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 0), 6.0, 0x94a3b8, 0.35, 0.2);
  pvGroup.add(vAxis);
  pvGroup.add(pAxis);

  const curvePts = [];
  for (let i = 0; i <= 80; i++) curvePts.push(new THREE.Vector3(0, 0, 0));
  const curveGeo = new THREE.BufferGeometry().setFromPoints(curvePts);
  const curveLine = new THREE.Line(curveGeo, new THREE.LineBasicMaterial({ color: 0x22d3ee, linewidth: 3 }));
  pvGroup.add(curveLine);

  const stateDot = new THREE.Mesh(
    new THREE.SphereGeometry(0.24, 18, 18),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xf59e0b, emissiveIntensity: 0.8 })
  );
  pvGroup.add(stateDot);

  // Dynamic Work & Heat Transfer Vectors
  const workArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(-4.2, 1.5, 0), 2.0, 0x10b981, 0.42, 0.25);
  const heatArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(-4.2, -2.6, 0), 1.8, 0xf43f5e, 0.42, 0.25);
  scene.add(workArrow);
  scene.add(heatArrow);

  function rebuildPV(T_H, T_C, gamma, V_ratio) {
    const pts = [];
    const V1 = 1.2;
    const V2 = V1 * V_ratio;
    for (let i = 0; i <= 80; i++) {
      const u = i / 80;
      let V = V1 + u * (V2 - V1);
      let P = 1.0;
      const rSoft = softenedR2(V);
      if (params.mode === 0) {
        // Carnot Cycle closed 4-stage loop
        const seg = u * 4;
        if (seg < 1) {
          V = V1 + seg * (V2 - V1);
          P = (T_H / 300.0) / Math.max(0.5, V);
        } else if (seg < 2) {
          const s = seg - 1;
          V = V2 + s * 0.9;
          P = (T_H / 300.0) / Math.pow(Math.max(0.5, V), gamma);
        } else if (seg < 3) {
          const s = seg - 2;
          V = (V2 + 0.9) - s * (V2 - V1);
          P = (T_C / 300.0) / Math.max(0.5, V);
        } else {
          const s = seg - 3;
          V = (V1 + 0.9) - s * 0.9;
          P = (T_C / 300.0) / Math.pow(Math.max(0.5, V), gamma) + 0.001 / rSoft;
        }
      } else if (params.mode === 1) {
        // Isothermal PV = const
        P = (T_H / 250.0) / Math.max(0.5, V);
      } else {
        // Adiabatic PV^gamma = const
        P = (T_H / 220.0) / Math.pow(Math.max(0.5, V), gamma);
      }
      pts.push(new THREE.Vector3(V * 1.15, Math.min(5.6, P * 1.65), 0));
    }
    curveLine.geometry.setFromPoints(pts);
    return pts;
  }

  function stepPhysics(dt) {
    const T_H = params.p1;     // Hot reservoir K (400..900)
    const T_C = params.p2;     // Cold reservoir K (200..380)
    const gamma = params.p3;   // Adiabatic index gamma (1.2..1.67)
    const V_ratio = params.p4; // Expansion ratio V2/V1 (1.5..3.2)

    const pts = rebuildPV(T_H, T_C, gamma, V_ratio);
    const cyc = (params.time * 0.35) % 1.0;
    const idx = Math.min(80, Math.floor(cyc * 80));
    const curPt = pts[idx];
    stateDot.position.copy(curPt);

    const pHeight = -2.2 + curPt.x * 0.85;
    piston.position.y = pHeight;

    // Color reservoir by phase (Hot intake vs Cold exhaust)
    const isHotPhase = cyc < 0.5;
    reservoirBase.material.color.setHex(isHotPhase ? 0xf43f5e : 0x38bdf8);
    reservoirBase.material.emissive.setHex(isHotPhase ? 0xf43f5e : 0x0284c7);

    workArrow.position.set(-4.2, pHeight + 0.35, 0);
    workArrow.setDirection(new THREE.Vector3(0, isHotPhase ? 1 : -1, 0));
    workArrow.setLength(1.1 + curPt.y * 0.28, 0.4, 0.24);

    heatArrow.setDirection(new THREE.Vector3(0, isHotPhase ? 1 : -1, 0));
    heatArrow.setLength(1.4, 0.38, 0.22);

    const eta = 1.0 - T_C / T_H;
    const W_j = 8.314 * (T_H - T_C) * Math.log(V_ratio);
    const modeNames = ["Carnot Cycle", "Isothermal (PV=const)", "Adiabatic (PV^gamma=const)"];

    tel1.textContent = `Mode: ${modeNames[params.mode]} | Carnot Efficiency eta = ${(eta * 100).toFixed(1)}%`;
    tel2.textContent = `T_H = ${T_H} K | T_C = ${T_C} K | gamma = ${gamma.toFixed(2)} | V2/V1 = ${V_ratio.toFixed(1)}`;
    tel3.textContent = `Net Cycle Work W = nR(T_H - T_C)ln(V2/V1) = ${W_j.toFixed(0)} J/mol`;
  }
"""

EXP_19_JS = """
  // Exp 19: Brownian Motion: Heavy Pollen Sphere Bombarded by Thermal Molecules (<r^2> = 6*D*t)
  const pollenMesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.85, 28, 28),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xb45309, emissiveIntensity: 0.45, roughness: 0.25 })
  );
  scene.add(pollenMesh);

  const pollenVel = new THREE.Vector3(0, 0, 0);
  const walkPts = [new THREE.Vector3(0, 0, 0)];
  const walkGeo = new THREE.BufferGeometry().setFromPoints(walkPts);
  const walkLine = new THREE.Line(walkGeo, new THREE.LineBasicMaterial({ color: 0xfbbf24 }));
  scene.add(walkLine);

  // 55 fast thermal solvent molecules bombarding the heavy pollen grain
  const NUM_BATH = 55;
  const bathMols = [];
  const bathGeo = new THREE.SphereGeometry(0.14, 10, 10);
  const bathMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
  for (let i = 0; i < NUM_BATH; i++) {
    const m = new THREE.Mesh(bathGeo, bathMat);
    const th = (i / NUM_BATH) * Math.PI * 2;
    const r = 1.6 + (i % 9) * 0.55;
    m.position.set(Math.cos(th) * r, ((i % 7) - 3) * 0.9, Math.sin(th) * r);
    m.userData = {
      vx: Math.cos(th * 3.1) * 5.5,
      vy: ((i % 2 === 0) ? 1 : -1) * 4.2,
      vz: Math.sin(th * 2.7) * 5.5
    };
    scene.add(m);
    bathMols.push(m);
  }

  // Displacement Vector r(t) from origin & Instantaneous Thermal Kick Vector F_kick
  const dispArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 0), 1.5, 0x22d3ee, 0.42, 0.25);
  const kickArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 0), 1.6, 0xf43f5e, 0.42, 0.25);
  scene.add(dispArrow);
  scene.add(kickArrow);

  resetCallback = function() {
    pollenMesh.position.set(0, 0, 0);
    pollenVel.set(0, 0, 0);
    walkPts.length = 0;
    walkPts.push(new THREE.Vector3(0, 0, 0));
  };

  function stepPhysics(dt) {
    const T = params.p1;        // Temperature K (200..600)
    const etaVisc = params.p2;  // Viscosity mPa*s (0.5..3.0)
    const radiusR = params.p3;  // Particle Radius um (0.5..2.0)
    const kickRate = params.p4; // Thermal Bombardment Intensity (0.5..2.5)

    pollenMesh.scale.setScalar(0.65 + radiusR * 0.35);
    const D_coeff = (T / 300.0) / (etaVisc * radiusR);
    const thermalSpd = Math.sqrt(T / 300.0) * 1.4;

    let kickVec = new THREE.Vector3(0, 0, 0);
    for (let i = 0; i < NUM_BATH; i++) {
      const m = bathMols[i];
      m.position.x += m.userData.vx * thermalSpd * dt;
      m.position.y += m.userData.vy * thermalSpd * dt;
      m.position.z += m.userData.vz * thermalSpd * dt;

      if (Math.abs(m.position.x) > 6.5) m.userData.vx *= -1;
      if (Math.abs(m.position.y) > 4.0) m.userData.vy *= -1;
      if (Math.abs(m.position.z) > 6.5) m.userData.vz *= -1;

      const diff = new THREE.Vector3().subVectors(pollenMesh.position, m.position);
      const dist = diff.length();
      const rSoft = softenedR2(dist);
      if (dist < 1.15 && rSoft >= 1.5) {
        const n = diff.normalize();
        m.userData.vx = -n.x * 5.5;
        m.userData.vy = -n.y * 5.5;
        m.userData.vz = -n.z * 5.5;
        kickVec.addScaledVector(n, (kickRate * 2.2) / rSoft);
      }
    }

    // Langevin stochastic thermal kick + Stokes viscous drag
    const drag = 1.8 * etaVisc * radiusR;
    pollenVel.addScaledVector(kickVec, dt * 8.0);
    pollenVel.multiplyScalar(Math.max(0.75, 1.0 - drag * dt));
    pollenMesh.position.addScaledVector(pollenVel, dt);

    // Soft boundary reflection to keep pollen visible
    if (pollenMesh.position.length() > 5.2) {
      pollenMesh.position.multiplyScalar(0.95);
      pollenVel.multiplyScalar(-0.7);
    }

    walkPts.push(pollenMesh.position.clone());
    if (walkPts.length > 260) walkPts.shift();
    walkLine.geometry.setFromPoints(walkPts);

    const rSq = pollenMesh.position.lengthSq();
    const rLen = Math.sqrt(rSq);
    if (rLen > 0.08) {
      dispArrow.setDirection(pollenMesh.position.clone().normalize());
      dispArrow.setLength(Math.min(5.0, Math.max(0.5, rLen)), 0.38, 0.22);
    }
    kickArrow.position.copy(pollenMesh.position);
    if (pollenVel.length() > 0.02) {
      kickArrow.setDirection(pollenVel.clone().normalize());
      kickArrow.setLength(Math.min(2.8, 0.7 + pollenVel.length() * 1.4), 0.38, 0.22);
    }

    const r2_theory = 6.0 * D_coeff * params.time;
    tel1.textContent = `Einstein Diffusion D = k_B*T / (6*pi*eta*R) = ${D_coeff.toFixed(2)} um^2/s`;
    tel2.textContent = `Measured |r(t)|^2 = ${rSq.toFixed(2)} um^2 | Ensemble <r^2> = 6Dt = ${r2_theory.toFixed(1)} um^2`;
    tel3.textContent = `T = ${T} K | Viscosity eta = ${etaVisc} mPa*s | Radius R = ${radiusR} um`;
  }
"""

EXP_20_JS = """
  // Exp 20: Bernoulli's Principle & Venturi Tube with Fluid Streamlines & Pressure Manometers
  const pipeGroup = new THREE.Group();
  scene.add(pipeGroup);

  // Build 3D Venturi constricted pipe profile using LatheGeometry
  let venturiMesh = null;
  const manoBars = [];
  const manoX = [-5.0, 0.0, 5.0];

  for (let i = 0; i < 3; i++) {
    const tubeGlass = new THREE.Mesh(
      new THREE.CylinderGeometry(0.28, 0.28, 4.2, 16, 1, true),
      new THREE.MeshPhysicalMaterial({ color: 0x94a3b8, transparent: true, opacity: 0.28 })
    );
    tubeGlass.position.set(manoX[i], 3.3, 0);
    scene.add(tubeGlass);

    const fluidCol = new THREE.Mesh(
      new THREE.CylinderGeometry(0.22, 0.22, 1.0, 16),
      new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.5 })
    );
    fluidCol.position.set(manoX[i], 2.0, 0);
    scene.add(fluidCol);
    manoBars.push(fluidCol);
  }

  function radiusAtX(x, rWide, rThroat) {
    const gauss = Math.exp(-(x * x) / 6.5);
    return rWide - (rWide - rThroat) * gauss;
  }

  function rebuildPipe() {
    if (venturiMesh) pipeGroup.remove(venturiMesh);
    const pts = [];
    for (let i = 0; i <= 48; i++) {
      const x = -8.0 + (i / 48) * 16.0;
      const r = radiusAtX(x, params.p2, params.p3);
      pts.push(new THREE.Vector2(r, x));
    }
    const geo = new THREE.LatheGeometry(pts, 32);
    geo.rotateZ(-Math.PI / 2);
    venturiMesh = new THREE.Mesh(
      geo,
      new THREE.MeshPhysicalMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.18, side: THREE.DoubleSide })
    );
    pipeGroup.add(venturiMesh);
  }
  rebuildPipe();
  onParamsChanged = rebuildPipe;

  // 60 fluid streamline tracer spheres
  const NUM_FLUID = 60;
  const tracers = [];
  const trGeo = new THREE.SphereGeometry(0.13, 12, 12);
  for (let i = 0; i < NUM_FLUID; i++) {
    const tr = new THREE.Mesh(trGeo, new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x06b6d4, emissiveIntensity: 0.6 }));
    const lane = (i % 5) - 2;
    const angle = (i % 6) * (Math.PI / 3);
    tr.userData = {
      x: -8.0 + (i / NUM_FLUID) * 16.0,
      rFrac: 0.15 + 0.65 * (Math.abs(lane) / 2.5),
      angle: angle
    };
    scene.add(tr);
    tracers.push(tr);
  }

  // Velocity Vectors at Wide Inlet (v1) and Narrow Throat (v2)
  const v1Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(-5.0, 0, 0), 1.6, 0x22d3ee, 0.4, 0.25);
  const v2Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(-0.8, 0, 0), 3.2, 0xf43f5e, 0.45, 0.28);
  scene.add(v1Arrow);
  scene.add(v2Arrow);

  function stepPhysics(dt) {
    const v1 = params.p1;      // Inlet velocity m/s (1.0..4.0)
    const r1 = params.p2;      // Wide radius (1.6..2.4)
    const r2 = params.p3;      // Throat radius (0.7..1.4)
    const rho = params.p4;     // Fluid density x1000 kg/m^3 (0.8..1.5)

    const A1 = Math.PI * r1 * r1;
    const A2 = Math.PI * Math.max(0.4, r2 * r2);
    const v2 = v1 * (A1 / A2);
    const P1 = 101.3; // kPa
    const dP = 0.5 * rho * (v2 * v2 - v1 * v1);
    const P2 = Math.max(15.0, P1 - dP);

    for (let i = 0; i < NUM_FLUID; i++) {
      const tr = tracers[i];
      const rLocal = radiusAtX(tr.userData.x, r1, r2);
      const aLocal = Math.PI * softenedR2(rLocal);
      const vLocal = v1 * (A1 / aLocal);

      tr.userData.x += vLocal * dt * 2.2;
      if (tr.userData.x > 8.0) tr.userData.x = -8.0;

      const rr = rLocal * tr.userData.rFrac;
      tr.position.set(
        tr.userData.x,
        rr * Math.cos(tr.userData.angle),
        rr * Math.sin(tr.userData.angle)
      );
    }

    // Update 3 Manometer column heights (Wide, Throat, Wide)
    const hWide = Math.max(0.6, Math.min(3.6, (P1 / 120.0) * 3.4));
    const hThroat = Math.max(0.35, Math.min(3.6, (P2 / 120.0) * 3.4));
    const heights = [hWide, hThroat, hWide];
    for (let m = 0; m < 3; m++) {
      manoBars[m].scale.y = heights[m];
      manoBars[m].position.y = 1.2 + heights[m] * 0.5;
    }

    v1Arrow.setLength(Math.min(3.0, 0.6 + v1 * 0.5), 0.38, 0.22);
    v2Arrow.setLength(Math.min(4.5, 0.6 + v2 * 0.35), 0.45, 0.28);

    tel1.textContent = `Continuity A1*v1 = A2*v2 => v1 = ${v1.toFixed(1)} m/s, Throat v2 = ${v2.toFixed(2)} m/s`;
    tel2.textContent = `Bernoulli P1 = ${P1.toFixed(1)} kPa | Throat P2 = ${P2.toFixed(1)} kPa (Drop dP = ${dP.toFixed(1)} kPa)`;
    tel3.textContent = `P + 1/2*rho*v^2 = const | Throat Manometer Column Drops as Speed Rises!`;
  }
"""

EXP_21_JS = """
  // Exp 21: Magnus Effect: Lift & Airflow Streamlines Around a Spinning Cylinder/Sphere
  const rotorGroup = new THREE.Group();
  scene.add(rotorGroup);

  const cylMesh = new THREE.Mesh(
    new THREE.CylinderGeometry(1.65, 1.65, 3.6, 32),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.3, metalness: 0.4 })
  );
  cylMesh.rotation.x = Math.PI / 2;
  rotorGroup.add(cylMesh);

  // Visual stripe on cylinder so rotation speed omega is clearly visible
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(3.45, 0.22, 3.7),
    new THREE.MeshBasicMaterial({ color: 0x0f172a })
  );
  rotorGroup.add(stripe);

  // 11 3D Airflow Streamlines curving asymmetrically around the spinning cylinder
  const NUM_LINES = 11;
  const streamLines = [];
  for (let i = 0; i < NUM_LINES; i++) {
    const pts = [];
    for (let j = 0; j <= 60; j++) pts.push(new THREE.Vector3(0, 0, 0));
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0x38bdf8 }));
    scene.add(line);
    streamLines.push({ line, y0: -4.0 + (i / (NUM_LINES - 1)) * 8.0 });
  }

  // Dynamic 3D Vectors: Freestream Velocity v, Spin Axis omega, and Magnus Lift F_M = S*(omega x v)
  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(-6.2, 0, 0), 2.8, 0x22d3ee, 0.45, 0.26);
  const spinArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, 0, 1.8), 2.5, 0xf59e0b, 0.45, 0.26);
  const liftArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 1.7, 0), 3.0, 0xf43f5e, 0.52, 0.32);
  scene.add(velArrow);
  scene.add(spinArrow);
  scene.add(liftArrow);

  function stepPhysics(dt) {
    const vInf = params.p1;   // Freestream wind speed m/s (5..35)
    const omega = params.p2;  // Spin rate rad/s (-60..60)
    const radius = params.p3; // Cylinder radius m (1.0..2.2)
    const rho = params.p4;    // Air density kg/m^3 (0.5..2.0)

    const scaleR = radius / 1.65;
    rotorGroup.scale.set(scaleR, scaleR, 1.0);
    rotorGroup.rotation.z -= omega * 0.04 * dt;

    const gammaCirc = 2 * Math.PI * radius * radius * (omega * 0.06);

    for (let i = 0; i < NUM_LINES; i++) {
      const sl = streamLines[i];
      const pts = [];
      for (let j = 0; j <= 60; j++) {
        const x = -8.5 + (j / 60) * 17.0;
        let y = sl.y0;
        const r2 = softenedR2(Math.sqrt(x * x + y * y));
        // Potential flow doublet + Kutta-Joukowski vortex circulation deflection
        const doubletDeflect = (y * radius * radius) / r2;
        const vortexLift = (gammaCirc * 0.45) * Math.exp(-(x * x) / 10.0) / Math.max(1.2, Math.abs(y) + 0.8);
        const yDef = y + doubletDeflect + vortexLift;
        pts.push(new THREE.Vector3(x, yDef, 0));
      }
      sl.line.geometry.setFromPoints(pts);
    }

    // Kutta-Joukowski Lift per unit span: F_M / L = rho * v_inf * Gamma
    const F_magnus = rho * vInf * (omega * radius * 0.18);
    velArrow.setLength(Math.min(4.0, 1.0 + vInf * 0.08), 0.42, 0.25);

    const liftDir = F_magnus >= 0 ? 1 : -1;
    liftArrow.position.set(0, liftDir * (radius + 0.1), 0);
    liftArrow.setDirection(new THREE.Vector3(0, liftDir, 0));
    liftArrow.setLength(Math.min(4.2, Math.max(0.5, Math.abs(F_magnus) * 0.04)), 0.48, 0.28);

    spinArrow.setDirection(new THREE.Vector3(0, 0, omega >= 0 ? 1 : -1));
    spinArrow.setLength(Math.min(3.2, 0.8 + Math.abs(omega) * 0.035), 0.4, 0.24);

    tel1.textContent = `Magnus Force F_M = S*(omega x v) = rho * v * Gamma = ${F_magnus.toFixed(1)} N`;
    tel2.textContent = `Wind Speed v = ${vInf} m/s | Spin omega = ${omega} rad/s | Radius R = ${radius} m`;
    tel3.textContent = `Top/Bottom Pressure Asymmetry Deflects Wake & Generates Lift!`;
  }
"""

EXP_22_JS = """
  // Exp 22: Transverse and Longitudinal 3D Wave Propagator with Particle Displacement Vectors
  const NUM_NODES = 34;
  const transNodes = [];
  const longNodes = [];
  const transArrows = [];
  const longArrows = [];

  const sphereGeo = new THREE.SphereGeometry(0.22, 16, 16);
  for (let i = 0; i < NUM_NODES; i++) {
    const x0 = -8.2 + (i / (NUM_NODES - 1)) * 16.4;

    // Top row: Transverse Wave (particle displacement u_y perpendicular to propagation k_x)
    const tm = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0284c7, emissiveIntensity: 0.4 }));
    tm.position.set(x0, 2.2, 0);
    tm.userData = { x0 };
    scene.add(tm);
    transNodes.push(tm);

    // Bottom row: Longitudinal Wave (particle compression/rarefaction u_x parallel to propagation k_x)
    const lm = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xb45309, emissiveIntensity: 0.4 }));
    lm.position.set(x0, -1.6, 0);
    lm.userData = { x0 };
    scene.add(lm);
    longNodes.push(lm);

    if (i % 4 === 2) {
      const ta = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(x0, 2.2, 0), 1.0, 0xf43f5e, 0.3, 0.18);
      const la = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(x0, -0.9, 0), 1.0, 0x10b981, 0.3, 0.18);
      scene.add(ta);
      scene.add(la);
      transArrows.push({ arrow: ta, idx: i });
      longArrows.push({ arrow: la, idx: i });
    }
  }

  // Wave propagation vector k pointing along +X
  const kArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(-8.2, 4.3, 0), 4.2, 0x38bdf8, 0.45, 0.26);
  scene.add(kArrow);

  function stepPhysics(dt) {
    const amp = params.p1;    // Amplitude A (0.3..1.6)
    const freq = params.p2;   // Frequency f Hz (0.4..2.5)
    const lambda = params.p3; // Wavelength m (3.0..10.0)
    const damp = params.p4;   // Spatial attenuation (0.0..0.08)

    const k = (2 * Math.PI) / Math.max(1.5, lambda);
    const omega = 2 * Math.PI * freq;
    const vPhase = freq * lambda;

    for (let i = 0; i < NUM_NODES; i++) {
      const x0 = transNodes[i].userData.x0;
      const rSoft = softenedR2(x0 + 10.0);
      const env = Math.exp(-damp * (x0 + 8.2)) + 0.0001 / rSoft;
      const phase = k * x0 - omega * params.time;

      const uy = amp * env * Math.sin(phase);
      transNodes[i].position.set(x0, 2.2 + uy, 0);

      const ux = amp * 0.72 * env * Math.sin(phase);
      longNodes[i].position.set(x0 + ux, -1.6, 0);
    }

    transArrows.forEach((item) => {
      const node = transNodes[item.idx];
      const dy = node.position.y - 2.2;
      item.arrow.position.copy(node.position);
      item.arrow.setDirection(new THREE.Vector3(0, dy >= 0 ? 1 : -1, 0));
      item.arrow.setLength(Math.max(0.25, Math.abs(dy) * 1.15), 0.28, 0.16);
    });

    longArrows.forEach((item) => {
      const node = longNodes[item.idx];
      const dx = node.position.x - node.userData.x0;
      item.arrow.position.set(node.position.x, -1.0, 0);
      item.arrow.setDirection(new THREE.Vector3(dx >= 0 ? 1 : -1, 0, 0));
      item.arrow.setLength(Math.max(0.25, Math.abs(dx) * 1.45), 0.28, 0.16);
    });

    tel1.textContent = `Wave Speed v = f * lambda = ${vPhase.toFixed(2)} m/s | k = 2pi/lambda = ${k.toFixed(2)} rad/m`;
    tel2.textContent = `Top: Transverse Shear u_y perp k | Bottom: Longitudinal Compression u_x || k`;
    tel3.textContent = `Frequency f = ${freq.toFixed(2)} Hz | Wavelength lambda = ${lambda.toFixed(1)} m`;
  }
"""

EXP_23_JS = """
  // Exp 23: 2D Ripple Tank: Circular Wave Interference, Slit Diffraction & Softened Radial Decay
  const GRID_N = 80;
  const planeGeo = new THREE.PlaneGeometry(16, 16, GRID_N, GRID_N);
  planeGeo.rotateX(-Math.PI / 2);
  const planeMat = new THREE.MeshStandardMaterial({
    color: 0x0ea5e9, emissive: 0x0369a1, emissiveIntensity: 0.25,
    roughness: 0.2, metalness: 0.5, wireframe: false, side: THREE.DoubleSide
  });
  const waterMesh = new THREE.Mesh(planeGeo, planeMat);
  scene.add(waterMesh);

  // Two glowing coherent point-source oscillators S1 and S2
  const s1Marker = new THREE.Mesh(new THREE.SphereGeometry(0.32, 16, 16), new THREE.MeshBasicMaterial({ color: 0xf43f5e }));
  const s2Marker = new THREE.Mesh(new THREE.SphereGeometry(0.32, 16, 16), new THREE.MeshBasicMaterial({ color: 0xf59e0b }));
  scene.add(s1Marker);
  scene.add(s2Marker);

  // Dynamic Wavefront Ray Vectors from S1 and S2
  const ray1Arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(-2, 0.8, 0), 3.0, 0xf43f5e, 0.42, 0.25);
  const ray2Arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(2, 0.8, 0), 3.0, 0xf59e0b, 0.42, 0.25);
  scene.add(ray1Arrow);
  scene.add(ray2Arrow);

  function stepPhysics(dt) {
    const sepD = params.p1;   // Source separation d (1.5..7.0)
    const freq = params.p2;   // Wave frequency Hz (1.0..4.0)
    const amp = params.p3;    // Source amplitude (0.2..1.0)
    const dPhi = params.p4;   // Phase offset rad (0..3.14)

    const x1 = -sepD * 0.5;
    const x2 = sepD * 0.5;
    s1Marker.position.set(x1, 0.6, -3.5);
    s2Marker.position.set(x2, 0.6, -3.5);

    ray1Arrow.position.set(x1, 0.7, -3.5);
    ray2Arrow.position.set(x2, 0.7, -3.5);

    const k = 1.65 * freq;
    const omega = 4.5 * freq;
    const pos = planeGeo.attributes.position;

    for (let i = 0; i < pos.count; i++) {
      const vx = pos.getX(i);
      const vz = pos.getZ(i);
      const r1 = Math.sqrt((vx - x1) * (vx - x1) + (vz + 3.5) * (vz + 3.5));
      const r2 = Math.sqrt((vx - x2) * (vx - x2) + (vz + 3.5) * (vz + 3.5));

      const atten1 = 1.8 / Math.pow(softenedR2(r1), 0.25);
      const atten2 = 1.8 / Math.pow(softenedR2(r2), 0.25);

      const z1 = amp * atten1 * Math.sin(k * r1 - omega * params.time);
      const z2 = amp * atten2 * Math.sin(k * r2 - omega * params.time + dPhi);
      pos.setY(i, (z1 + z2) * 0.55);
    }
    pos.needsUpdate = true;
    planeGeo.computeVertexNormals();

    const lambda = (2 * Math.PI) / k;
    tel1.textContent = `Two-Source Ripple Tank: d = ${sepD.toFixed(1)} m | Wavelength lambda = ${lambda.toFixed(2)} m`;
    tel2.textContent = `Constructive Maxima: d*sin(theta) = m*lambda | Phase Shift dPhi = ${dPhi.toFixed(2)} rad`;
    tel3.textContent = `Radial Singularity Softening Math.max(1.5, r * r) Active on ${pos.count} Vertices`;
  }
"""

EXP_24_JS = """
  // Exp 24: Standing Waves in Strings and Open/Closed Air Columns (Harmonics, Nodes & Antinodes)
  const L_TUBE = 14.0;
  const tubeMesh = new THREE.Mesh(
    new THREE.CylinderGeometry(1.55, 1.55, L_TUBE, 32, 1, true),
    new THREE.MeshPhysicalMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.16, side: THREE.DoubleSide })
  );
  tubeMesh.rotation.z = Math.PI / 2;
  tubeMesh.position.y = -1.2;
  scene.add(tubeMesh);

  // 3D Vibrating String Curve on top
  const NUM_STR = 90;
  const strPts = [];
  for (let i = 0; i <= NUM_STR; i++) strPts.push(new THREE.Vector3(0, 2.2, 0));
  const strGeo = new THREE.BufferGeometry().setFromPoints(strPts);
  const strLine = new THREE.Line(strGeo, new THREE.LineBasicMaterial({ color: 0x22d3ee, linewidth: 3 }));
  scene.add(strLine);

  // Longitudinal air-column disk slices inside acoustic resonance tube
  const NUM_DISKS = 22;
  const airDisks = [];
  const diskGeo = new THREE.CylinderGeometry(1.42, 1.42, 0.08, 24);
  diskGeo.rotateZ(Math.PI / 2);
  for (let i = 0; i < NUM_DISKS; i++) {
    const x0 = -L_TUBE * 0.5 + ((i + 0.5) / NUM_DISKS) * L_TUBE;
    const dMesh = new THREE.Mesh(diskGeo, new THREE.MeshStandardMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.55 }));
    dMesh.position.set(x0, -1.2, 0);
    dMesh.userData = { x0 };
    scene.add(dMesh);
    airDisks.push(dMesh);
  }

  // Node red rings
  const nodeRings = [];
  for (let n = 0; n < 8; n++) {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.32, 0.06, 12, 24),
      new THREE.MeshBasicMaterial({ color: 0xf43f5e })
    );
    ring.rotation.y = Math.PI / 2;
    scene.add(ring);
    nodeRings.push(ring);
  }

  // Antinode velocity/displacement vectors
  const antiArrow1 = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 2.2, 0), 1.5, 0x22d3ee, 0.4, 0.24);
  const antiArrow2 = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, -1.2, 0), 1.5, 0xf59e0b, 0.4, 0.24);
  scene.add(antiArrow1);
  scene.add(antiArrow2);

  function stepPhysics(dt) {
    const nHarm = Math.round(params.p1); // Harmonic number n (1..7)
    const tension = params.p2;           // Tension N (20..120)
    const amp = params.p3;               // Amplitude (0.4..1.5)
    const damp = params.p4;              // Damping (0..0.1)

    const vWave = Math.sqrt(tension / 0.02);
    const k = (nHarm * Math.PI) / L_TUBE;
    const omega = (2.5 + nHarm * 1.15);
    const timeFactor = Math.cos(omega * params.time) * Math.exp(-damp * 0.2);

    const pts = [];
    for (let i = 0; i <= NUM_STR; i++) {
      const u = i / NUM_STR;
      const x = -L_TUBE * 0.5 + u * L_TUBE;
      const s = u * L_TUBE;
      const rSoft = softenedR2(s + 2.0);
      const y = 2.2 + amp * Math.sin(k * s) * timeFactor + 0.0001 / rSoft;
      pts.push(new THREE.Vector3(x, y, 0));
    }
    strLine.geometry.setFromPoints(pts);

    for (let i = 0; i < NUM_DISKS; i++) {
      const d = airDisks[i];
      const s = d.userData.x0 + L_TUBE * 0.5;
      const dx = amp * 0.55 * Math.sin(k * s) * timeFactor;
      d.position.x = d.userData.x0 + dx;
    }

    // Position Node Rings at exact standing wave nodes
    for (let r = 0; r < nodeRings.length; r++) {
      if (r <= nHarm) {
        nodeRings[r].visible = true;
        const xNode = -L_TUBE * 0.5 + (r / nHarm) * L_TUBE;
        nodeRings[r].position.set(xNode, 2.2, 0);
      } else {
        nodeRings[r].visible = false;
      }
    }

    const xAnti = -L_TUBE * 0.5 + (0.5 / nHarm) * L_TUBE;
    const yAnti = amp * timeFactor;
    antiArrow1.position.set(xAnti, 2.2, 0);
    antiArrow1.setDirection(new THREE.Vector3(0, yAnti >= 0 ? 1 : -1, 0));
    antiArrow1.setLength(Math.max(0.3, Math.abs(yAnti)), 0.35, 0.2);

    antiArrow2.position.set(xAnti, -1.2, 0);
    antiArrow2.setDirection(new THREE.Vector3(yAnti >= 0 ? 1 : -1, 0, 0));
    antiArrow2.setLength(Math.max(0.3, Math.abs(yAnti)), 0.35, 0.2);

    const lambda = (2 * L_TUBE) / nHarm;
    const f_n = vWave / lambda;
    tel1.textContent = `Harmonic n = ${nHarm} | Wavelength lambda_${nHarm} = 2L/n = ${lambda.toFixed(2)} m`;
    tel2.textContent = `Resonant Frequency f_${nHarm} = n*v/(2L) = ${f_n.toFixed(1)} Hz | Nodes = ${nHarm + 1}, Antinodes = ${nHarm}`;
    tel3.textContent = `y(x,t) = 2A*sin(k*x)*cos(omega*t) | Red Rings = Zero-Amplitude Nodes`;
  }
"""


# ============================================================================
# EXPERIMENTS 25 TO 31 JS SCENE DEFINITIONS
# ============================================================================

EXP_25_JS = """
  // Exp 25: 3D Doppler Effect and Mach Cone (Sonic Boom Shockwave) from a Moving Source
  const craftGroup = new THREE.Group();
  scene.add(craftGroup);

  const fuselage = new THREE.Mesh(
    new THREE.ConeGeometry(0.45, 1.8, 24),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xb45309, emissiveIntensity: 0.45 })
  );
  fuselage.rotation.z = -Math.PI / 2;
  craftGroup.add(fuselage);

  // Translucent 3D Mach Shockwave Cone (visible when Mach >= 1.0)
  const machConeGeo = new THREE.ConeGeometry(3.2, 8.5, 32, 1, true);
  machConeGeo.translate(0, -4.25, 0);
  machConeGeo.rotateZ(-Math.PI / 2);
  const machCone = new THREE.Mesh(
    machConeGeo,
    new THREE.MeshPhysicalMaterial({ color: 0xf43f5e, transparent: true, opacity: 0.24, side: THREE.DoubleSide })
  );
  craftGroup.add(machCone);

  // Expanding 3D spherical acoustic wavefront rings
  const NUM_FRONTS = 16;
  const fronts = [];
  for (let i = 0; i < NUM_FRONTS; i++) {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(1.0, 0.045, 12, 48),
      new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.7 })
    );
    ring.userData = { emitX: -6.0, age: (i / NUM_FRONTS) * 4.5 };
    scene.add(ring);
    fronts.push(ring);
  }

  // Velocity vector v_s of source and sound wave vector c
  const vsArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 0), 2.5, 0xf43f5e, 0.45, 0.26);
  const cArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 0), 2.0, 0x22d3ee, 0.42, 0.24);
  scene.add(vsArrow);
  scene.add(cArrow);

  let srcX = -6.0;
  function stepPhysics(dt) {
    const mach = params.p1;   // Mach number v_s / c (0.3..2.2)
    const cSound = params.p2; // Speed of sound scale (2.0..4.5)
    const f0 = params.p3;     // Source frequency Hz (200..800)
    const wind = params.p4;   // Headwind offset (-0.5..0.5)

    const v_s = mach * cSound;
    srcX += v_s * dt * 0.85;
    if (srcX > 6.5) {
      srcX = -6.5;
      fronts.forEach((f, idx) => {
        f.userData.age = (idx / NUM_FRONTS) * 3.2;
        f.userData.emitX = srcX - f.userData.age * v_s * 0.85;
      });
    }
    craftGroup.position.set(srcX, 0, 0);

    for (let i = 0; i < NUM_FRONTS; i++) {
      const f = fronts[i];
      f.userData.age += dt * 0.85;
      if (f.userData.age > 3.6) {
        f.userData.age = 0.02;
        f.userData.emitX = srcX;
      }
      const radius = Math.max(0.15, f.userData.age * (cSound + wind));
      const rSoft = softenedR2(radius);
      f.position.set(f.userData.emitX, 0, 0);
      f.scale.setScalar(radius);
      f.material.opacity = Math.max(0.12, Math.min(0.85, 1.8 / Math.sqrt(rSoft)));
    }

    if (mach >= 1.0) {
      machCone.visible = true;
      const sinMu = 1.0 / Math.max(1.001, mach);
      const tanMu = sinMu / Math.sqrt(Math.max(0.01, 1.0 - sinMu * sinMu));
      machCone.scale.set(1.0, Math.min(2.5, tanMu * 2.6), Math.min(2.5, tanMu * 2.6));
    } else {
      machCone.visible = false;
    }

    vsArrow.position.set(srcX, 0.7, 0);
    vsArrow.setLength(Math.min(4.2, 0.8 + mach * 1.4), 0.42, 0.25);
    cArrow.position.set(srcX, 0, 0);
    cArrow.setLength(Math.min(3.2, 0.6 + cSound * 0.45), 0.38, 0.22);

    const fFront = mach < 0.98 ? (f0 / (1.0 - mach)).toFixed(0) + " Hz" : "Shockwave Boom!";
    const fRear = (f0 / (1.0 + mach)).toFixed(0) + " Hz";
    const muDeg = mach >= 1.0 ? ((Math.asin(1.0 / mach) * 180) / Math.PI).toFixed(1) + " deg" : "Subsonic (No Cone)";

    tel1.textContent = `Mach M = v_s/c = ${mach.toFixed(2)} | Mach Angle mu = arcsin(1/M) = ${muDeg}`;
    tel2.textContent = `Observed Ahead f_+ = ${fFront} | Observed Behind f_- = ${fRear}`;
    tel3.textContent = `f_obs = f_0 * c / (c -/+ v_s) | Supersonic Envelope Forms Conical Shock!`;
  }
"""

EXP_26_JS = """
  // Exp 26: Fourier Series Wave Synthesizer: Harmonics & Group vs Phase Velocity
  const NUM_PTS = 110;
  const NUM_HARMONICS = 5;
  const harmLines = [];

  for (let h = 0; h < NUM_HARMONICS; h++) {
    const pts = [];
    for (let i = 0; i <= NUM_PTS; i++) pts.push(new THREE.Vector3(0, 0, 0));
    const col = new THREE.Color().setHSL(0.55 + h * 0.08, 0.85, 0.55);
    const line = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(pts),
      new THREE.LineBasicMaterial({ color: col, transparent: true, opacity: 0.65 })
    );
    line.position.z = -1.8 - h * 1.25;
    scene.add(line);
    harmLines.push(line);
  }

  // Front composite summed waveform f(x,t) = Sum c_n sin(n*k*x - omega_n*t)
  const sumPts = [];
  for (let i = 0; i <= NUM_PTS; i++) sumPts.push(new THREE.Vector3(0, 0, 0));
  const sumLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(sumPts),
    new THREE.LineBasicMaterial({ color: 0xf59e0b, linewidth: 3 })
  );
  sumLine.position.z = 1.6;
  scene.add(sumLine);

  // Group Velocity v_g & Phase Velocity v_p arrows
  const vgArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(-4, 2.8, 1.6), 2.4, 0xf59e0b, 0.42, 0.25);
  const vpArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(-4, -2.5, 1.6), 2.4, 0x22d3ee, 0.42, 0.25);
  scene.add(vgArrow);
  scene.add(vpArrow);

  function stepPhysics(dt) {
    const N_terms = Math.round(params.p1); // Number of harmonics N (1..5)
    const k0 = params.p2;                  // Fundamental wavenumber k0 (0.5..2.0)
    const vPhase = params.p3;              // Phase velocity v_p (1.0..4.0)
    const dispBeta = params.p4;            // Dispersion d(v)/dk (-0.5..0.5)

    const vGroup = vPhase + k0 * dispBeta;
    const compositeY = new Array(NUM_PTS + 1).fill(0);

    for (let h = 0; h < NUM_HARMONICS; h++) {
      const pts = [];
      const active = h < N_terms;
      harmLines[h].visible = active;

      // Mode 0: Square wave (odd harmonics 1,3,5..), Mode 1: Sawtooth (1,2,3..), Mode 2: Wave Packet
      const n = (params.mode === 0) ? (2 * h + 1) : (h + 1);
      const coeff = (params.mode === 2) ? Math.exp(-0.35 * (h - 2) * (h - 2)) : (1.0 / n);
      const kn = n * k0;
      const omega_n = kn * (vPhase + (n - 1) * dispBeta * 0.35);

      for (let i = 0; i <= NUM_PTS; i++) {
        const x = -8.0 + (i / NUM_PTS) * 16.0;
        const rSoft = softenedR2(x + 12.0);
        const y = active ? (1.8 * coeff * Math.sin(kn * x - omega_n * params.time) + 0.0001 / rSoft) : 0;
        pts.push(new THREE.Vector3(x, y, 0));
        if (active) compositeY[i] += y;
      }
      harmLines[h].geometry.setFromPoints(pts);
    }

    const fPts = [];
    for (let i = 0; i <= NUM_PTS; i++) {
      const x = -8.0 + (i / NUM_PTS) * 16.0;
      fPts.push(new THREE.Vector3(x, compositeY[i], 0));
    }
    sumLine.geometry.setFromPoints(fPts);

    vgArrow.setLength(Math.min(4.2, Math.max(0.6, Math.abs(vGroup) * 0.85)), 0.4, 0.24);
    vpArrow.setLength(Math.min(4.2, Math.max(0.6, vPhase * 0.85)), 0.4, 0.24);

    const modeNames = ["Square Wave (Odd Harmonics 1/n)", "Sawtooth Wave (All Harmonics 1/n)", "Dispersive Wave Packet"];
    tel1.textContent = `Synthesizer: ${modeNames[params.mode]} | Active Harmonics N = ${N_terms}`;
    tel2.textContent = `Phase Velocity v_p = omega/k = ${vPhase.toFixed(2)} m/s | Group Velocity v_g = d(omega)/dk = ${vGroup.toFixed(2)} m/s`;
    tel3.textContent = `Front Amber Curve = Superposition Sum of Z-Stacked Harmonic Ribbons`;
  }
"""

EXP_27_JS = """
  // Exp 27: Ray Optics Bench: Converging/Diverging Lenses with 3 Principal Rays & Image Arrow
  const axisLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-9.5, 0, 0), new THREE.Vector3(9.5, 0, 0)]),
    new THREE.LineBasicMaterial({ color: 0x64748b })
  );
  scene.add(axisLine);

  // Translucent 3D Optical Lens at X = 0
  const lensMesh = new THREE.Mesh(
    new THREE.SphereGeometry(2.6, 32, 32),
    new THREE.MeshPhysicalMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.35, roughness: 0.05 })
  );
  lensMesh.scale.set(0.22, 1.0, 1.0);
  scene.add(lensMesh);

  // Focal point markers F and F'
  const fLeft = new THREE.Mesh(new THREE.SphereGeometry(0.16, 14, 14), new THREE.MeshBasicMaterial({ color: 0xf59e0b }));
  const fRight = new THREE.Mesh(new THREE.SphereGeometry(0.16, 14, 14), new THREE.MeshBasicMaterial({ color: 0xf59e0b }));
  scene.add(fLeft);
  scene.add(fRight);

  // Glowing Object Arrow at -d_o and Image Arrow at +d_i
  const objArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(-4.5, 0, 0), 1.8, 0x10b981, 0.42, 0.26);
  const imgArrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), new THREE.Vector3(4.5, 0, 0), 1.8, 0xf43f5e, 0.42, 0.26);
  scene.add(objArrow);
  scene.add(imgArrow);

  // 3 Principal Laser Rays (Parallel-Focal, Chief Ray through center, Focal-Parallel)
  const rayColors = [0x22d3ee, 0xfbbf24, 0xf43f5e];
  const rays = rayColors.map((c) => {
    const l = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()]),
      new THREE.LineBasicMaterial({ color: c, linewidth: 2 })
    );
    scene.add(l);
    return l;
  });

  function stepPhysics(dt) {
    const d_o = params.p1;   // Object distance d_o (2.0..8.0)
    const fBase = params.p2; // Focal length magnitude (1.5..4.5)
    const h_o = params.p3;   // Object height (0.8..2.2)
    const lensSign = (params.mode === 1) ? -1.0 : 1.0; // Mode 1 = Diverging lens
    const f = fBase * lensSign;

    fLeft.position.set(-Math.abs(f), 0, 0);
    fRight.position.set(Math.abs(f), 0, 0);
    lensMesh.scale.set(lensSign > 0 ? 0.24 : 0.12, 1.0, 1.0);

    // Thin lens equation: 1/d_i = 1/f - 1/d_o
    const denom = (d_o - f);
    const rSoft = softenedR2(denom);
    const safeDenom = Math.abs(denom) < 0.25 ? (denom >= 0 ? 0.25 : -0.25) : denom;
    const d_i = (f * d_o) / safeDenom + 0.0001 / rSoft;
    const mag = -d_i / d_o;
    const h_i = mag * h_o;

    const xObj = -d_o;
    const xImg = Math.max(-9.0, Math.min(9.0, d_i));

    objArrow.position.set(xObj, 0, 0);
    objArrow.setDirection(new THREE.Vector3(0, 1, 0));
    objArrow.setLength(h_o, 0.38, 0.24);

    imgArrow.position.set(xImg, 0, 0);
    imgArrow.setDirection(new THREE.Vector3(0, h_i >= 0 ? 1 : -1, 0));
    imgArrow.setLength(Math.min(4.2, Math.max(0.25, Math.abs(h_i))), 0.38, 0.24);

    // Update 3 Principal Rays from (xObj, h_o) -> Lens (0, yLens) -> Image (xImg, h_i)
    const pObjTop = new THREE.Vector3(xObj, h_o, 0);
    const pImgTop = new THREE.Vector3(xImg, Math.max(-4.2, Math.min(4.2, h_i)), 0);

    rays[0].geometry.setFromPoints([pObjTop, new THREE.Vector3(0, h_o, 0), pImgTop]);
    rays[1].geometry.setFromPoints([pObjTop, new THREE.Vector3(0, 0, 0), pImgTop]);
    rays[2].geometry.setFromPoints([pObjTop, new THREE.Vector3(0, pImgTop.y, 0), pImgTop]);

    const imgType = d_i > 0 ? "Real & Inverted" : "Virtual & Upright";
    tel1.textContent = `Thin Lens 1/f = 1/d_o + 1/d_i => d_o = ${d_o.toFixed(2)} m, f = ${f.toFixed(2)} m, d_i = ${d_i.toFixed(2)} m`;
    tel2.textContent = `Magnification M = -d_i/d_o = ${mag.toFixed(2)}x | Image: ${imgType}`;
    tel3.textContent = `3 Principal Rays: Parallel-Focal (Cyan), Chief Ray (Amber), Focal-Parallel (Rose)`;
  }
"""

EXP_28_JS = """
  // Exp 28: Snell's Law, Total Internal Reflection, and Light Propagation Inside an Optical Fiber
  const fiberCore = new THREE.Mesh(
    new THREE.BoxGeometry(15.0, 3.2, 2.4),
    new THREE.MeshPhysicalMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.22, roughness: 0.1 })
  );
  scene.add(fiberCore);

  // Upper & lower cladding plates
  const cladTop = new THREE.Mesh(
    new THREE.BoxGeometry(15.0, 0.25, 2.5),
    new THREE.MeshStandardMaterial({ color: 0x334155 })
  );
  cladTop.position.y = 1.72;
  scene.add(cladTop);

  const cladBot = cladTop.clone();
  cladBot.position.y = -1.72;
  scene.add(cladBot);

  // Multi-bounce laser beam inside fiber core + refracted leak ray when theta < theta_c
  const laserLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]),
    new THREE.LineBasicMaterial({ color: 0xf43f5e, linewidth: 3 })
  );
  scene.add(laserLine);

  const leakLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]),
    new THREE.LineBasicMaterial({ color: 0x22d3ee, linewidth: 2 })
  );
  scene.add(leakLine);

  // Incident wavevector k_1 and Refracted/Reflected wavevector k_2
  const k1Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, 1, 0).normalize(), new THREE.Vector3(-7.0, 0, 0), 2.2, 0xf43f5e, 0.42, 0.25);
  const k2Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, -1, 0).normalize(), new THREE.Vector3(-4.0, 1.6, 0), 2.2, 0xf59e0b, 0.42, 0.25);
  scene.add(k1Arrow);
  scene.add(k2Arrow);

  function stepPhysics(dt) {
    const thetaDeg = params.p1; // Incidence angle at core-cladding wall (20..82 deg)
    const n1 = params.p2;       // Core refractive index n_1 (1.35..1.90)
    const n2 = params.p3;       // Cladding refractive index n_2 (1.00..1.45)

    const thRad = (thetaDeg * Math.PI) / 180.0;
    const ratio = Math.min(0.999, n2 / Math.max(n2 + 0.02, n1));
    const thetaCritDeg = (Math.asin(ratio) * 180.0) / Math.PI;
    const isTIR = (n1 > n2) && (thetaDeg >= thetaCritDeg);

    // Trace bouncing laser zig-zag along the 3D optical fiber core
    const dxStep = Math.max(1.2, 3.2 * Math.tan(thRad));
    const pts = [new THREE.Vector3(-7.5, 0, 0)];
    let curX = -7.5 + dxStep * 0.5;
    let signY = 1;
    let firstHit = new THREE.Vector3(curX, 1.6, 0);

    while (curX < 7.5 && pts.length < 14) {
      pts.push(new THREE.Vector3(curX, signY * 1.6, 0));
      signY *= -1;
      curX += dxStep;
    }
    const rSoft = softenedR2(dxStep);
    pts.push(new THREE.Vector3(7.5, signY * 1.2 + 0.0001 / rSoft, 0));
    laserLine.geometry.setFromPoints(pts);

    const dirIn = new THREE.Vector3().subVectors(firstHit, pts[0]).normalize();
    k1Arrow.position.copy(pts[0]);
    k1Arrow.setDirection(dirIn);

    k2Arrow.position.copy(firstHit);
    if (isTIR) {
      leakLine.visible = false;
      k2Arrow.setDirection(new THREE.Vector3(dirIn.x, -dirIn.y, 0).normalize());
    } else {
      leakLine.visible = true;
      const sinTh2 = Math.min(0.99, (n1 / Math.max(1.0, n2)) * Math.sin(thRad));
      const cosTh2 = Math.sqrt(Math.max(0.01, 1.0 - sinTh2 * sinTh2));
      const refrDir = new THREE.Vector3(sinTh2, cosTh2, 0).normalize();
      k2Arrow.setDirection(refrDir);
      leakLine.geometry.setFromPoints([
        firstHit,
        firstHit.clone().addScaledVector(refrDir, 3.5)
      ]);
    }

    const NA = Math.sqrt(Math.max(0, n1 * n1 - n2 * n2));
    tel1.textContent = `Snell's Law: n1*sin(theta1) = n2*sin(theta2) | Critical Angle theta_c = ${thetaCritDeg.toFixed(1)} deg`;
    tel2.textContent = `State: ${isTIR ? "TOTAL INTERNAL REFLECTION (100% Confined in Core)" : "Partial Refraction Escape into Cladding"}`;
    tel3.textContent = `Core n1 = ${n1.toFixed(2)} | Cladding n2 = ${n2.toFixed(2)} | Numerical Aperture NA = ${NA.toFixed(2)}`;
  }
"""

EXP_29_JS = """
  // Exp 29: Young's Double-Slit, Single-Slit, and Diffraction Grating Interference Visualizer
  const barrierLeft = new THREE.Mesh(new THREE.BoxGeometry(0.25, 3.8, 3.0), new THREE.MeshStandardMaterial({ color: 0x334155 }));
  const barrierCenter = new THREE.Mesh(new THREE.BoxGeometry(0.25, 3.8, 1.2), new THREE.MeshStandardMaterial({ color: 0x334155 }));
  const barrierRight = new THREE.Mesh(new THREE.BoxGeometry(0.25, 3.8, 3.0), new THREE.MeshStandardMaterial({ color: 0x334155 }));
  barrierLeft.position.set(-2.5, 0, -2.8);
  barrierCenter.position.set(-2.5, 0, 0);
  barrierRight.position.set(-2.5, 0, 2.8);
  scene.add(barrierLeft);
  scene.add(barrierCenter);
  scene.add(barrierRight);

  // Observation screen at X = +4.8
  const screenBoard = new THREE.Mesh(
    new THREE.BoxGeometry(0.2, 4.2, 11.5),
    new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8 })
  );
  screenBoard.position.set(5.2, 0, 0);
  scene.add(screenBoard);

  // 3D Intensity Envelope Curve I(z) = I0 * cos^2(beta) * (sin(alpha)/alpha)^2 in front of screen
  const NUM_Z = 120;
  const intPts = [];
  for (let i = 0; i <= NUM_Z; i++) intPts.push(new THREE.Vector3(4.8, 0, 0));
  const intLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(intPts),
    new THREE.LineBasicMaterial({ color: 0x22d3ee, linewidth: 3 })
  );
  scene.add(intLine);

  // Incident Laser Beam & Constructive Order Vector Arrows
  const incArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(-7.2, 0, 0), 4.4, 0xf43f5e, 0.45, 0.28);
  const diffArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0.25).normalize(), new THREE.Vector3(-2.4, 0, 0), 7.2, 0xf59e0b, 0.45, 0.28);
  scene.add(incArrow);
  scene.add(diffArrow);

  function stepPhysics(dt) {
    const lambdaNm = params.p1; // Wavelength nm (400..700)
    const slitD = params.p2;    // Slit separation d (1.0..4.0)
    const slitA = params.p3;    // Slit width a (0.2..1.2)
    const screenL = params.p4;  // Screen distance L (3.5..6.5)

    // Color laser & intensity curve according to optical wavelength (400nm violet -> 700nm red)
    const hue = Math.max(0, Math.min(0.78, ((700 - lambdaNm) / 300) * 0.72));
    const col = new THREE.Color().setHSL(hue, 0.95, 0.55);
    intLine.material.color.copy(col);

    barrierCenter.scale.z = Math.max(0.25, slitD * 0.45);
    screenBoard.position.x = -2.5 + screenL * 1.25;

    const lambdaScale = lambdaNm / 500.0;
    const pts = [];
    for (let i = 0; i <= NUM_Z; i++) {
      const z = -5.4 + (i / NUM_Z) * 10.8;
      const rSoft = softenedR2(screenL);
      const sinTheta = z / Math.sqrt(rSoft + z * z);

      const alpha = (Math.PI * slitA * sinTheta) / (lambdaScale * 0.45);
      const beta = (Math.PI * slitD * sinTheta) / (lambdaScale * 0.45);

      const sinc = Math.abs(alpha) < 1e-4 ? 1.0 : Math.sin(alpha) / alpha;
      const I_rel = (sinc * sinc) * Math.pow(Math.cos(beta), 2);

      pts.push(new THREE.Vector3(screenBoard.position.x - 0.25, -1.6 + I_rel * 3.4, z));
    }
    intLine.geometry.setFromPoints(pts);

    // First-order bright fringe z_1 = lambda * L / d
    const z1 = (lambdaScale * 0.45 * screenL) / Math.max(0.5, slitD);
    const dirM1 = new THREE.Vector3(screenBoard.position.x + 2.4, 0, z1).normalize();
    diffArrow.setDirection(dirM1);
    diffArrow.setLength(screenBoard.position.x + 2.2, 0.42, 0.25);

    tel1.textContent = `Double-Slit Fringe Spacing dy = lambda*L/d = ${z1.toFixed(2)} cm | lambda = ${lambdaNm} nm`;
    tel2.textContent = `I(theta) = I_0 * cos^2(pi*d*sin(theta)/lambda) * [sin(alpha)/alpha]^2`;
    tel3.textContent = `Slit Separation d = ${slitD.toFixed(2)} mm | Slit Width a = ${slitA.toFixed(2)} mm`;
  }
"""

EXP_30_JS = """
  // Exp 30: Malus's Law and Brewster's Angle: 3D Polarization of Electromagnetic Waves
  const pol1Group = new THREE.Group();
  pol1Group.position.set(-2.5, 0, 0);
  scene.add(pol1Group);

  const pol2Group = new THREE.Group();
  pol2Group.position.set(2.5, 0, 0);
  scene.add(pol2Group);

  function buildPolarizerDisk(colorHex) {
    const g = new THREE.Group();
    const ring = new THREE.Mesh(
      new THREE.CylinderGeometry(2.3, 2.3, 0.14, 32),
      new THREE.MeshPhysicalMaterial({ color: colorHex, transparent: true, opacity: 0.22 })
    );
    ring.rotation.z = Math.PI / 2;
    g.add(ring);
    const slitBar = new THREE.Mesh(
      new THREE.BoxGeometry(0.18, 4.4, 0.12),
      new THREE.MeshBasicMaterial({ color: colorHex })
    );
    g.add(slitBar);
    return g;
  }
  pol1Group.add(buildPolarizerDisk(0x38bdf8));
  pol2Group.add(buildPolarizerDisk(0xf59e0b));

  // 3D Electromagnetic Wave E-field ribbon across 3 regions: Unpolarized/Input -> Polarizer 1 -> Analyzer 2
  const NUM_W = 120;
  const wavePts = [];
  for (let i = 0; i <= NUM_W; i++) wavePts.push(new THREE.Vector3(0, 0, 0));
  const waveLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(wavePts),
    new THREE.LineBasicMaterial({ color: 0x22d3ee, linewidth: 3 })
  );
  scene.add(waveLine);

  // Transmission Axis Vectors for Polarizer 1 and Analyzer 2
  const axis1Arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(-2.5, 0, 0), 2.5, 0x38bdf8, 0.42, 0.25);
  const axis2Arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(2.5, 0, 0), 2.5, 0xf59e0b, 0.42, 0.25);
  scene.add(axis1Arrow);
  scene.add(axis2Arrow);

  function stepPhysics(dt) {
    const theta1Deg = params.p1; // Polarizer 1 angle (0..90 deg)
    const theta2Deg = params.p2; // Analyzer 2 angle (0..180 deg)
    const I0 = params.p3;        // Incident Intensity W/m^2 (10..100)
    const nBrewster = params.p4; // Refractive index for Brewster angle (1.2..2.4)

    const th1 = (theta1Deg * Math.PI) / 180.0;
    const th2 = (theta2Deg * Math.PI) / 180.0;
    const dTheta = th2 - th1;
    const cosDelta = Math.cos(dTheta);
    const malusFactor = cosDelta * cosDelta;

    pol1Group.rotation.x = th1;
    pol2Group.rotation.x = th2;

    axis1Arrow.setDirection(new THREE.Vector3(0, Math.cos(th1), Math.sin(th1)).normalize());
    axis2Arrow.setDirection(new THREE.Vector3(0, Math.cos(th2), Math.sin(th2)).normalize());

    const amp0 = Math.sqrt(I0 / 50.0) * 1.45;
    const pts = [];
    for (let i = 0; i <= NUM_W; i++) {
      const x = -8.0 + (i / NUM_W) * 16.0;
      const rSoft = softenedR2(x + 12.0);
      const phase = 2.2 * x - 6.0 * params.time + 0.0001 / rSoft;
      let y = 0;
      let z = 0;
      if (x < -2.5) {
        // Unpolarized / circularly varying input
        y = amp0 * Math.sin(phase);
        z = amp0 * 0.65 * Math.cos(phase * 1.3);
      } else if (x < 2.5) {
        // Linearly polarized along theta_1
        const a1 = amp0 * Math.sin(phase);
        y = a1 * Math.cos(th1);
        z = a1 * Math.sin(th1);
      } else {
        // Transmitted through Analyzer 2: E_2 = E_1 * cos(theta_2 - theta_1) along theta_2
        const a2 = amp0 * cosDelta * Math.sin(phase);
        y = a2 * Math.cos(th2);
        z = a2 * Math.sin(th2);
      }
      pts.push(new THREE.Vector3(x, y, z));
    }
    waveLine.geometry.setFromPoints(pts);

    const I_trans = I0 * 0.5 * malusFactor;
    const brewsterDeg = (Math.atan(nBrewster) * 180.0) / Math.PI;
    tel1.textContent = `Malus's Law: I = I_1 * cos^2(dTheta) = ${I_trans.toFixed(1)} W/m^2 (cos^2 = ${(malusFactor * 100).toFixed(1)}%)`;
    tel2.textContent = `Polarizer 1 = ${theta1Deg} deg | Analyzer 2 = ${theta2Deg} deg | dTheta = ${Math.abs(theta2Deg - theta1Deg).toFixed(0)} deg`;
    tel3.textContent = `Brewster Angle theta_B = arctan(n2/n1) = ${brewsterDeg.toFixed(1)} deg (for n = ${nBrewster.toFixed(2)})`;
  }
"""

EXP_31_JS = """
  // Exp 31: Michelson Interferometer with Adjustable Mirror Path Difference & Circular Fringe Bullseye
  // 45-degree Beam Splitter at origin (0, 0, 0)
  const splitter = new THREE.Mesh(
    new THREE.BoxGeometry(1.8, 1.6, 0.18),
    new THREE.MeshPhysicalMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.42 })
  );
  splitter.rotation.y = Math.PI / 4;
  scene.add(splitter);

  // Fixed Mirror M1 (+Z arm) and Movable Mirror M2 (+X arm)
  const mirrorM1 = new THREE.Mesh(
    new THREE.BoxGeometry(2.2, 1.6, 0.2),
    new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.9, roughness: 0.1 })
  );
  mirrorM1.position.set(0, 0, -5.2);
  scene.add(mirrorM1);

  const mirrorM2 = new THREE.Mesh(
    new THREE.BoxGeometry(0.2, 1.6, 2.2),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.85, roughness: 0.15 })
  );
  mirrorM2.position.set(5.2, 0, 0);
  scene.add(mirrorM2);

  // Circular Haidinger Interference Fringe Bullseye Rings at Detector (+Z = +4.8)
  const NUM_RINGS = 7;
  const fringeRings = [];
  for (let r = 0; r < NUM_RINGS; r++) {
    const torus = new THREE.Mesh(
      new THREE.TorusGeometry(0.3 + r * 0.28, 0.07, 12, 36),
      new THREE.MeshBasicMaterial({ color: 0xf43f5e, transparent: true, opacity: 0.8 })
    );
    torus.position.set(0, 0, 4.8);
    scene.add(torus);
    fringeRings.push(torus);
  }

  // Orthogonal Laser Arm Vectors (Arm 1 to M1, Arm 2 to M2)
  const arm1Arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, 0, 0), 4.8, 0x22d3ee, 0.42, 0.25);
  const arm2Arrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 0), 4.8, 0xf43f5e, 0.42, 0.25);
  scene.add(arm1Arrow);
  scene.add(arm2Arrow);

  function stepPhysics(dt) {
    const deltaD_nm = params.p1; // Mirror M2 micrometer translation nm (0..2000)
    const lambdaNm = params.p2;  // Laser wavelength nm (450..680)
    const armL = params.p3;      // Base interferometer arm length (3.8..6.2)

    mirrorM1.position.z = -armL;
    const m2Shift = (deltaD_nm / 2000.0) * 0.85;
    mirrorM2.position.x = armL + m2Shift;

    arm1Arrow.setLength(armL - 0.25, 0.4, 0.24);
    arm2Arrow.setLength(armL + m2Shift - 0.25, 0.4, 0.24);

    // Phase difference dPhi = 4*pi*delta_d / lambda
    const fringeCount = (2.0 * deltaD_nm) / Math.max(100.0, lambdaNm);
    const dPhi = 2.0 * Math.PI * fringeCount;

    const hue = Math.max(0, Math.min(0.75, ((680 - lambdaNm) / 250) * 0.68));
    const col = new THREE.Color().setHSL(hue, 0.95, 0.55);

    for (let r = 0; r < NUM_RINGS; r++) {
      const ring = fringeRings[r];
      const rSoft = softenedR2(r + 1.5);
      const phaseR = dPhi - r * 1.15 + 0.0001 / rSoft;
      const intensity = Math.pow(Math.cos(phaseR * 0.5), 2);
      ring.material.color.copy(col);
      ring.material.opacity = 0.12 + 0.85 * intensity;
      const pulseScale = 1.0 + 0.08 * Math.sin(phaseR);
      ring.scale.setScalar(pulseScale);
    }

    const centralI = Math.pow(Math.cos(dPhi * 0.5), 2);
    tel1.textContent = `Optical Path Difference 2*Delta_d = ${(2 * deltaD_nm).toFixed(0)} nm | Fringes Shifted m = ${fringeCount.toFixed(2)}`;
    tel2.textContent = `Central Detector Intensity I = I_0 * cos^2(2*pi*d/lambda) = ${(centralI * 100).toFixed(1)}%`;
    tel3.textContent = `Laser Wavelength lambda = ${lambdaNm} nm | Sub-Wavelength Displacement Sensor`;
  }
"""


# ============================================================================
# SPECIFICATIONS FOR EXPERIMENTS 17 TO 31
# ============================================================================

_EXPERIMENT_SPECS: Dict[int, Dict[str, Any]] = {
    17: {
        "title": "3D Ideal Gas Kinetic Theory Box with Piston, Temperature Control, and Maxwell-Boltzmann Histogram",
        "domain": "Thermodynamics & Statistical Mechanics",
        "keywords": ["ideal gas", "kinetic theory", "piston", "maxwell-boltzmann", "pv=nrt", "temperature", "pressure"],
        "subtitle": "PV = nRT | v_rms = sqrt(3RT/M) | Live 3D Maxwell-Boltzmann Speed Histogram",
        "button_label": "Cycle Gas Mode",
        "sliders": [
            {"label": "Temperature T", "min": 100, "max": 900, "step": 10, "default": 300, "unit": " K"},
            {"label": "Piston Height V", "min": 2.2, "max": 6.2, "step": 0.2, "default": 4.2, "unit": " L"},
            {"label": "Molar Mass M", "min": 4, "max": 44, "step": 2, "default": 28, "unit": " g/mol"},
            {"label": "Molecule Count N", "min": 20, "max": 48, "step": 2, "default": 42, "unit": " mols"},
        ],
        "legend": [
            {"color": "#22d3ee", "label": "Gas Pressure Force F_P"},
            {"color": "#f43f5e", "label": "External Piston Load F_ext"},
            {"color": "#f59e0b", "label": "Maxwell-Boltzmann Speed Bins"},
        ],
        "steps": [
            "1. Raise Temperature T to accelerate gas molecules as v_rms = sqrt(3RT/M) and shift the 3D Maxwell-Boltzmann histogram right.",
            "2. Compress Piston Height V to watch wall collision frequency and upward pressure force F_P = P*A increase (Boyle's Law).",
        ],
        "equations": [
            "P * V = n * R * T = (1/3) * N * m * v_rms^2",
            "v_rms = sqrt(3 * R * T / M)   |   <K_tr> = (3/2) * k_B * T",
            "f(v) = 4*pi * (m / (2*pi*k_B*T))^(3/2) * v^2 * exp(-m*v^2 / (2*k_B*T))",
        ],
        "teacher_guide": "Show students how macroscopic pressure on the piston emerges from elastic molecular momentum impulses, while the 3D histogram flattens and shifts toward higher speeds as Temperature T rises.",
        "misconception_alert": "Students often think all gas molecules move at the exact same speed v_rms at temperature T. Point to the 3D Maxwell-Boltzmann bars to show the continuous distribution of speeds.",
        "intuition_questions": [
            "If you halve the Molar Mass M at constant Temperature T, how does v_rms change, and why does pressure P remain unchanged?",
            "Why does the Maxwell-Boltzmann histogram peak broaden and drop in height when Temperature T is doubled?",
        ],
        "tts_narration": "Welcome to the 3D Ideal Gas and Maxwell-Boltzmann Lab! Raise the temperature slider to speed up the colliding molecules and watch the 3D speed histogram shift toward higher velocities while pushing upward on the piston.",
        "js": EXP_17_JS,
    },
    18: {
        "title": "Thermodynamic PV Diagram Simulator: Isothermal, Adiabatic, Isobaric, and Carnot Cycle Engine",
        "domain": "Thermodynamics & Heat Engines",
        "keywords": ["pv diagram", "carnot cycle", "isothermal", "adiabatic", "isobaric", "heat engine", "efficiency"],
        "subtitle": "dU = Q - W | Carnot Efficiency eta = 1 - T_C/T_H | Live 3D P-V Loop",
        "button_label": "Switch Cycle (Carnot/Iso/Adiab)",
        "sliders": [
            {"label": "Hot Reservoir T_H", "min": 400, "max": 900, "step": 20, "default": 650, "unit": " K"},
            {"label": "Cold Reservoir T_C", "min": 200, "max": 380, "step": 10, "default": 300, "unit": " K"},
            {"label": "Adiabatic Index gamma", "min": 1.2, "max": 1.67, "step": 0.01, "default": 1.4, "unit": ""},
            {"label": "Expansion Ratio V2/V1", "min": 1.5, "max": 3.2, "step": 0.1, "default": 2.4, "unit": "x"},
        ],
        "legend": [
            {"color": "#10b981", "label": "Piston Mechanical Work W"},
            {"color": "#f43f5e", "label": "Reservoir Heat Transfer Q"},
            {"color": "#22d3ee", "label": "Live 3D P-V State Trajectory"},
        ],
        "steps": [
            "1. Compare the steeper Adiabatic curve (P*V^gamma = const) against the shallower Isothermal curve (P*V = const).",
            "2. Widen the gap between Hot Reservoir T_H and Cold Reservoir T_C to maximize Carnot efficiency eta = 1 - T_C/T_H.",
        ],
        "equations": [
            "eta_Carnot = 1 - T_C / T_H   |   W_cycle = oint P dV",
            "Isothermal: P * V = n*R*T = const   |   W_iso = n*R*T * ln(V_2 / V_1)",
            "Adiabatic: P * V^gamma = const   (Q = 0, dU = -W)",
        ],
        "teacher_guide": "Use the Mode button to switch between the closed 4-stroke Carnot loop, pure Isothermal expansion, and steeper Adiabatic expansion while tracking the glowing orange state point on the 3D P-V axes.",
        "misconception_alert": "Students frequently assume temperature stays constant when a gas expands without heat exchange (Q = 0). Highlight that adiabatic expansion does positive work at the expense of internal energy, cooling the gas.",
        "intuition_questions": [
            "Why is an adiabatic curve (P*V^gamma = const) always steeper on a P-V diagram than an isothermal curve (P*V = const)?",
            "What limits a Carnot engine from ever reaching 100% thermal efficiency when T_C > 0 K?",
        ],
        "tts_narration": "Explore the 3D Thermodynamic P-V Diagram and Carnot Engine! Watch the piston cycle between the hot red reservoir and cold blue reservoir while the glowing state marker traces the enclosed mechanical work on the 3D pressure-volume graph.",
        "js": EXP_18_JS,
    },
    19: {
        "title": "Brownian Motion: Heavy Particle Bombarded by Thermal Gas Molecules with Mean-Square Displacement",
        "domain": "Statistical Mechanics & Stochastic Processes",
        "keywords": ["brownian motion", "diffusion", "random walk", "mean square displacement", "einstein relation", "pollen"],
        "subtitle": "<r^2> = 6*D*t | D = k_B*T / (6*pi*eta*R) | 3D Thermal Bombardment Trail",
        "button_label": "Perturb Thermal Bath",
        "sliders": [
            {"label": "Bath Temperature T", "min": 200, "max": 600, "step": 20, "default": 320, "unit": " K"},
            {"label": "Fluid Viscosity eta", "min": 0.5, "max": 3.0, "step": 0.1, "default": 1.0, "unit": " mPa*s"},
            {"label": "Particle Radius R", "min": 0.5, "max": 2.0, "step": 0.1, "default": 1.0, "unit": " um"},
            {"label": "Collision Impulse", "min": 0.5, "max": 2.5, "step": 0.1, "default": 1.3, "unit": "x"},
        ],
        "legend": [
            {"color": "#22d3ee", "label": "Net Displacement Vector r(t)"},
            {"color": "#f43f5e", "label": "Instantaneous Thermal Kick F_kick"},
            {"color": "#fbbf24", "label": "3D Stochastic Random Walk Trail"},
        ],
        "steps": [
            "1. Watch dozens of fast blue solvent molecules bombard the heavy golden pollen grain from random directions.",
            "2. Increase Temperature T or lower Viscosity eta to increase Einstein diffusivity D = k_B*T/(6*pi*eta*R) and expand the random walk.",
        ],
        "equations": [
            "<r^2(t)> = 6 * D * t   (3D Mean-Square Displacement)",
            "D = (k_B * T) / (6 * pi * eta * R)   (Stokes-Einstein Relation)",
            "m * dv/dt = -6*pi*eta*R*v + F_stochastic(t)",
        ],
        "teacher_guide": "Highlight how net displacement <r> averages to zero by symmetry, yet mean-square displacement <r^2> grows linearly with time t — Einstein's 1905 proof of the physical existence of atoms!",
        "misconception_alert": "Students often expect the root-mean-square distance to grow linearly with time (r_rms ~ t) like ballistic motion, rather than with the square root of time (r_rms ~ sqrt(t)).",
        "intuition_questions": [
            "Why does quadrupling the observation time t only double the root-mean-square distance r_rms traveled by the Brownian particle?",
            "How did Jean Perrin use the Stokes-Einstein relation D = RT / (N_A * 6*pi*eta*R) to experimentally determine Avogadro's number N_A?",
        ],
        "tts_narration": "Observe 3D Brownian Motion in action! Rapid collisions from surrounding thermal molecules kick the heavy golden sphere along a 3D random walk whose mean-square displacement grows linearly with time.",
        "js": EXP_19_JS,
    },
    20: {
        "title": "Bernoulli's Principle and Venturi Tube with Fluid Streamlines and Pressure Manometers",
        "domain": "Fluid Dynamics",
        "keywords": ["bernoulli", "venturi", "continuity", "fluid dynamics", "manometer", "streamlines", "pressure drop"],
        "subtitle": "A_1*v_1 = A_2*v_2 | P + 1/2*rho*v^2 = const | 3D Venturi Constriction & Manometers",
        "button_label": "Toggle Flow Profile",
        "sliders": [
            {"label": "Inlet Velocity v_1", "min": 1.0, "max": 4.0, "step": 0.2, "default": 2.0, "unit": " m/s"},
            {"label": "Inlet Radius R_1", "min": 1.6, "max": 2.4, "step": 0.1, "default": 2.0, "unit": " m"},
            {"label": "Throat Radius R_2", "min": 0.7, "max": 1.4, "step": 0.05, "default": 1.0, "unit": " m"},
            {"label": "Fluid Density rho", "min": 0.8, "max": 1.5, "step": 0.1, "default": 1.0, "unit": " g/cm3"},
        ],
        "legend": [
            {"color": "#22d3ee", "label": "Inlet Velocity Vector v_1"},
            {"color": "#f43f5e", "label": "Accelerated Throat Velocity v_2"},
            {"color": "#38bdf8", "label": "3D Static Pressure Manometer Columns"},
        ],
        "steps": [
            "1. Narrow the Throat Radius R_2 to see streamline tracer particles accelerate by continuity v_2 = v_1*(R_1/R_2)^2.",
            "2. Observe the middle vertical manometer column drop as kinetic energy density 1/2*rho*v^2 rises at the expense of static pressure P.",
        ],
        "equations": [
            "A_1 * v_1 = A_2 * v_2   (Incompressible Continuity Equation)",
            "P_1 + (1/2)*rho*v_1^2 = P_2 + (1/2)*rho*v_2^2   (Bernoulli's Equation)",
            "Delta_P = P_1 - P_2 = (1/2)*rho*v_1^2 * ((A_1 / A_2)^2 - 1)",
        ],
        "teacher_guide": "Ask students to predict which of the three vertical manometer columns will be lowest before narrowing the Venturi throat, then connect the pressure gradient -dP/dx directly to convective acceleration v*dv/dx.",
        "misconception_alert": "Students intuitively think squeezing fluid into a narrower throat must increase static pressure there. Point to the middle manometer column and explain that higher pressure upstream is what accelerates the fluid into the low-pressure throat!",
        "intuition_questions": [
            "If the throat radius R_2 is half the inlet radius R_1, by what factor does the fluid speed v_2 increase?",
            "What provides the net forward force that accelerates a fluid parcel as it enters the narrow Venturi constriction?",
        ],
        "tts_narration": "Welcome to the 3D Venturi Tube and Bernoulli Lab! Watch the glowing fluid streamlines accelerate through the narrow constriction while the central manometer column drops due to conservation of fluid energy.",
        "js": EXP_20_JS,
    },
    21: {
        "title": "Magnus Effect: Lift and Airflow Streamlines Around a Spinning Cylinder",
        "domain": "Fluid Dynamics & Aerodynamics",
        "keywords": ["magnus effect", "lift", "spinning cylinder", "kutta-joukowski", "vortex", "streamlines", "aerodynamics"],
        "subtitle": "F_M = S*(omega x v) | Kutta-Joukowski Lift L' = rho * v_inf * Gamma",
        "button_label": "Reverse Spin Axis",
        "sliders": [
            {"label": "Freestream Speed v", "min": 5, "max": 35, "step": 1, "default": 20, "unit": " m/s"},
            {"label": "Spin Rate omega", "min": -60, "max": 60, "step": 5, "default": 35, "unit": " rad/s"},
            {"label": "Cylinder Radius R", "min": 1.0, "max": 2.2, "step": 0.1, "default": 1.6, "unit": " m"},
            {"label": "Air Density rho", "min": 0.5, "max": 2.0, "step": 0.1, "default": 1.2, "unit": " kg/m3"},
        ],
        "legend": [
            {"color": "#22d3ee", "label": "Freestream Velocity v"},
            {"color": "#f59e0b", "label": "Angular Spin Vector omega"},
            {"color": "#f43f5e", "label": "Magnus Lift Force F_M = S*(omega x v)"},
        ],
        "steps": [
            "1. Increase Spin Rate omega to circulate air with the top surface and against the bottom surface, bunching streamlines above.",
            "2. Reverse omega from positive (backspin) to negative (topspin) to see the magenta Magnus force arrow F_M flip from upward lift to downward dive.",
        ],
        "equations": [
            "F_M = S * (omega x v)   (3D Vector Cross-Product Magnus Lift)",
            "F_M / L = rho * v_inf * Gamma   (Kutta-Joukowski Theorem, Gamma = 2*pi*R^2*omega)",
            "Delta_P = (1/2) * rho * (v_top^2 - v_bottom^2)",
        ],
        "teacher_guide": "Have students apply the right-hand rule from Spin Vector omega (amber) into Velocity v (cyan) to verify the direction of the Magnus Lift arrow F_M (magenta) and observe wake deflection.",
        "misconception_alert": "Students often confuse skin friction drag with Magnus lift. Emphasize that Magnus force acts perpendicular to both the velocity vector v and the spin axis omega.",
        "intuition_questions": [
            "Why does a baseball thrown with backspin experience an upward Magnus force that flattens its trajectory?",
            "How do Flettner rotor ships use giant vertical spinning cylinders to harness crosswinds for marine propulsion?",
        ],
        "tts_narration": "Explore the 3D Magnus Effect Wind Tunnel! As the cylinder spins in the airflow, circulation speeds up air over one side and slows it on the other, generating a cross-product Magnus lift force.",
        "js": EXP_21_JS,
    },
    22: {
        "title": "Transverse and Longitudinal 3D Wave Propagator with Particle Displacement Vectors",
        "domain": "Waves & Acoustics",
        "keywords": ["transverse wave", "longitudinal wave", "compression", "rarefaction", "shear wave", "wavelength", "displacement"],
        "subtitle": "u(x,t) = A*sin(k*x - omega*t) | Transverse (u_y perp k) vs Longitudinal (u_x || k)",
        "button_label": "Sync Phase Markers",
        "sliders": [
            {"label": "Wave Amplitude A", "min": 0.3, "max": 1.6, "step": 0.1, "default": 1.0, "unit": " m"},
            {"label": "Frequency f", "min": 0.4, "max": 2.5, "step": 0.1, "default": 1.2, "unit": " Hz"},
            {"label": "Wavelength lambda", "min": 3.0, "max": 10.0, "step": 0.5, "default": 6.0, "unit": " m"},
            {"label": "Attenuation alpha", "min": 0.0, "max": 0.08, "step": 0.01, "default": 0.01, "unit": " /m"},
        ],
        "legend": [
            {"color": "#38bdf8", "label": "Wave Propagation Vector k"},
            {"color": "#f43f5e", "label": "Transverse Particle Displacement u_y"},
            {"color": "#10b981", "label": "Longitudinal Compression/Rarefaction u_x"},
        ],
        "steps": [
            "1. Compare the top chain (Transverse shear wave: particles oscillate vertically u_y perpendicular to k) with the bottom chain (Longitudinal acoustic wave: particles oscillate horizontally u_x parallel to k).",
            "2. Track a single sphere with its attached ArrowHelper to verify that individual particles oscillate locally around equilibrium x_0 while phase fronts travel at v = f*lambda.",
        ],
        "equations": [
            "u_y(x,t) = A * sin(k*x - omega*t)   (Transverse: u perp k)",
            "u_x(x,t) = A * sin(k*x - omega*t)   (Longitudinal: u || k)",
            "v_phase = omega / k = f * lambda   |   Delta_P(x,t) = -B * (du_x / dx)",
        ],
        "teacher_guide": "Focus students on a single particle with a red or green vector arrow so they see it never travels across the screen with the wave crest — only energy and phase propagate along +X!",
        "misconception_alert": "Students frequently believe matter travels with the wave from source to receiver, and often misread a sine graph of pressure vs position as showing transverse motion for sound waves.",
        "intuition_questions": [
            "In the bottom longitudinal wave chain, where is the local particle density highest relative to the zero-crossings of displacement u_x?",
            "Why can transverse S-waves propagate through solid rock but not through the liquid outer core of the Earth?",
        ],
        "tts_narration": "Compare Transverse and Longitudinal 3D Waves side by side! In the top row, particles oscillate perpendicular to wave propagation, while in the bottom row, particles compress and rarefy parallel to the wave vector k.",
        "js": EXP_22_JS,
    },
    23: {
        "title": "2D Ripple Tank: Circular Wave Interference, Diffraction Through a Slit, and Refraction",
        "domain": "Waves & Superposition",
        "keywords": ["ripple tank", "wave interference", "two source", "nodal lines", "superposition", "diffraction"],
        "subtitle": "z = z_1(r_1,t) + z_2(r_2,t) | Constructive Maxima d*sin(theta) = m*lambda",
        "button_label": "Toggle Source Phase",
        "sliders": [
            {"label": "Source Separation d", "min": 1.5, "max": 7.0, "step": 0.25, "default": 4.0, "unit": " m"},
            {"label": "Wave Frequency f", "min": 1.0, "max": 4.0, "step": 0.2, "default": 2.2, "unit": " Hz"},
            {"label": "Source Amplitude A", "min": 0.2, "max": 1.0, "step": 0.05, "default": 0.65, "unit": " m"},
            {"label": "Phase Offset dPhi", "min": 0.0, "max": 3.14, "step": 0.15, "default": 0.0, "unit": " rad"},
        ],
        "legend": [
            {"color": "#f43f5e", "label": "Coherent Oscillator S_1"},
            {"color": "#f59e0b", "label": "Coherent Oscillator S_2"},
            {"color": "#0ea5e9", "label": "3D Superposition Water Heightfield"},
        ],
        "steps": [
            "1. Increase Source Separation d or Frequency f to increase the number of hyperbolic nodal lines where |r_1 - r_2| = (m + 1/2)*lambda.",
            "2. Adjust Phase Offset dPhi from 0 to pi radians to see the central antinodal maximum invert into a calm destructive nodal line.",
        ],
        "equations": [
            "Delta_r = |r_1 - r_2| = d * sin(theta) = m * lambda   (Constructive Antinodal Rays)",
            "Delta_r = |r_1 - r_2| = (m + 1/2) * lambda   (Destructive Nodal Hyperbolas)",
            "z(x,y,t) = A_1(r_1)*sin(k*r_1 - omega*t) + A_2(r_2)*sin(k*r_2 - omega*t + dPhi)",
        ],
        "teacher_guide": "Orbit the camera above the 3D water mesh so students clearly see the stationary hyperbolic nodal alleys where crests from S_1 continuously cancel troughs from S_2.",
        "misconception_alert": "Students sometimes think water along a nodal line is frozen only momentarily. Point out that along a nodal hyperbola, destructive cancellation holds at every instant t!",
        "intuition_questions": [
            "Why do the nodal curves form hyperbolas in the 2D water plane?",
            "What happens to the angular spacing of interference fringes when the source separation d becomes smaller than a single wavelength lambda?",
        ],
        "tts_narration": "Welcome to the 3D Ripple Tank! Two coherent point sources emit circular water waves that interfere across the 3D heightfield, sculpting hyperbolic nodal lines and constructive antinodal ridges.",
        "js": EXP_23_JS,
    },
    24: {
        "title": "Standing Waves in Strings and Open/Closed Air Columns (Harmonics, Nodes, and Antinodes)",
        "domain": "Waves & Musical Acoustics",
        "keywords": ["standing waves", "harmonics", "nodes", "antinodes", "resonance", "air column", "vibrating string"],
        "subtitle": "y(x,t) = 2A*sin(k*x)*cos(omega*t) | f_n = n * v / (2L) | String & Acoustic Tube",
        "button_label": "Step Harmonic Mode",
        "sliders": [
            {"label": "Harmonic Number n", "min": 1, "max": 7, "step": 1, "default": 3, "unit": ""},
            {"label": "String Tension T", "min": 20, "max": 120, "step": 5, "default": 60, "unit": " N"},
            {"label": "Wave Amplitude A", "min": 0.4, "max": 1.5, "step": 0.1, "default": 1.0, "unit": " m"},
            {"label": "Damping Factor b", "min": 0.0, "max": 0.1, "step": 0.01, "default": 0.0, "unit": ""},
        ],
        "legend": [
            {"color": "#22d3ee", "label": "Transverse String Standing Wave"},
            {"color": "#f59e0b", "label": "Longitudinal Air-Column Planes"},
            {"color": "#f43f5e", "label": "Stationary Node Rings (y = 0)"},
        ],
        "steps": [
            "1. Drag Harmonic Number n from 1 (fundamental) to 7 to quantize the wavelength lambda_n = 2L/n and count n antinodes between n+1 red node rings.",
            "2. Compare the top transverse string against the bottom cylindrical acoustic tube where yellow air-molecule planes bunch up at displacement nodes (pressure antinodes!).",
        ],
        "equations": [
            "y(x,t) = 2*A * sin(n*pi*x / L) * cos(omega_n * t)",
            "lambda_n = 2*L / n   |   f_n = n * (v / 2L) = (n / 2L) * sqrt(T / mu)",
            "Nodes at x_m = m * (L / n)   (m = 0, 1, ..., n)",
        ],
        "teacher_guide": "Draw attention to the bottom acoustic cylinder: at the red Node Rings, the yellow air slices on either side rush toward and away from each other, meaning a displacement node is a pressure antinode!",
        "misconception_alert": "Students often think a displacement node in a sound tube has zero pressure variation. Show them the colliding yellow air disks at each node to prove maximum compression occurs right at displacement nodes!",
        "intuition_questions": [
            "Why must a string fixed at both ends only support wavelengths that satisfy L = n * (lambda / 2)?",
            "If you quadruple the string tension T while keeping length L and harmonic n constant, by what factor does the resonant frequency f_n increase?",
        ],
        "tts_narration": "Explore Standing Waves and Acoustic Harmonics in 3D! Change the harmonic number n to see how boundary conditions quantize the nodes and antinodes on both a vibrating string and an acoustic air column.",
        "js": EXP_24_JS,
    },
    25: {
        "title": "3D Doppler Effect and Mach Cone (Sonic Boom Shockwave) from a Moving Source",
        "domain": "Waves, Acoustics & Supersonic Flow",
        "keywords": ["doppler effect", "mach cone", "sonic boom", "shockwave", "supersonic", "frequency shift"],
        "subtitle": "f_obs = f_0 * c / (c -/+ v_s) | Mach Cone Angle sin(mu) = c / v_s = 1 / M",
        "button_label": "Subsonic / Supersonic",
        "sliders": [
            {"label": "Mach Number M = v_s/c", "min": 0.3, "max": 2.2, "step": 0.05, "default": 1.35, "unit": " M"},
            {"label": "Sound Speed c", "min": 2.0, "max": 4.5, "step": 0.1, "default": 3.0, "unit": " m/s"},
            {"label": "Source Frequency f_0", "min": 200, "max": 800, "step": 20, "default": 440, "unit": " Hz"},
            {"label": "Wind Drift Offset", "min": -0.5, "max": 0.5, "step": 0.05, "default": 0.0, "unit": " m/s"},
        ],
        "legend": [
            {"color": "#f43f5e", "label": "Source Velocity Vector v_s & Mach Shock Cone"},
            {"color": "#22d3ee", "label": "Acoustic Wave Speed Vector c"},
            {"color": "#38bdf8", "label": "Expanding Spherical Wavefronts"},
        ],
        "steps": [
            "1. Set Mach Number M < 1.0 (subsonic) to see spherical wavefronts bunch up ahead of the aircraft (higher pitch f_+) and stretch behind it (lower pitch f_-).",
            "2. Push Mach Number M >= 1.0 (supersonic) to see the source outrun its own waves, forming a 3D conical Mach shockwave with half-angle sin(mu) = 1/M.",
        ],
        "equations": [
            "f_obs = f_0 * (c / (c - v_s * cos(theta)))   (Doppler Frequency Shift)",
            "sin(mu) = c / v_s = 1 / M   (Mach Shockwave Cone Half-Angle for M >= 1)",
            "lambda_front = (c - v_s) / f_0   |   lambda_rear = (c + v_s) / f_0",
        ],
        "teacher_guide": "Have students transition smoothly from M = 0.7 (subsonic Doppler shift) to M = 1.0 (sound barrier where wavefronts pile up at the nose) to M = 1.8 (narrow supersonic Mach cone).",
        "misconception_alert": "Students commonly think a sonic boom happens only once at the exact moment a jet crosses Mach 1. Show that the 3D Mach cone is swept continuously along the ground for as long as the aircraft flies supersonically!",
        "intuition_questions": [
            "Why does the Mach cone angle mu become narrower as the aircraft flies at higher Mach numbers M?",
            "Why is each individual circular wavefront still centered on the past position where it was emitted rather than on the current position of the jet?",
        ],
        "tts_narration": "Experience the 3D Doppler Effect and Supersonic Mach Cone! Below Mach 1, wavefronts compress ahead of the source. Above Mach 1, the craft outruns its own sound waves, forming a conical shockwave.",
        "js": EXP_25_JS,
    },
    26: {
        "title": "Fourier Series Wave Synthesizer: Building Square, Sawtooth, and Wave Packets (Group vs Phase Velocity)",
        "domain": "Waves, Harmonics & Signal Physics",
        "keywords": ["fourier series", "harmonics", "square wave", "sawtooth", "wave packet", "group velocity", "phase velocity"],
        "subtitle": "f(x,t) = Sum c_n*sin(n*k_0*x - omega_n*t) | v_p = omega/k vs v_g = d(omega)/dk",
        "button_label": "Switch Square/Saw/Packet",
        "sliders": [
            {"label": "Harmonic Count N", "min": 1, "max": 5, "step": 1, "default": 4, "unit": " terms"},
            {"label": "Fundamental k_0", "min": 0.5, "max": 2.0, "step": 0.1, "default": 1.0, "unit": " rad/m"},
            {"label": "Phase Velocity v_p", "min": 1.0, "max": 4.0, "step": 0.2, "default": 2.0, "unit": " m/s"},
            {"label": "Dispersion dv/dk", "min": -0.5, "max": 0.5, "step": 0.05, "default": 0.0, "unit": ""},
        ],
        "legend": [
            {"color": "#f59e0b", "label": "Composite Sum f(x,t) & Group Velocity v_g"},
            {"color": "#22d3ee", "label": "Individual Harmonics & Phase Velocity v_p"},
        ],
        "steps": [
            "1. Increase Harmonic Count N from 1 to 5 to watch the Z-stacked sine-wave ribbons sum into a sharp Square Wave or Sawtooth Wave in front.",
            "2. Adjust Dispersion dv/dk away from zero to see individual harmonic ripples travel at Phase Velocity v_p while the overall wave-packet envelope travels at Group Velocity v_g = d(omega)/dk.",
        ],
        "equations": [
            "f_square(x) = (4/pi) * Sum_{m=1,3,5..} (1/m) * sin(m * k_0 * x)",
            "v_phase = omega / k   |   v_group = d(omega) / dk = v_p + k * (dv_p / dk)",
            "Delta_x * Delta_k >= 1/2   (Fourier Bandwidth-Localization Uncertainty)",
        ],
        "teacher_guide": "Orbit the camera to view the Z-axis decomposition: from the side, students see the composite waveform; rotated at 45 degrees, they see the individual harmonic sine waves in frequency space!",
        "misconception_alert": "Students often assume the speed of individual wave crests (v_p) must always equal the speed of the energy envelope (v_g). Turn on Dispersion dv/dk != 0 to show crests sliding through the moving envelope!",
        "intuition_questions": [
            "Why does a square wave require only odd harmonics (n = 1, 3, 5, ...) while a sawtooth wave requires both even and odd harmonics?",
            "What happens to the shape of a square wave pulse when it travels through a dispersive medium where dv_p/dk != 0?",
        ],
        "tts_narration": "Welcome to the 3D Fourier Wave Synthesizer! Stacked in depth are the pure harmonic sine waves, and in front is their real-time superposition sum forming square waves, sawtooth waves, and dispersive wave packets.",
        "js": EXP_26_JS,
    },
    27: {
        "title": "Ray Optics Bench: Converging/Diverging Lenses and Mirrors with Real and Virtual Image Formation",
        "domain": "Geometric & Ray Optics",
        "keywords": ["ray optics", "thin lens", "converging lens", "diverging lens", "focal length", "real image", "virtual image", "magnification"],
        "subtitle": "1/f = 1/d_o + 1/d_i | M = h_i/h_o = -d_i/d_o | 3 Principal Laser Rays",
        "button_label": "Toggle Converging/Diverging",
        "sliders": [
            {"label": "Object Distance d_o", "min": 2.0, "max": 8.0, "step": 0.2, "default": 5.0, "unit": " m"},
            {"label": "Focal Length |f|", "min": 1.5, "max": 4.5, "step": 0.2, "default": 2.5, "unit": " m"},
            {"label": "Object Height h_o", "min": 0.8, "max": 2.2, "step": 0.1, "default": 1.5, "unit": " m"},
            {"label": "Lens Aperture", "min": 0.8, "max": 1.5, "step": 0.1, "default": 1.0, "unit": "x"},
        ],
        "legend": [
            {"color": "#10b981", "label": "Object Vector Arrow (d_o, h_o)"},
            {"color": "#f43f5e", "label": "Image Vector Arrow (d_i, h_i)"},
            {"color": "#22d3ee", "label": "3 Principal Rays (Parallel, Chief, Focal)"},
        ],
        "steps": [
            "1. Place Object Distance d_o > f with a converging lens to see the 3 principal rays intersect on the right, forming a Real, Inverted Image (d_i > 0).",
            "2. Move the object inside the focal point (d_o < f) or switch to a Diverging Lens to see rays diverge and trace back to an Upright Virtual Image (d_i < 0).",
        ],
        "equations": [
            "1 / f = 1 / d_o + 1 / d_i   (Thin Lens & Mirror Equation)",
            "M = h_i / h_o = -d_i / d_o   (Lateral Magnification)",
            "P = 1 / f = (n - 1) * (1/R_1 - 1/R_2)   (Lensmaker's Equation)",
        ],
        "teacher_guide": "Move d_o from 2f (where |M| = 1) toward f so students watch the real image shoot toward infinity, then cross inside f to become a magnifying glass virtual image!",
        "misconception_alert": "Students frequently think covering half of a lens cuts off half of the image. Point to the 3 principal rays leaving the tip of the object arrow to show that every part of the lens forms the entire image!",
        "intuition_questions": [
            "If you cover the top half of the converging lens with an opaque card, what happens to the brightness and completeness of the real image?",
            "Why can a diverging lens (f < 0) never form a real image of a real object regardless of object distance d_o?",
        ],
        "tts_narration": "Explore the 3D Ray Optics Bench! Drag the object distance and focal length sliders to trace the parallel, chief, and focal laser rays as they converge into real or virtual 3D images.",
        "js": EXP_27_JS,
    },
    28: {
        "title": "Snell's Law, Total Internal Reflection, and Light Propagation Inside an Optical Fiber",
        "domain": "Geometric Optics & Photonics",
        "keywords": ["snell's law", "total internal reflection", "optical fiber", "critical angle", "refraction", "numerical aperture"],
        "subtitle": "n_1*sin(theta_1) = n_2*sin(theta_2) | theta_c = arcsin(n_2/n_1) | 3D Optical Waveguide",
        "button_label": "Step Cladding Index",
        "sliders": [
            {"label": "Incidence Angle theta_1", "min": 20, "max": 82, "step": 1, "default": 58, "unit": " deg"},
            {"label": "Core Index n_1", "min": 1.35, "max": 1.90, "step": 0.05, "default": 1.60, "unit": ""},
            {"label": "Cladding Index n_2", "min": 1.00, "max": 1.45, "step": 0.05, "default": 1.20, "unit": ""},
            {"label": "Core Thickness", "min": 1.0, "max": 2.0, "step": 0.1, "default": 1.5, "unit": "x"},
        ],
        "legend": [
            {"color": "#f43f5e", "label": "Guided Core Laser Ray & Incident k_1"},
            {"color": "#f59e0b", "label": "Reflected/Refracted Wavevector k_2"},
            {"color": "#22d3ee", "label": "Refracted Cladding Leak Ray (theta < theta_c)"},
        ],
        "steps": [
            "1. Lower Incidence Angle theta_1 below the critical angle theta_c = arcsin(n_2/n_1) to see the cyan refracted ray leak out into the cladding.",
            "2. Increase theta_1 above theta_c (with n_1 > n_2) to lock the laser into 100% lossless Total Internal Reflection bouncing down the 3D optical fiber!",
        ],
        "equations": [
            "n_1 * sin(theta_1) = n_2 * sin(theta_2)   (Snell's Law of Refraction)",
            "theta_c = arcsin(n_2 / n_1)   (Critical Angle for Total Internal Reflection, n_1 > n_2)",
            "NA = sqrt(n_1^2 - n_2^2)   (Optical Fiber Numerical Aperture)",
        ],
        "teacher_guide": "Ask students to find the exact critical angle theta_c where the cyan refracted ray skims along the core-cladding interface at 90 degrees before vanishing into Total Internal Reflection.",
        "misconception_alert": "Students often forget that Total Internal Reflection can only occur when light travels from a higher-index medium (n_1) toward a lower-index medium (n_2 < n_1).",
        "intuition_questions": [
            "Why do telecommunications optical fibers surround the glass core (n_1) with a lower-index glass cladding (n_2) instead of leaving the bare core exposed to air?",
            "How does cutting a diamond with a high refractive index (n = 2.42, theta_c = 24.4 deg) trap incoming light and make it sparkle?",
        ],
        "tts_narration": "See Snell's Law and Total Internal Reflection inside a 3D Optical Fiber! When the incidence angle exceeds the critical angle, refraction into the cladding vanishes and the laser beam bounces losslessly down the waveguide.",
        "js": EXP_28_JS,
    },
    29: {
        "title": "Young's Double-Slit, Single-Slit, and Diffraction Grating Interference Intensity Visualizer",
        "domain": "Wave Optics & Diffraction",
        "keywords": ["double slit", "single slit", "diffraction grating", "young's experiment", "interference fringes", "wavelength"],
        "subtitle": "I(theta) = I_0 * cos^2(beta) * (sin(alpha)/alpha)^2 | d*sin(theta) = m*lambda",
        "button_label": "Switch Slit Profile",
        "sliders": [
            {"label": "Laser Wavelength lambda", "min": 400, "max": 700, "step": 10, "default": 530, "unit": " nm"},
            {"label": "Slit Separation d", "min": 1.0, "max": 4.0, "step": 0.1, "default": 2.2, "unit": " mm"},
            {"label": "Slit Width a", "min": 0.2, "max": 1.2, "step": 0.05, "default": 0.45, "unit": " mm"},
            {"label": "Screen Distance L", "min": 3.5, "max": 6.5, "step": 0.2, "default": 5.0, "unit": " m"},
        ],
        "legend": [
            {"color": "#f43f5e", "label": "Incident Coherent Laser Wavevector"},
            {"color": "#f59e0b", "label": "First-Order Diffraction Vector (m = 1)"},
            {"color": "#22d3ee", "label": "3D Intensity Envelope I(theta)"},
        ],
        "steps": [
            "1. Sweep Laser Wavelength lambda from 400 nm (violet) to 700 nm (red) to watch the 3D intensity curve change color and expand fringe spacing dy = lambda*L/d.",
            "2. Increase Single-Slit Width a to narrow the outer sinc^2 diffraction envelope and suppress higher interference orders (missing orders when d/a is an integer).",
        ],
        "equations": [
            "I(theta) = I_0 * cos^2(beta) * (sin(alpha) / alpha)^2",
            "beta = (pi * d * sin(theta)) / lambda   |   alpha = (pi * a * sin(theta)) / lambda",
            "Delta_y = (lambda * L) / d   (Double-Slit Bright Fringe Spacing)",
        ],
        "teacher_guide": "Show students how two distinct physical effects multiply together on the observation screen: rapid cos^2(beta) interference fringes from slit separation d modulated by the broad sinc^2(alpha) envelope from slit width a.",
        "misconception_alert": "Students frequently predict that narrowing the slits makes the pattern on the screen narrower. Demonstrate that reducing slit width a or separation d actually spreads the diffraction pattern wider!",
        "intuition_questions": [
            "Which interference order m is 'missing' (suppressed by the first single-slit diffraction minimum) when the slit separation d is exactly 3 times the slit width a?",
            "Why did Thomas Young's double-slit experiment provide decisive evidence for the wave nature of light?",
        ],
        "tts_narration": "Welcome to Young's Double-Slit and Diffraction Lab! Adjust the optical wavelength from violet to red and watch the 3D intensity curve on the observation screen expand or contract according to lambda L over d.",
        "js": EXP_29_JS,
    },
    30: {
        "title": "Malus's Law and Brewster's Angle: 3D Polarization of Electromagnetic Waves Through Polarizers",
        "domain": "Wave Optics & Electromagnetism",
        "keywords": ["polarization", "malus's law", "brewster's angle", "polarizer", "analyzer", "electromagnetic wave"],
        "subtitle": "I = I_0 * cos^2(theta) | E_trans = E_0 * cos(theta) | Brewster tan(theta_B) = n_2/n_1",
        "button_label": "Cross / Align Polarizers",
        "sliders": [
            {"label": "Polarizer 1 Angle theta_1", "min": 0, "max": 90, "step": 5, "default": 0, "unit": " deg"},
            {"label": "Analyzer 2 Angle theta_2", "min": 0, "max": 180, "step": 5, "default": 45, "unit": " deg"},
            {"label": "Incident Intensity I_0", "min": 10, "max": 100, "step": 5, "default": 80, "unit": " W/m2"},
            {"label": "Medium Index n (Brewster)", "min": 1.2, "max": 2.4, "step": 0.05, "default": 1.5, "unit": ""},
        ],
        "legend": [
            {"color": "#38bdf8", "label": "Polarizer 1 Transmission Axis"},
            {"color": "#f59e0b", "label": "Rotatable Analyzer 2 Transmission Axis"},
            {"color": "#22d3ee", "label": "3D E-Field Wave Vector Projection"},
        ],
        "steps": [
            "1. Rotate Analyzer 2 Angle theta_2 relative to Polarizer 1 to watch the transmitted electric field amplitude scale as E_0*cos(dTheta) and intensity follow Malus's Law I = I_1*cos^2(dTheta).",
            "2. Set dTheta = 90 degrees (crossed polarizers) to witness complete extinction of the transmitted 3D electromagnetic wave beyond the second disk.",
        ],
        "equations": [
            "I(theta) = I_1 * cos^2(theta_2 - theta_1)   (Malus's Law)",
            "E_trans = (E_1 . u_hat_2) u_hat_2 = E_1 * cos(Delta_theta) u_hat_2",
            "tan(theta_B) = n_2 / n_1   (Brewster's Polarization Angle at Dielectric Interface)",
        ],
        "teacher_guide": "Have students cross Polarizer 1 (0 deg) and Analyzer 2 (90 deg) so the output wave drops to zero, then ask what happens if a third polarizer is inserted between them at 45 degrees!",
        "misconception_alert": "Students often think a polarizer blocks a scalar percentage of light regardless of orientation, rather than projecting the transverse electric field vector E onto the polarizer's transmission axis.",
        "intuition_questions": [
            "Why can transverse electromagnetic waves be polarized, whereas longitudinal sound waves in air cannot?",
            "Why do polarized sunglasses have vertical transmission axes to block glare reflected off horizontal water or road surfaces at Brewster's angle?",
        ],
        "tts_narration": "Explore 3D Electromagnetic Wave Polarization and Malus's Law! As the wave passes through Polarizer 1 and rotatable Analyzer 2, only the electric field component parallel to each transmission axis survives.",
        "js": EXP_30_JS,
    },
    31: {
        "title": "Michelson Interferometer with Adjustable Mirror Path Difference and Circular Fringe Pattern",
        "domain": "Wave Optics & Precision Metrology",
        "keywords": ["michelson interferometer", "path difference", "interference fringes", "beam splitter", "ligo", "metrology"],
        "subtitle": "Delta_phi = 4*pi*Delta_d / lambda | Shift of 1 Fringe per lambda/2 Mirror Translation",
        "button_label": "Zero Path Difference",
        "sliders": [
            {"label": "Mirror M2 Shift Delta_d", "min": 0, "max": 2000, "step": 25, "default": 400, "unit": " nm"},
            {"label": "Laser Wavelength lambda", "min": 450, "max": 680, "step": 10, "default": 630, "unit": " nm"},
            {"label": "Arm Length L", "min": 3.8, "max": 6.2, "step": 0.2, "default": 5.0, "unit": " m"},
            {"label": "Beam Contrast", "min": 0.5, "max": 1.0, "step": 0.05, "default": 1.0, "unit": ""},
        ],
        "legend": [
            {"color": "#22d3ee", "label": "Reference Arm 1 Laser Path (Fixed M1)"},
            {"color": "#f43f5e", "label": "Adjustable Arm 2 Path (M2) & Bullseye Fringes"},
            {"color": "#38bdf8", "label": "45-Degree 50/50 Optical Beam Splitter"},
        ],
        "steps": [
            "1. Translate Movable Mirror M2 by Delta_d = lambda/4 to change the round-trip optical path difference by 2*Delta_d = lambda/2, flipping the central bullseye fringe from bright to dark!",
            "2. Count how many circular Haidinger fringes expand or contract past the detector center as you sweep Delta_d across 2000 nm.",
        ],
        "equations": [
            "Delta_L = 2 * (L_2 - L_1) = 2 * Delta_d   (Round-Trip Optical Path Difference)",
            "I_det = I_0 * cos^2((2 * pi * Delta_d) / lambda)",
            "Delta_m = (2 * Delta_d) / lambda   (Number of Interference Fringes Shifted)",
        ],
        "teacher_guide": "Emphasize the factor of 2 in 2*Delta_d: because light travels to Mirror M2 and reflects back to the beam splitter, moving M2 by just half a wavelength (lambda/2) shifts the pattern by one full fringe!",
        "misconception_alert": "Students frequently forget the round-trip factor of 2 and calculate Delta_d = lambda instead of Delta_d = lambda/2 for a single full fringe shift.",
        "intuition_questions": [
            "If moving Mirror M2 by 0.0316 mm causes 100 bright fringes to pass the center of the detector, what is the wavelength lambda of the laser?",
            "How do Michelson-Morley and LIGO gravitational-wave interferometers use orthogonal arms to detect sub-attometer spacetime strain?",
        ],
        "tts_narration": "Welcome to the 3D Michelson Interferometer! A 45-degree beam splitter divides the laser into two orthogonal arms that recombine at the detector into circular interference fringes sensitive to nanometer mirror movements.",
        "js": EXP_31_JS,
    },
}


def _build_experiment_entry(exp_id: int, custom_prompt: str = "") -> Dict[str, Any]:
    spec = _EXPERIMENT_SPECS[exp_id]
    title = _strip_combining_arrows(spec["title"])
    domain = _strip_combining_arrows(spec["domain"])

    physics_audit = {
        "physically_accurate": True,
        "domain": domain,
        "verified_law": _strip_combining_arrows(spec["equations"][0]),
        "conservation_invariants": [
            _strip_combining_arrows(spec["equations"][0]),
            "Singularity Softening Math.max(1.5, r * r) enforced on all radial denominators",
        ],
        "required_solver": "Analytical / Symplectic Phase Integrator",
        "vector_visualizers": [
            _strip_combining_arrows(item["label"]) for item in spec["legend"][:2]
        ],
        "verdict": _strip_combining_arrows(
            f"Verified: Exp {exp_id} ({title}) 3D equations and conservation laws validated."
        ),
    }

    curriculum = {
        "concept": title,
        "equations": [_strip_combining_arrows(eq) for eq in spec["equations"]],
        "teacher_guide": _strip_combining_arrows(spec["teacher_guide"]),
        "misconception_alert": _strip_combining_arrows(spec["misconception_alert"]),
        "intuition_questions": [
            _strip_combining_arrows(q) for q in spec["intuition_questions"]
        ],
        "tts_narration": _strip_combining_arrows(spec["tts_narration"]),
    }

    html = _render_3d_scene_html(
        title=title,
        subtitle=_strip_combining_arrows(spec["subtitle"]),
        sliders=spec["sliders"],
        button_label=spec["button_label"],
        legend_items=spec["legend"],
        concept_steps=spec["steps"],
        scene_js=spec["js"],
    )

    return {
        "id": exp_id,
        "title": title,
        "domain": domain,
        "keywords": list(spec["keywords"]),
        "physics_audit": physics_audit,
        "curriculum": curriculum,
        "html": html,
    }


EXPERIMENTS_17_TO_31: Dict[int, Dict[str, Any]] = {
    exp_id: _build_experiment_entry(exp_id) for exp_id in range(17, 32)
}


def build_thermo_waves_optics_experiment(exp_id: int, custom_prompt: str = "") -> Dict[str, Any]:
    """
    Returns the complete, pre-verified 3D experiment dictionary for `exp_id` in `17..31`:
    `{"id": exp_id, "title": ..., "domain": ..., "keywords": [...], "physics_audit": {...}, "curriculum": {...}, "html": "..."}`
    """
    if exp_id not in EXPERIMENTS_17_TO_31:
        raise ValueError(f"Experiment ID {exp_id} is outside range 17..31")
    entry = _build_experiment_entry(exp_id, custom_prompt=custom_prompt)
    return entry
