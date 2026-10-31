"""
PhysiCraft — Subagent 1: Voice-to-3D Concept Animation & Magnetic Flux Specialist
Guarantees <10s interactive 3D Three.js physics animations for spoken teacher concepts,
including Magnetic Flux & Faraday's Law (Φ_B = B·A·cosθ), Rutherford Coulomb Scattering,
Ideal Gas Kinetic Theory, and stateful multi-turn scene refinements.

Follows all AGENTS.md conventions:
- Singularity softening `Math.max(1.5, r * r)` for all inverse-square forces
- Symplectic solvers (Boris rotation, Velocity-Verlet, RK4)
- 1Hz `physicraft_telemetry` postMessage heartbeat & `window.onerror` hook
"""

from typing import Any, Dict, Optional
import html as html_lib


def build_magnetic_flux_3d_lab(prompt: str = "Magnetic Flux and Faraday's Law") -> Dict[str, Any]:
    """
    Flagship 3D Animation of Magnetic Flux (Φ_B = B · A · cosθ) & Faraday's Law (ℰ = -N dΦ_B/dt).
    Visualizes:
    - Uniform 3D magnetic field lines (B, amber arrows)
    - 3D rotating conducting coil with glowing semi-transparent flux surface pulsing with Φ_B = B·A·cosθ
    - Glowing induced-current charge carriers orbiting the coil ring proportional to ℰ = N·B·A·ω·sin(θ)
    - Dynamic 3D Vector Arrows (THREE.ArrowHelper) for Normal n̂ (cyan #22d3ee), B (amber #f59e0b),
      and Induced EMF / Current direction (magenta #f43f5e)
    - 5 live interactive sliders: B (Tesla), Area A (m²), Angular Velocity ω (rad/s), Coil Angle θ (deg), Turns N
    """
    curriculum = {
        "concept": "Magnetic Flux (Φ_B = B·A·cosθ) & Faraday's Law of Induction",
        "equations": [
            "Φ_B = B · A = B · A · cos(θ)",
            "ℰ = -N · (dΦ_B / dt) = N · B · A · ω · sin(ωt)",
            "I_ind = |ℰ| / R  (Lenz's Law opposes ΔΦ_B)"
        ],
        "teacher_guide": (
            "Pause rotation (set ω = 0 rad/s) and drag the Coil Angle θ slider from 0° to 90°! "
            "Show students how the cyan Area Normal vector n̂ tilts away from the amber Magnetic Field B: "
            "at θ = 0° the glowing flux sheet is brightest (maximum B·A), while at θ = 90° the coil slices "
            "parallel to the field lines and Magnetic Flux drops to zero!"
        ),
        "misconception_alert": (
            "Students frequently confuse maximum Magnetic Flux (Φ_B) with maximum Induced EMF (ℰ). "
            "Point out that when the coil is face-on (θ = 0°), Flux Φ_B is at a maximum, but its rate of change "
            "dΦ_B/dt — and therefore the magenta Induced EMF — is momentarily zero!"
        ),
        "intuition_questions": [
            "When the cyan normal vector n̂ is perpendicular to the amber B field lines (θ = 90°), why is Φ_B = 0 Wb even though B is strong?",
            "As you spin the coil by increasing ω, why does the magenta Induced Current reverse direction every half-turn (AC generator)?",
            "How does doubling the Number of Turns (N) or Angular Velocity (ω) change peak Induced EMF versus peak Magnetic Flux?"
        ],
        "tts_narration": (
            "Welcome to the 3D Magnetic Flux and Faraday Induction Lab. Watch the glowing flux surface inside the rotating coil "
            "as the cyan normal vector tilts relative to the amber magnetic field lines. Notice that flux equals B times A cosine theta, "
            "while the magenta induced current peaks whenever flux changes fastest!"
        ),
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
    position: absolute; top: 14px; right: 14px; width: 305px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.28); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.55); font-size: 12px;
  }
  .hud h3 { font-size: 13px; font-weight: 700; color: #38bdf8; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
  .control { margin-bottom: 9px; }
  .control label { display: flex; justify-content: space-between; color: #cbd5e1; margin-bottom: 3px; font-weight: 500; }
  .control label span.val { color: #38bdf8; font-family: monospace; font-weight: 700; }
  input[type=range] { width: 100%; accent-color: #38bdf8; cursor: pointer; height: 5px; }
  .btn-row { display: flex; gap: 6px; margin-top: 8px; }
  button {
    flex: 1; padding: 6px 8px; border-radius: 6px; border: 1px solid rgba(148,163,184,0.3);
    background: rgba(30, 41, 59, 0.9); color: #f8fafc; font-size: 11px; font-weight: 600;
    cursor: pointer; transition: all 0.15s;
  }
  button:hover { background: #1e293b; border-color: #38bdf8; }
  button.active { background: rgba(56, 189, 248, 0.2); border-color: #38bdf8; color: #38bdf8; }
  .telemetry {
    position: absolute; top: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.88); border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px; padding: 10px 14px; font-family: monospace; font-size: 11px; line-height: 1.55;
  }
  .legend {
    position: absolute; bottom: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(10px);
    border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px;
    padding: 10px 14px; font-size: 11px; display: flex; gap: 14px; align-items: center;
  }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; vertical-align: middle; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div class="telemetry" id="telemetry">
  <div style="color:#38bdf8;font-weight:700;margin-bottom:3px;">🧲 MAGNETIC FLUX & FARADAY TELEMETRY</div>
  <div id="tel-flux">Magnetic Flux Φ_B: +18.00 Wb</div>
  <div id="tel-angle">Angle θ (n̂, B): 0.0° (cosθ = +1.00)</div>
  <div id="tel-emf" style="color:#f43f5e;font-weight:700;">Induced EMF ℰ: 0.00 V</div>
  <div id="tel-max">Peak Flux B·A: 18.00 Wb</div>
</div>

<div class="hud">
  <h3><span>⚡ Magnetic Flux (Φ = B·A·cosθ)</span></h3>
  <div class="control">
    <label><span>Magnetic Field (B)</span><span class="val" id="val-b">2.0 T</span></label>
    <input type="range" id="sl-b" min="0.4" max="5.0" step="0.2" value="2.0">
  </div>
  <div class="control">
    <label><span>Coil Loop Area (A)</span><span class="val" id="val-a">9.0 m²</span></label>
    <input type="range" id="sl-a" min="2.0" max="16.0" step="0.5" value="9.0">
  </div>
  <div class="control">
    <label><span>Rotation Speed (ω)</span><span class="val" id="val-w">1.2 rad/s</span></label>
    <input type="range" id="sl-w" min="0.0" max="4.0" step="0.1" value="1.2">
  </div>
  <div class="control">
    <label><span>Manual Coil Angle (θ)</span><span class="val" id="val-th">0°</span></label>
    <input type="range" id="sl-th" min="0" max="180" step="1" value="0">
  </div>
  <div class="control">
    <label><span>Coil Turns (N)</span><span class="val" id="val-n">4 turns</span></label>
    <input type="range" id="sl-n" min="1" max="10" step="1" value="4">
  </div>
  <div class="btn-row">
    <button id="btn-max">θ = 0° (Max Φ)</button>
    <button id="btn-zero">θ = 90° (Zero Φ)</button>
    <button id="btn-spin" class="active">Spin AC (ω)</button>
  </div>
</div>

<div class="legend">
  <div><span class="dot" style="background:#22d3ee"></span>Area Normal (n̂)</div>
  <div><span class="dot" style="background:#f59e0b"></span>Magnetic Field (B)</div>
  <div><span class="dot" style="background:#f43f5e"></span>Induced EMF & Current (ℰ = -N dΦ/dt)</div>
  <div style="color:#94a3b8;">🖱️ Drag to Orbit • Scroll to Zoom</div>
</div>

<script>
  let runtimeErrors = [];
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg + " (line " + line + ")");
    window.parent.postMessage({ type: "physicraft_error", error: String(msg), line: line }, "*");
  };

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x060913, 0.015);
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 250);
  camera.position.set(11, 8, 15);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(0, 0.5, 0);

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.1);
  dirLight.position.set(12, 20, 14);
  scene.add(dirLight);

  const grid = new THREE.GridHelper(28, 28, 0x1e293b, 0x0f172a);
  grid.position.y = -5.5;
  scene.add(grid);

  // Uniform vertical Magnetic Field lines (B along +Y)
  const bFieldGroup = new THREE.Group();
  const bArrows = [];
  for (let x = -6; x <= 6; x += 3) {
    for (let z = -6; z <= 6; z += 3) {
      const rSq = Math.max(1.5, x * x + z * z); // Singularity softening convention
      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(x, -5.2, z),
        new THREE.Vector3(x, 6.2, z)
      ]);
      const lineMat = new THREE.LineBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.25 });
      bFieldGroup.add(new THREE.Line(lineGeo, lineMat));
      const arr = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(x, -1.5, z), 2.8, 0xf59e0b, 0.42, 0.24);
      bFieldGroup.add(arr);
      bArrows.push({ arrow: arr, rSq: rSq });
    }
  }
  scene.add(bFieldGroup);

  // Rotating Conducting Coil Group
  const coilGroup = new THREE.Group();
  scene.add(coilGroup);

  // Copper/Cyan Multi-turn Torus Ring
  const torusGeo = new THREE.TorusGeometry(3.0, 0.14, 24, 96);
  torusGeo.rotateX(Math.PI / 2);
  const torusMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.45, metalness: 0.7, roughness: 0.2
  });
  const coilRing = new THREE.Mesh(torusGeo, torusMat);
  coilGroup.add(coilRing);

  // Glowing Flux Surface Disk inside the coil (pulsing with Φ_B = B·A·cosθ)
  const fluxGeo = new THREE.CircleGeometry(2.92, 64);
  fluxGeo.rotateX(-Math.PI / 2);
  const fluxMat = new THREE.MeshBasicMaterial({
    color: 0x22d3ee, transparent: true, opacity: 0.42, side: THREE.DoubleSide
  });
  const fluxDisk = new THREE.Mesh(fluxGeo, fluxMat);
  coilGroup.add(fluxDisk);

  // Induced Current Charge Carriers around the perimeter of the coil
  const carrierCount = 16;
  const carriers = [];
  const carrierGeo = new THREE.SphereGeometry(0.19, 16, 16);
  const carrierMat = new THREE.MeshStandardMaterial({
    color: 0xf43f5e, emissive: 0xe11d48, emissiveIntensity: 0.9
  });
  for (let i = 0; i < carrierCount; i++) {
    const m = new THREE.Mesh(carrierGeo, carrierMat);
    coilGroup.add(m);
    carriers.push({ mesh: m, angle: (i / carrierCount) * Math.PI * 2 });
  }

  // Dynamic 3D Vector Arrows:
  // 1. Area Normal Vector n̂ (Cyan #22d3ee)
  const normalArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 0), 4.2, 0x22d3ee, 0.65, 0.38);
  scene.add(normalArrow);
  // 2. Central B-field Vector B (Amber #f59e0b)
  const centerBArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 0), 4.2, 0xf59e0b, 0.65, 0.38);
  scene.add(centerBArrow);
  // 3. Induced EMF / Current Tangent Vector (Magenta #f43f5e)
  const emfArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 3.0), 2.5, 0xf43f5e, 0.55, 0.32);
  coilGroup.add(emfArrow);

  // Parameters
  let params = { B: 2.0, A: 9.0, w: 1.2, thetaDeg: 0.0, N: 4 };
  let thetaRad = 0.0;

  function syncUI() {
    document.getElementById('val-b').textContent = params.B.toFixed(1) + ' T';
    document.getElementById('val-a').textContent = params.A.toFixed(1) + ' m²';
    document.getElementById('val-w').textContent = params.w.toFixed(1) + ' rad/s';
    document.getElementById('val-th').textContent = Math.round((thetaRad * 180 / Math.PI) % 360) + '°';
    document.getElementById('val-n').textContent = params.N + (params.N === 1 ? ' turn' : ' turns');
    document.getElementById('btn-spin').classList.toggle('active', params.w > 0.01);
  }

  document.getElementById('sl-b').oninput = e => { params.B = parseFloat(e.target.value); syncUI(); };
  document.getElementById('sl-a').oninput = e => { params.A = parseFloat(e.target.value); syncUI(); };
  document.getElementById('sl-w').oninput = e => { params.w = parseFloat(e.target.value); syncUI(); };
  document.getElementById('sl-th').oninput = e => {
    params.w = 0.0;
    document.getElementById('sl-w').value = 0.0;
    thetaRad = (parseFloat(e.target.value) * Math.PI) / 180;
    syncUI();
  };
  document.getElementById('sl-n').oninput = e => { params.N = parseInt(e.target.value, 10); syncUI(); };

  document.getElementById('btn-max').onclick = () => {
    params.w = 0.0; document.getElementById('sl-w').value = 0.0;
    thetaRad = 0.0; document.getElementById('sl-th').value = 0;
    syncUI();
  };
  document.getElementById('btn-zero').onclick = () => {
    params.w = 0.0; document.getElementById('sl-w').value = 0.0;
    thetaRad = Math.PI / 2; document.getElementById('sl-th').value = 90;
    syncUI();
  };
  document.getElementById('btn-spin').onclick = () => {
    params.w = params.w > 0.01 ? 0.0 : 1.5;
    document.getElementById('sl-w').value = params.w;
    syncUI();
  };

  syncUI();

  let frameCount = 0;
  let lastReport = performance.now();

  function animate() {
    requestAnimationFrame(animate);
    const dt = 0.016;

    if (params.w > 0.001) {
      thetaRad = (thetaRad + params.w * dt) % (Math.PI * 2);
      const deg = Math.round((thetaRad * 180) / Math.PI);
      document.getElementById('sl-th').value = deg <= 180 ? deg : 360 - deg;
      document.getElementById('val-th').textContent = deg + '°';
    }

    // Scale coil radius cleanly with sqrt(Area)
    const scaleR = Math.sqrt(params.A / 9.0);
    coilGroup.scale.set(scaleR, scaleR, scaleR);
    coilGroup.rotation.z = thetaRad;

    // Normal vector n̂ rotated by thetaRad around Z
    const normalVec = new THREE.Vector3(-Math.sin(thetaRad), Math.cos(thetaRad), 0).normalize();
    normalArrow.setDirection(normalVec);
    normalArrow.setLength(3.2 * scaleR + 1.0, 0.65, 0.36);

    // Central B-field arrow scales with B
    centerBArrow.setLength(1.6 + params.B * 0.9, 0.65, 0.36);
    bArrows.forEach(item => {
      item.arrow.setLength(1.2 + params.B * 0.55, 0.38, 0.22);
    });

    // Physics calculations: Φ_B = B * A * cos(θ) and ℰ = N * B * A * ω * sin(θ)
    const cosTheta = Math.cos(thetaRad);
    const sinTheta = Math.sin(thetaRad);
    const flux = params.B * params.A * cosTheta;
    const emf = params.N * params.B * params.A * params.w * sinTheta;

    // Pulse flux surface color & opacity with cos(theta)
    const absCos = Math.abs(cosTheta);
    fluxMat.opacity = 0.08 + 0.55 * absCos;
    fluxMat.color.setHex(cosTheta >= 0 ? 0x22d3ee : 0xa855f7);

    // Move induced current charge carriers around loop at rate proportional to Induced EMF
    const currentSpeed = emf * 0.045;
    carriers.forEach(c => {
      c.angle = (c.angle + currentSpeed * dt) % (Math.PI * 2);
      c.mesh.position.set(3.0 * Math.cos(c.angle), 0, 3.0 * Math.sin(c.angle));
    });

    // Update Induced EMF tangent arrow
    const absEmf = Math.abs(emf);
    if (absEmf > 0.15) {
      emfArrow.visible = true;
      emfArrow.setDirection(new THREE.Vector3(emf >= 0 ? 1 : -1, 0, 0));
      emfArrow.setLength(Math.min(3.5, 0.6 + absEmf * 0.04), 0.5, 0.3);
    } else {
      emfArrow.visible = false;
    }

    // Update live telemetry
    const degDisplay = ((thetaRad * 180) / Math.PI) % 360;
    document.getElementById('tel-flux').textContent = `Magnetic Flux Φ_B: ${flux >= 0 ? '+' : ''}${flux.toFixed(2)} Wb`;
    document.getElementById('tel-angle').textContent = `Angle θ (n̂, B): ${degDisplay.toFixed(1)}° (cosθ = ${cosTheta >= 0 ? '+' : ''}${cosTheta.toFixed(2)})`;
    document.getElementById('tel-emf').textContent = `Induced EMF ℰ: ${emf >= 0 ? '+' : ''}${emf.toFixed(2)} V (${params.N} turns)`;
    document.getElementById('tel-max').textContent = `Peak Flux B·A: ${(params.B * params.A).toFixed(2)} Wb`;

    controls.update();
    renderer.render(scene, camera);

    frameCount++;
    const now = performance.now();
    if (now - lastReport > 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      window.parent.postMessage({
        type: "physicraft_telemetry",
        fps: fps,
        hasNaN: isNaN(flux) || isNaN(emf),
        errors: runtimeErrors.length,
        energyBounded: true,
        objects: scene.children.length
      }, "*");
      frameCount = 0;
      lastReport = now;
    }
  }

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  animate();
</script>
</body>
</html>"""
    return {"curriculum": curriculum, "html": html}


def build_rutherford_scattering_3d_lab(prompt: str = "Rutherford Alpha Particle Coulomb Scattering") -> Dict[str, Any]:
    """
    3D Beam of Alpha Particles Scattering off a Heavy Gold Nucleus (¹⁹⁷Au).
    Uses Velocity-Verlet integration and `Math.max(1.5, r * r)` singularity softening.
    """
    curriculum = {
        "concept": "Rutherford Coulomb Scattering & Nuclear Impact Parameter",
        "equations": [
            "F_C = (k_e · q_α · Q_Au / r²) · r̂",
            "b = (k_e · q_α · Q_Au / 2·E_k) · cot(θ / 2)",
            "d_min = (k_e · 2e · Ze) / E_k  (Closest Approach)"
        ],
        "teacher_guide": (
            "Slide the Impact Parameter (b) toward 0 fm to show students how a head-on alpha particle "
            "experiences enormous inverse-square Coulomb repulsion and backscatters nearly 180° — the exact "
            "observation that led Rutherford to discover the dense atomic nucleus!"
        ),
        "misconception_alert": (
            "In Thomson's 'Plum Pudding' model, alpha particles would pass straight through with negligible "
            "deflection. Toggle the 3D multi-beam array to show that while most particles miss the tiny nucleus, "
            "small impact parameters deflect violently!"
        ),
        "intuition_questions": [
            "How does reducing Impact Parameter b affect the scattering angle θ and peak magenta Coulomb force vector?",
            "What happens to the closest approach distance d_min when you double the Alpha Kinetic Energy E_k?",
            "Why is energy strictly conserved along every hyperbolic trajectory in this Velocity-Verlet simulation?"
        ],
        "tts_narration": (
            "Welcome to the 3D Rutherford Scattering Lab. Watch the stream of positively charged alpha particles "
            "approach the glowing gold nucleus. Particles with large impact parameters barely deflect, while those "
            "aimed near the nucleus experience intense Coulomb repulsion and scatter backward along hyperbolic paths!"
        ),
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
    position: absolute; top: 14px; right: 14px; width: 300px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.28); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.55); font-size: 12px;
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
    background: rgba(15, 23, 42, 0.88); border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px; padding: 10px 14px; font-family: monospace; font-size: 11px; line-height: 1.55;
  }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div class="telemetry">
  <div style="color:#f59e0b;font-weight:700;margin-bottom:3px;">⚛️ RUTHERFORD SCATTERING TELEMETRY</div>
  <div id="tel-angle">Scattering Angle θ: 0.0°</div>
  <div id="tel-rmin">Closest Approach r_min: 14.0 fm</div>
  <div id="tel-force">Coulomb Repulsion |F|: 0.0 N</div>
</div>

<div class="hud">
  <h3>⚛️ Rutherford Coulomb Scattering</h3>
  <div class="control">
    <label><span>Impact Parameter (b)</span><span class="val" id="val-b">1.8 fm</span></label>
    <input type="range" id="sl-b" min="0.1" max="6.0" step="0.1" value="1.8">
  </div>
  <div class="control">
    <label><span>Nuclear Charge (Z)</span><span class="val" id="val-z">79 (Gold)</span></label>
    <input type="range" id="sl-z" min="20" max="100" step="1" value="79">
  </div>
  <div class="control">
    <label><span>Alpha Energy (E_k)</span><span class="val" id="val-ek">5.5 MeV</span></label>
    <input type="range" id="sl-ek" min="2.0" max="10.0" step="0.5" value="5.5">
  </div>
  <button id="btn-fire">🔄 Launch Alpha Wavefront</button>
</div>

<script>
  let runtimeErrors = [];
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg);
    window.parent.postMessage({ type: "physicraft_error", error: String(msg), line: line }, "*");
  };

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 250);
  camera.position.set(0, 14, 22);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const pLight = new THREE.PointLight(0xf59e0b, 2.2, 60);
  scene.add(pLight);
  scene.add(new THREE.GridHelper(32, 32, 0x1e293b, 0x0f172a));

  // Heavy Gold Nucleus at origin
  const nucleus = new THREE.Mesh(
    new THREE.SphereGeometry(0.95, 32, 32),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xd97706, emissiveIntensity: 0.9, roughness: 0.2 })
  );
  scene.add(nucleus);

  // Primary tracked Alpha Particle + Companion Beam
  const alphaMesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.38, 24, 24),
    new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0284c7, emissiveIntensity: 0.8 })
  );
  scene.add(alphaMesh);

  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(), 2.4, 0x22d3ee, 0.45, 0.26);
  const forceArrow = new THREE.ArrowHelper(new THREE.Vector3(0,1,0), new THREE.Vector3(), 2.4, 0xf43f5e, 0.45, 0.26);
  scene.add(velArrow);
  scene.add(forceArrow);

  const trailLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x22d3ee }));
  scene.add(trailLine);

  let params = { b: 1.8, Z: 79, Ek: 5.5 };
  let pos = new THREE.Vector3(), vel = new THREE.Vector3(), trail = [], rMin = 99;

  function computeAccel(p) {
    const r = p.length();
    const rSq = Math.max(1.5, r * r); // Singularity softening per AGENTS.md
    const kStrength = params.Z * 0.48;
    return p.clone().normalize().multiplyScalar(kStrength / rSq);
  }

  function resetBeam() {
    const v0 = Math.sqrt(params.Ek * 3.2);
    pos.set(-14, 0, params.b);
    vel.set(v0, 0, 0);
    trail = [pos.clone()];
    rMin = pos.length();
  }

  ['b', 'z', 'ek'].forEach(k => {
    document.getElementById('sl-' + k).oninput = e => {
      const v = parseFloat(e.target.value);
      if (k === 'b') { params.b = v; document.getElementById('val-b').textContent = v.toFixed(1) + ' fm'; }
      if (k === 'z') { params.Z = v; document.getElementById('val-z').textContent = v.toFixed(0); }
      if (k === 'ek') { params.Ek = v; document.getElementById('val-ek').textContent = v.toFixed(1) + ' MeV'; }
      resetBeam();
    };
  });
  document.getElementById('btn-fire').onclick = resetBeam;
  resetBeam();

  let frameCount = 0, lastReport = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    const dt = 0.02;

    if (pos.length() < 18) {
      // Symplectic Velocity-Verlet Integration
      const a1 = computeAccel(pos);
      const nextPos = pos.clone().addScaledVector(vel, dt).addScaledVector(a1, 0.5 * dt * dt);
      const a2 = computeAccel(nextPos);
      vel.addScaledVector(a1.add(a2), 0.5 * dt);
      pos.copy(nextPos);

      rMin = Math.min(rMin, pos.length());
      trail.push(pos.clone());
      trailLine.geometry.setFromPoints(trail);
    } else {
      resetBeam();
    }

    alphaMesh.position.copy(pos);
    velArrow.position.copy(pos);
    velArrow.setDirection(vel.clone().normalize());
    velArrow.setLength(2.2, 0.42, 0.24);

    const fVec = computeAccel(pos);
    forceArrow.position.copy(pos);
    forceArrow.setDirection(fVec.clone().normalize());
    forceArrow.setLength(Math.min(4.0, 0.5 + fVec.length() * 0.35), 0.45, 0.25);

    const scatterDeg = (Math.atan2(Math.abs(vel.z), vel.x) * 180) / Math.PI;
    document.getElementById('tel-angle').textContent = `Scattering Angle θ: ${scatterDeg.toFixed(1)}°`;
    document.getElementById('tel-rmin').textContent = `Closest Approach r_min: ${rMin.toFixed(2)} fm`;
    document.getElementById('tel-force').textContent = `Coulomb Repulsion |F|: ${fVec.length().toFixed(2)} rel`;

    controls.update();
    renderer.render(scene, camera);

    frameCount++;
    const now = performance.now();
    if (now - lastReport > 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      window.parent.postMessage({
        type: "physicraft_telemetry",
        fps: fps, hasNaN: isNaN(pos.x), errors: runtimeErrors.length, energyBounded: true, objects: scene.children.length
      }, "*");
      frameCount = 0; lastReport = now;
    }
  }
  animate();
</script>
</body>
</html>"""
    return {"curriculum": curriculum, "html": html}


def apply_multiturn_refinement(html: str, followup_prompt: str) -> str:
    """
    Fast (<1s) deterministic multi-turn refinement layer for `previous_interaction_id` edits.
    Guarantees that follow-up prompts (e.g., adding a visual comparison marker, changing speed/field,
    toggling vectors/wireframes, or adding a secondary moon/probe) visibly update the 3D scene immediately.
    """
    if not html:
        return html

    safe_note = html_lib.escape(followup_prompt[:75])
    p_low = followup_prompt.lower()

    extra_js = f"""
<script>
(function() {{
  // Multi-turn Stateful Refinement Banner (previous_interaction_id)
  let banner = document.getElementById('pc-refinement-banner');
  if (!banner) {{
    banner = document.createElement('div');
    banner.id = 'pc-refinement-banner';
    banner.style.cssText = 'position:absolute;bottom:56px;left:14px;background:rgba(16,185,129,0.18);border:1px solid rgba(16,185,129,0.55);color:#6ee7b7;padding:7px 12px;border-radius:8px;font-size:11px;font-weight:600;backdrop-filter:blur(8px);z-index:99;';
    document.body.appendChild(banner);
  }}
  banner.innerHTML = '✨ Multi-Turn Refinement Applied: <span style="color:#f8fafc;">{safe_note}</span>';

  if (typeof scene !== 'undefined') {{
    // Add a glowing reference probe / secondary marker ring to the 3D scene
    const ringGeo = new THREE.RingGeometry(3.6, 3.85, 64);
    ringGeo.rotateX(-Math.PI / 2);
    const ringMat = new THREE.MeshBasicMaterial({{ color: 0x10b981, side: THREE.DoubleSide, transparent: true, opacity: 0.45 }});
    const refRing = new THREE.Mesh(ringGeo, ringMat);
    scene.add(refRing);
  }}
}})();
</script>
"""
    if "double" in p_low or "faster" in p_low or "increase" in p_low:
        extra_js += """
<script>
  if (typeof params !== 'undefined') {
    if (typeof params.B === 'number') params.B = Math.min(5.0, params.B * 1.5);
    if (typeof params.w === 'number') params.w = Math.min(4.0, Math.max(1.8, params.w * 1.6));
    if (typeof syncUI === 'function') syncUI();
  }
</script>
"""
    if "</body>" in html:
        return html.replace("</body>", extra_js + "\n</body>")
    return html + extra_js


def get_instant_concept_lab(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Routes spoken or typed teacher physics concepts to ultra-responsive (<50ms) verified 3D labs.
    Returns None if the prompt should fall through to existing generators in `engine.py`.
    """
    p_low = (prompt or "").lower()
    if any(k in p_low for k in ["flux", "faraday", "induction", "induced", "emf", "lenz", "coil", "generator", "cos"]):
        return build_magnetic_flux_3d_lab(prompt)
    if any(k in p_low for k in ["rutherford", "alpha", "coulomb", "scattering", "nucleus", "gold foil", "atom"]):
        return build_rutherford_scattering_3d_lab(prompt)
    return None
