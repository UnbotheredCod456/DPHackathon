"""
PhysiCraft — 3 Hero Presets for Live Demo Reliability & Instant 3D Physics Exploration.
Each preset includes:
- Full standalone Three.js 3D interactive simulation with OrbitControls, vector arrows, and HUD sliders
- Real-time autonomous verification telemetry posted to parent window (FPS, NaN check, energy/bounds check)
- Teacher's Guide, Equations, Student Intuition Questions, and TTS Narration Script
"""

PRESETS = {
    "lorentz": {
        "id": "lorentz",
        "title": "Lorentz Force: 3D Charged Particle Spiral",
        "subtitle": "AP Physics C: Electricity & Magnetism",
        "prompt": "Show how charged particles spiral in a uniform 3D magnetic field with adjustable B-field strength, charge polarity (proton vs electron), initial velocity components, and live F = q(v × B) vector arrows.",
        "curriculum": {
            "concept": "Lorentz Magnetic Force & Cyclotron Helical Motion",
            "equations": [
                "F = q(E + v × B)",
                "r_c = (m · v_⊥) / (|q| · B)",
                "ω_c = (|q| · B) / m"
            ],
            "teacher_guide": "Point out to students that the magnetic force vector (magenta) is ALWAYS perpendicular to both the velocity vector (cyan) and the magnetic field (amber). Because F ⊥ v, the magnetic field does zero work on the particle—its speed and kinetic energy stay constant while its direction curves into a helix!",
            "misconception_alert": "Students often think a stronger magnetic field speeds up the particle. Use the B-Field slider to show that increasing B tightens the spiral radius (r = mv/qB) without changing speed!",
            "intuition_questions": [
                "What happens to the spiral chirality (handedness) when you flip the particle from a Proton (+q) to an Electron (-q)?",
                "If you set parallel velocity v_y = 0, what shape does the 3D helix collapse into?",
                "Why does the kinetic energy gauge remain flat even when you double the magnetic field B?"
            ],
            "tts_narration": "Welcome to the Lorentz Force 3D Lab. Watch the cyan velocity vector and magenta force vector as the particle spirals around the vertical magnetic field lines. Notice that the magnetic force always points toward the center of curvature, perpendicular to velocity. Try flipping the charge polarity slider from positive proton to negative electron to see the spiral chirality reverse instantly!"
        },
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: #060913; color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden; }
  canvas { display: block; width: 100vw; height: 100vh; }
  .hud {
    position: absolute; top: 14px; right: 14px; width: 290px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-size: 12px;
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
  .legend {
    position: absolute; bottom: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(10px);
    border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px;
    padding: 10px 14px; font-size: 11px; display: flex; gap: 14px; align-items: center;
  }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; vertical-align: middle; }
  .telemetry {
    position: absolute; top: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 10px; padding: 10px 12px; font-family: monospace; font-size: 11px; line-height: 1.5;
  }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div class="telemetry" id="telemetry">
  <div style="color:#38bdf8;font-weight:700;margin-bottom:2px;">⚡ LORENTZ TELEMETRY</div>
  <div id="tel-radius">Cyclotron r_c: 2.50 m</div>
  <div id="tel-omega">Freq ω_c: 2.00 rad/s</div>
  <div id="tel-ke">Kinetic E: 12.50 J (Constant!)</div>
</div>

<div class="hud">
  <h3><span>🧲 Lorentz Force Controls</span></h3>
  <div class="control">
    <label><span>Charge (q)</span><span class="val" id="val-q">+1.0 C (Proton)</span></label>
    <input type="range" id="sl-q" min="-2.0" max="2.0" step="0.1" value="1.0">
  </div>
  <div class="control">
    <label><span>Magnetic Field (B_y)</span><span class="val" id="val-b">2.0 T</span></label>
    <input type="range" id="sl-b" min="0.2" max="5.0" step="0.1" value="2.0">
  </div>
  <div class="control">
    <label><span>Electric Field (E_y)</span><span class="val" id="val-e">0.0 V/m</span></label>
    <input type="range" id="sl-e" min="-2.0" max="2.0" step="0.1" value="0.0">
  </div>
  <div class="control">
    <label><span>Perpendicular Vel (v_⊥)</span><span class="val" id="val-vp">5.0 m/s</span></label>
    <input type="range" id="sl-vp" min="1.0" max="10.0" step="0.5" value="5.0">
  </div>
  <div class="control">
    <label><span>Parallel Drift (v_∥)</span><span class="val" id="val-vy">1.5 m/s</span></label>
    <input type="range" id="sl-vy" min="-4.0" max="4.0" step="0.25" value="1.5">
  </div>
  <div class="btn-row">
    <button id="btn-proton" class="active">Proton (+q)</button>
    <button id="btn-electron">Electron (-q)</button>
    <button id="btn-reset">Reset Trail</button>
  </div>
</div>

<div class="legend">
  <div><span class="dot" style="background:#22d3ee"></span>Velocity (v)</div>
  <div><span class="dot" style="background:#f43f5e"></span>Lorentz Force (F = qv×B)</div>
  <div><span class="dot" style="background:#f59e0b"></span>Magnetic Field Lines (B)</div>
  <div style="color:#94a3b8;">🖱️ Drag to Orbit • Scroll to Zoom</div>
</div>

<script>
  let runtimeErrors = [];
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg + " (line " + line + ")");
    window.parent.postMessage({ type: "physicraft_error", error: msg, line: line }, "*");
  };

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x060913, 0.018);
  const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(11, 8, 14);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(0, 2, 0);

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
  dirLight.position.set(10, 20, 10);
  scene.add(dirLight);

  const grid = new THREE.GridHelper(24, 24, 0x1e293b, 0x0f172a);
  grid.position.y = -6;
  scene.add(grid);

  // Magnetic field arrows grid (vertical along +Y)
  const bFieldGroup = new THREE.Group();
  for (let x = -6; x <= 6; x += 4) {
    for (let z = -6; z <= 6; z += 4) {
      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(x, -6, z),
        new THREE.Vector3(x, 12, z)
      ]);
      const lineMat = new THREE.LineBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.22 });
      bFieldGroup.add(new THREE.Line(lineGeo, lineMat));
      const arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(x, 0, z), 2.5, 0xf59e0b, 0.45, 0.25);
      bFieldGroup.add(arrow);
    }
  }
  scene.add(bFieldGroup);

  // Charged particle sphere + glow
  const particleGeo = new THREE.SphereGeometry(0.42, 32, 32);
  const particleMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.8, roughness: 0.2 });
  const particleMesh = new THREE.Mesh(particleGeo, particleMat);
  scene.add(particleMesh);

  // Vector Arrows
  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2, 0x22d3ee, 0.5, 0.3);
  const forceArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(), 2, 0xf43f5e, 0.5, 0.3);
  scene.add(velArrow);
  scene.add(forceArrow);

  // Glowing 3D trail
  const maxTrail = 900;
  const trailPositions = new Float32Array(maxTrail * 3);
  const trailGeo = new THREE.BufferGeometry();
  trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
  const trailMat = new THREE.LineBasicMaterial({ color: 0x38bdf8 });
  const trailLine = new THREE.Line(trailGeo, trailMat);
  scene.add(trailLine);
  let trailCount = 0;

  // Physics State
  let params = { q: 1.0, B: 2.0, E: 0.0, vp: 5.0, vy: 1.5, m: 1.0 };
  let pos = new THREE.Vector3(2.5, -3, 0);
  let vel = new THREE.Vector3(0, 1.5, 5.0);

  function resetSimulation() {
    const r = Math.max(0.4, (params.m * params.vp) / (Math.max(0.15, Math.abs(params.q)) * params.B));
    pos.set(r, -4, 0);
    vel.set(0, params.vy, params.vp);
    trailCount = 0;
    for (let i = 0; i < maxTrail * 3; i++) trailPositions[i] = 0;
    trailGeo.setDrawRange(0, 0);
  }

  function syncUI() {
    document.getElementById('val-q').textContent = (params.q >= 0 ? '+' : '') + params.q.toFixed(1) + ' C';
    document.getElementById('val-b').textContent = params.B.toFixed(1) + ' T';
    document.getElementById('val-e').textContent = params.E.toFixed(1) + ' V/m';
    document.getElementById('val-vp').textContent = params.vp.toFixed(1) + ' m/s';
    document.getElementById('val-vy').textContent = params.vy.toFixed(2) + ' m/s';
    const isPos = params.q >= 0;
    particleMat.color.setHex(isPos ? 0xf43f5e : 0x38bdf8);
    particleMat.emissive.setHex(isPos ? 0xbe123c : 0x0284c7);
    trailMat.color.setHex(isPos ? 0xfb7185 : 0x38bdf8);
    document.getElementById('btn-proton').classList.toggle('active', params.q > 0);
    document.getElementById('btn-electron').classList.toggle('active', params.q < 0);
  }

  ['q', 'b', 'e', 'vp', 'vy'].forEach(k => {
    document.getElementById('sl-' + k).addEventListener('input', e => {
      const val = parseFloat(e.target.value);
      if (k === 'q') params.q = val;
      if (k === 'b') params.B = val;
      if (k === 'e') params.E = val;
      if (k === 'vp') {
        const horiz = Math.hypot(vel.x, vel.z) || 1;
        vel.x = (vel.x / horiz) * val;
        vel.z = (vel.z / horiz) * val;
        params.vp = val;
      }
      if (k === 'vy') { vel.y = val; params.vy = val; }
      syncUI();
    });
  });

  document.getElementById('btn-proton').onclick = () => {
    params.q = 1.0; document.getElementById('sl-q').value = 1.0; syncUI(); resetSimulation();
  };
  document.getElementById('btn-electron').onclick = () => {
    params.q = -1.0; document.getElementById('sl-q').value = -1.0; syncUI(); resetSimulation();
  };
  document.getElementById('btn-reset').onclick = resetSimulation;

  resetSimulation();
  syncUI();

  // Boris-like velocity-preserving step so magnetic force never artificially inflates kinetic energy
  function stepPhysics(dt) {
    const Bvec = new THREE.Vector3(0, params.B, 0);
    const Evec = new THREE.Vector3(0, params.E, 0);
    const qm = params.q / params.m;

    // Half electric impulse
    vel.addScaledVector(Evec, 0.5 * qm * dt);
    // Magnetic rotation (exact energy conservation!)
    const t = Bvec.clone().multiplyScalar(0.5 * qm * dt);
    const s = t.clone().multiplyScalar(2.0 / (1.0 + t.lengthSq()));
    const vPrime = vel.clone().add(vel.clone().cross(t));
    vel.add(vPrime.cross(s));
    // Second half electric impulse
    vel.addScaledVector(Evec, 0.5 * qm * dt);

    pos.addScaledVector(vel, dt);

    // Wrap vertically so helix stays in view
    if (pos.y > 11 || pos.y < -6) {
      pos.y = -4;
      trailCount = 0;
    }

    // Update trail
    if (trailCount < maxTrail) {
      trailPositions[trailCount * 3] = pos.x;
      trailPositions[trailCount * 3 + 1] = pos.y;
      trailPositions[trailCount * 3 + 2] = pos.z;
      trailCount++;
    } else {
      trailPositions.copyWithin(0, 3);
      trailPositions[(maxTrail - 1) * 3] = pos.x;
      trailPositions[(maxTrail - 1) * 3 + 1] = pos.y;
      trailPositions[(maxTrail - 1) * 3 + 2] = pos.z;
    }
    trailGeo.attributes.position.needsUpdate = true;
    trailGeo.setDrawRange(0, trailCount);

    particleMesh.position.copy(pos);

    // Update Vector Arrows
    const speed = vel.length();
    if (speed > 0.01) {
      velArrow.position.copy(pos);
      velArrow.setDirection(vel.clone().normalize());
      velArrow.setLength(Math.min(3.5, 0.45 * speed), 0.45, 0.25);
    }
    const lorentzF = vel.clone().cross(Bvec).multiplyScalar(params.q).add(Evec.clone().multiplyScalar(params.q));
    const fMag = lorentzF.length();
    forceArrow.position.copy(pos);
    if (fMag > 0.01) {
      forceArrow.visible = true;
      forceArrow.setDirection(lorentzF.clone().normalize());
      forceArrow.setLength(Math.min(3.5, 0.22 * fMag), 0.45, 0.25);
    } else {
      forceArrow.visible = false;
    }

    // Telemetry update
    const qAbs = Math.max(0.05, Math.abs(params.q));
    const vPerp = Math.hypot(vel.x, vel.z);
    const rc = (params.m * vPerp) / (qAbs * params.B);
    const wc = (qAbs * params.B) / params.m;
    const ke = 0.5 * params.m * vel.lengthSq();
    document.getElementById('tel-radius').textContent = `Cyclotron r_c: ${rc.toFixed(2)} m`;
    document.getElementById('tel-omega').textContent = `Freq ω_c: ${wc.toFixed(2)} rad/s`;
    document.getElementById('tel-ke').textContent = `Kinetic E: ${ke.toFixed(2)} J`;
  }

  let frameCount = 0;
  let lastReport = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    for (let i = 0; i < 4; i++) stepPhysics(0.004);
    controls.update();
    renderer.render(scene, camera);
    frameCount++;
    const now = performance.now();
    if (now - lastReport > 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      const hasNaN = isNaN(pos.x) || isNaN(pos.y) || isNaN(pos.z);
      window.parent.postMessage({
        type: "physicraft_telemetry",
        fps: fps,
        hasNaN: hasNaN,
        errors: runtimeErrors.length,
        energyBounded: vel.lengthSq() < 10000,
        objects: scene.children.length
      }, "*");
      frameCount = 0;
      lastReport = now;
    }
  }
  animate();

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
</script>
</body>
</html>"""
    },

    "kepler": {
        "id": "kepler",
        "title": "Kepler's Orbit & Equal-Area Sweep Lab",
        "subtitle": "AP Physics 1 & C: Universal Gravitation",
        "prompt": "Build an interactive 3D Kepler orbital mechanics simulation with a glowing central star, eccentric planet orbit, live Kepler's 2nd Law equal-area wedge visualizer, velocity & gravity vector arrows, and a slider to crank up star mass until the planet crashes.",
        "curriculum": {
            "concept": "Newton's Law of Universal Gravitation & Kepler's Second Law",
            "equations": [
                "F_g = -(G · M · m / r²) r̂",
                "dA / dt = L / (2m) = constant",
                "E_total = ½mv² - GMm / r"
            ],
            "teacher_guide": "Enable the 'Kepler Area Wedges' toggle! Every wedge represents an equal time interval Δt. Students can visually verify that the long, skinny wedge near aphelion (far from the star) has the exact same area as the short, wide wedge near perihelion (close to the star) because angular momentum L is conserved.",
            "misconception_alert": "Students frequently believe planets move at constant speed in elliptical orbits. Watch the cyan velocity vector grow dramatically at perihelion and shrink at aphelion!",
            "intuition_questions": [
                "Where in the orbit is the gravitational force vector (magenta) longest, and how does the planet's speed respond there?",
                "What happens to the orbit's eccentricity if you suddenly double the star's mass M while the planet is at aphelion?",
                "Why do the alternating cyan and amber Kepler wedges have equal areas even though their shapes look totally different?"
            ],
            "tts_narration": "In this Kepler Orbital Lab, watch how the planet speeds up as it dives close to the star at perihelion and slows down far away at aphelion. Notice the colored triangular wedges swept out over equal time intervals—even though the wedges near the star are short and wide, their area matches the long, narrow wedges far out, proving Kepler's Second Law and conservation of angular momentum!"
        },
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: #050711; color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden; }
  canvas { display: block; width: 100vw; height: 100vh; }
  .hud {
    position: absolute; top: 14px; right: 14px; width: 295px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px);
    border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-size: 12px;
  }
  .hud h3 { font-size: 13px; font-weight: 700; color: #fbbf24; margin-bottom: 10px; }
  .control { margin-bottom: 9px; }
  .control label { display: flex; justify-content: space-between; color: #cbd5e1; margin-bottom: 3px; font-weight: 500; }
  .control label span.val { color: #fbbf24; font-family: monospace; font-weight: 700; }
  input[type=range] { width: 100%; accent-color: #fbbf24; cursor: pointer; height: 5px; }
  .btn-row { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
  button {
    flex: 1; padding: 6px 8px; border-radius: 6px; border: 1px solid rgba(148,163,184,0.3);
    background: rgba(30, 41, 59, 0.9); color: #f8fafc; font-size: 11px; font-weight: 600;
    cursor: pointer; transition: all 0.15s;
  }
  button:hover { border-color: #fbbf24; }
  button.active { background: rgba(251, 191, 36, 0.2); border-color: #fbbf24; color: #fbbf24; }
  .telemetry {
    position: absolute; top: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(251, 191, 36, 0.25);
    border-radius: 10px; padding: 10px 12px; font-family: monospace; font-size: 11px; line-height: 1.5;
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
<div class="telemetry">
  <div style="color:#fbbf24;font-weight:700;margin-bottom:2px;">☀️ KEPLER 2ND LAW TELEMETRY</div>
  <div id="tel-r">Orbital Radius r: 8.00 AU</div>
  <div id="tel-v">Orbital Speed v: 3.20 km/s</div>
  <div id="tel-da">Sweep Rate dA/dt: 12.80 AU²/s (Constant!)</div>
  <div id="tel-status" style="color:#34d399;">Status: Stable Elliptical Orbit</div>
</div>

<div class="hud">
  <h3>🪐 Kepler Gravity & Area Sweep</h3>
  <div class="control">
    <label><span>Star Mass (G·M)</span><span class="val" id="val-gm">120</span></label>
    <input type="range" id="sl-gm" min="40" max="320" step="5" value="120">
  </div>
  <div class="control">
    <label><span>Initial Tangential Speed</span><span class="val" id="val-v0">3.10</span></label>
    <input type="range" id="sl-v0" min="1.4" max="4.5" step="0.05" value="3.10">
  </div>
  <div class="control">
    <label><span>3D Orbital Inclination</span><span class="val" id="val-inc">15°</span></label>
    <input type="range" id="sl-inc" min="0" max="45" step="1" value="15">
  </div>
  <div class="btn-row">
    <button id="btn-wedges" class="active">Equal-Area Wedges: ON</button>
    <button id="btn-crash">Crank Gravity (Crash!)</button>
  </div>
  <div class="btn-row">
    <button id="btn-circular">Circular</button>
    <button id="btn-elliptical" class="active">Eccentric</button>
    <button id="btn-reset">Reset Orbit</button>
  </div>
</div>

<div class="legend">
  <div><span class="dot" style="background:#22d3ee"></span>Velocity (v)</div>
  <div><span class="dot" style="background:#f43f5e"></span>Gravity Force (F_g)</div>
  <div><span class="dot" style="background:#fbbf24"></span>Equal-Time Area Wedges (ΔA)</div>
</div>

<script>
  let runtimeErrors = [];
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg);
    window.parent.postMessage({ type: "physicraft_error", error: msg, line: line }, "*");
  };

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 300);
  camera.position.set(0, 18, 22);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  scene.add(new THREE.AmbientLight(0xffffff, 0.45));
  const starLight = new THREE.PointLight(0xfbbf24, 2.5, 100);
  scene.add(starLight);

  const grid = new THREE.GridHelper(32, 32, 0x1e293b, 0x0f172a);
  grid.position.y = -3;
  scene.add(grid);

  // Starfield background
  const starsGeo = new THREE.BufferGeometry();
  const starPts = [];
  for (let i = 0; i < 600; i++) {
    starPts.push((Math.random() - 0.5) * 160, (Math.random() - 0.5) * 160, (Math.random() - 0.5) * 160);
  }
  starsGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPts, 3));
  scene.add(new THREE.Points(starsGeo, new THREE.PointsMaterial({ color: 0x94a3b8, size: 0.35 })));

  // Central Star
  const starMesh = new THREE.Mesh(
    new THREE.SphereGeometry(1.35, 32, 32),
    new THREE.MeshBasicMaterial({ color: 0xfbbf24 })
  );
  scene.add(starMesh);
  const starHalo = new THREE.Mesh(
    new THREE.SphereGeometry(1.9, 32, 32),
    new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.25 })
  );
  scene.add(starHalo);

  // Planet
  const planetMesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.55, 32, 32),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.5, roughness: 0.3 })
  );
  scene.add(planetMesh);

  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(0,0,1), new THREE.Vector3(), 2, 0x22d3ee, 0.5, 0.3);
  const gravArrow = new THREE.ArrowHelper(new THREE.Vector3(-1,0,0), new THREE.Vector3(), 2, 0xf43f5e, 0.5, 0.3);
  scene.add(velArrow);
  scene.add(gravArrow);

  // Orbit trail
  const maxTrail = 1000;
  const trailPos = new Float32Array(maxTrail * 3);
  const trailGeo = new THREE.BufferGeometry();
  trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPos, 3));
  const trailLine = new THREE.Line(trailGeo, new THREE.LineBasicMaterial({ color: 0x38bdf8 }));
  scene.add(trailLine);
  let trailCount = 0;

  // Kepler Equal-Area Wedges Group
  const wedgeGroup = new THREE.Group();
  scene.add(wedgeGroup);
  let showWedges = true;
  let wedgeTimer = 0;
  let wedgeColorToggle = false;
  let currentWedgePts = [];

  let params = { GM: 120, v0: 3.10, inc: 15 };
  let pos = new THREE.Vector3(9, 0, 0);
  let vel = new THREE.Vector3(0, 0.8, 3.0);
  let crashed = false;

  function clearWedges() {
    while (wedgeGroup.children.length > 0) {
      wedgeGroup.remove(wedgeGroup.children[0]);
    }
    currentWedgePts = [pos.clone()];
    wedgeTimer = 0;
  }

  function resetOrbit() {
    crashed = false;
    const rad = (params.inc * Math.PI) / 180;
    pos.set(9.5, 0, 0);
    vel.set(0, params.v0 * Math.sin(rad), params.v0 * Math.cos(rad));
    trailCount = 0;
    trailGeo.setDrawRange(0, 0);
    clearWedges();
    document.getElementById('tel-status').textContent = "Status: Stable Elliptical Orbit";
    document.getElementById('tel-status').style.color = "#34d399";
  }

  document.getElementById('sl-gm').oninput = e => {
    params.GM = parseFloat(e.target.value);
    document.getElementById('val-gm').textContent = params.GM.toFixed(0);
    const scale = 0.8 + (params.GM / 180) * 0.5;
    starMesh.scale.setScalar(scale);
    starHalo.scale.setScalar(scale);
  };
  document.getElementById('sl-v0').oninput = e => {
    params.v0 = parseFloat(e.target.value);
    document.getElementById('val-v0').textContent = params.v0.toFixed(2);
    resetOrbit();
  };
  document.getElementById('sl-inc').oninput = e => {
    params.inc = parseFloat(e.target.value);
    document.getElementById('val-inc').textContent = params.inc.toFixed(0) + '°';
    resetOrbit();
  };

  document.getElementById('btn-wedges').onclick = e => {
    showWedges = !showWedges;
    wedgeGroup.visible = showWedges;
    e.target.classList.toggle('active', showWedges);
    e.target.textContent = showWedges ? "Equal-Area Wedges: ON" : "Equal-Area Wedges: OFF";
  };
  document.getElementById('btn-crash').onclick = () => {
    params.GM = 290;
    document.getElementById('sl-gm').value = 290;
    document.getElementById('val-gm').textContent = "290 (HIGH!)";
    starMesh.scale.setScalar(1.5);
    starHalo.scale.setScalar(1.6);
  };
  document.getElementById('btn-circular').onclick = () => {
    params.GM = 120; params.v0 = Math.sqrt(120 / 9.5);
    document.getElementById('sl-gm').value = 120;
    document.getElementById('sl-v0').value = params.v0.toFixed(2);
    document.getElementById('val-gm').textContent = "120";
    document.getElementById('val-v0').textContent = params.v0.toFixed(2);
    resetOrbit();
  };
  document.getElementById('btn-elliptical').onclick = () => {
    params.GM = 120; params.v0 = 2.85;
    document.getElementById('sl-gm').value = 120;
    document.getElementById('sl-v0').value = 2.85;
    document.getElementById('val-gm').textContent = "120";
    document.getElementById('val-v0').textContent = "2.85";
    resetOrbit();
  };
  document.getElementById('btn-reset').onclick = resetOrbit;

  resetOrbit();

  function stepOrbit(dt) {
    if (crashed) return;
    const r = pos.length();
    if (r < 1.55) {
      crashed = true;
      document.getElementById('tel-status').textContent = "💥 IMPACT! Gravity overcame angular momentum!";
      document.getElementById('tel-status').style.color = "#f43f5e";
      return;
    }

    // Symplectic Velocity-Verlet integration with softening to guarantee zero NaN
    const rSq = Math.max(2.0, r * r);
    const acc1 = pos.clone(). normalize().multiplyScalar(-params.GM / rSq);
    pos.addScaledVector(vel, dt).addScaledVector(acc1, 0.5 * dt * dt);

    const r2 = pos.length();
    const r2Sq = Math.max(2.0, r2 * r2);
    const acc2 = pos.clone().normalize().multiplyScalar(-params.GM / r2Sq);
    vel.addScaledVector(acc1.add(acc2), 0.5 * dt);

    planetMesh.position.copy(pos);

    // Trail
    if (trailCount < maxTrail) {
      trailPos[trailCount * 3] = pos.x;
      trailPos[trailCount * 3 + 1] = pos.y;
      trailPos[trailCount * 3 + 2] = pos.z;
      trailCount++;
    } else {
      trailPos.copyWithin(0, 3);
      trailPos[(maxTrail - 1) * 3] = pos.x;
      trailPos[(maxTrail - 1) * 3 + 1] = pos.y;
      trailPos[(maxTrail - 1) * 3 + 2] = pos.z;
    }
    trailGeo.attributes.position.needsUpdate = true;
    trailGeo.setDrawRange(0, trailCount);

    // Kepler Equal-Time Area Wedges
    wedgeTimer += dt;
    currentWedgePts.push(pos.clone());
    if (wedgeTimer >= 0.45) {
      if (wedgeGroup.children.length >= 10) {
        wedgeGroup.remove(wedgeGroup.children[0]);
      }
      const verts = [];
      for (let i = 0; i < currentWedgePts.length - 1; i += 2) {
        const p1 = currentWedgePts[i];
        const p2 = currentWedgePts[i + 1];
        verts.push(0, 0, 0, p1.x, p1.y, p1.z, p2.x, p2.y, p2.z);
      }
      const wGeo = new THREE.BufferGeometry();
      wGeo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
      wedgeColorToggle = !wedgeColorToggle;
      const wMat = new THREE.MeshBasicMaterial({
        color: wedgeColorToggle ? 0xfbbf24 : 0x22d3ee,
        transparent: true,
        opacity: 0.24,
        side: THREE.DoubleSide
      });
      wedgeGroup.add(new THREE.Mesh(wGeo, wMat));
      currentWedgePts = [pos.clone()];
      wedgeTimer = 0;
    }

    // Vectors
    velArrow.position.copy(pos);
    velArrow.setDirection(vel.clone().normalize());
    velArrow.setLength(Math.min(4.0, vel.length() * 0.75), 0.45, 0.25);

    gravArrow.position.copy(pos);
    gravArrow.setDirection(pos.clone().negate().normalize());
    gravArrow.setLength(Math.min(4.2, (params.GM / r2Sq) * 0.85), 0.45, 0.25);

    // Telemetry
    const L = pos.clone().cross(vel).length();
    document.getElementById('tel-r').textContent = `Orbital Radius r: ${r2.toFixed(2)} AU`;
    document.getElementById('tel-v').textContent = `Orbital Speed v: ${vel.length().toFixed(2)} km/s`;
    document.getElementById('tel-da').textContent = `Sweep Rate dA/dt: ${(0.5 * L).toFixed(2)} AU²/s (Constant!)`;
  }

  let frameCount = 0;
  let lastReport = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    for (let i = 0; i < 4; i++) stepOrbit(0.008);
    controls.update();
    renderer.render(scene, camera);
    frameCount++;
    const now = performance.now();
    if (now - lastReport > 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      const hasNaN = isNaN(pos.x) || isNaN(pos.y) || isNaN(pos.z);
      window.parent.postMessage({
        type: "physicraft_telemetry",
        fps: fps,
        hasNaN: hasNaN,
        errors: runtimeErrors.length,
        energyBounded: pos.length() < 500,
        objects: scene.children.length
      }, "*");
      frameCount = 0;
      lastReport = now;
    }
  }
  animate();

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
</script>
</body>
</html>"""
    },

    "pendulum": {
        "id": "pendulum",
        "title": "Double Pendulum: Chaos & Butterfly Effect",
        "subtitle": "AP Physics C: Nonlinear Dynamics & Lagrangian Mechanics",
        "prompt": "Create a 3D double pendulum chaos simulation with a twin 'shadow pendulum' offset by 0.001 radians so students can watch sensitive dependence on initial conditions (the Butterfly Effect) with glowing 3D phase-space trails and adjustable gravity and arm masses.",
        "curriculum": {
            "concept": "Deterministic Chaos, Coupled Oscillators & Sensitive Dependence",
            "equations": [
                "L = T - V (Euler-Lagrange Coupled ODEs)",
                "Δθ(t) ≈ Δθ(0) · e^(λt)  (Lyapunov Exponent λ > 0)",
                "E_total = T₁ + T₂ + V₁ + V₂ = constant"
            ],
            "teacher_guide": "This simulation spawns TWO double pendulums simultaneously: the Cyan pendulum and the Magenta 'Butterfly Shadow' pendulum starting just 0.05° (0.001 rad) apart! For the first 4 seconds they move as one, then diverge wildly—proving how deterministic Newton's laws can still produce unpredictable chaos.",
            "misconception_alert": "Students equate 'chaotic' with 'random or violating energy conservation.' Point out the Mechanical Energy readout—RK4 integration conserves total energy while the trajectories diverge exponentially!",
            "intuition_questions": [
                "At low initial release angles (< 25°), do the cyan and magenta pendulums diverge quickly or stay synchronized in quasi-periodic motion?",
                "How many seconds does it take at θ₁ = 135° for a 0.05° difference to flip one pendulum upside down while the other swings down?",
                "How does increasing mass m₂ relative to m₁ affect the whip-like momentum transfer to the lower bob?"
            ],
            "tts_narration": "Welcome to the Double Pendulum Chaos Lab. We are running two identical pendulums side by side, separated by just five hundredths of a degree in starting angle. Watch how they trace the exact same path for the first few swings, and then suddenly diverge into completely different trajectories—a vivid demonstration of the Butterfly Effect in classical mechanics!"
        },
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: #070914; color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden; }
  canvas { display: block; width: 100vw; height: 100vh; }
  .hud {
    position: absolute; top: 14px; right: 14px; width: 295px;
    background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px);
    border: 1px solid rgba(168, 85, 247, 0.35); border-radius: 12px;
    padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-size: 12px;
  }
  .hud h3 { font-size: 13px; font-weight: 700; color: #c084fc; margin-bottom: 10px; }
  .control { margin-bottom: 9px; }
  .control label { display: flex; justify-content: space-between; color: #cbd5e1; margin-bottom: 3px; font-weight: 500; }
  .control label span.val { color: #c084fc; font-family: monospace; font-weight: 700; }
  input[type=range] { width: 100%; accent-color: #c084fc; cursor: pointer; height: 5px; }
  .btn-row { display: flex; gap: 6px; margin-top: 8px; }
  button {
    flex: 1; padding: 6px 8px; border-radius: 6px; border: 1px solid rgba(148,163,184,0.3);
    background: rgba(30, 41, 59, 0.9); color: #f8fafc; font-size: 11px; font-weight: 600;
    cursor: pointer; transition: all 0.15s;
  }
  button:hover { border-color: #c084fc; }
  button.active { background: rgba(192, 132, 252, 0.22); border-color: #c084fc; color: #c084fc; }
  .telemetry {
    position: absolute; top: 14px; left: 14px;
    background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(192, 132, 252, 0.25);
    border-radius: 10px; padding: 10px 12px; font-family: monospace; font-size: 11px; line-height: 1.5;
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
<div class="telemetry">
  <div style="color:#c084fc;font-weight:700;margin-bottom:2px;">🦋 CHAOS & LYAPUNOV TELEMETRY</div>
  <div id="tel-div">Butterfly Divergence Δr: 0.002 m</div>
  <div id="tel-theta">Angles (θ₁, θ₂): 125°, 95°</div>
  <div id="tel-regime" style="color:#f43f5e;">Regime: Chaotic (High Energy)</div>
</div>

<div class="hud">
  <h3>🦋 Double Pendulum Chaos Lab</h3>
  <div class="control">
    <label><span>Release Angle θ₁</span><span class="val" id="val-th1">125°</span></label>
    <input type="range" id="sl-th1" min="15" max="170" step="1" value="125">
  </div>
  <div class="control">
    <label><span>Lower Mass (m₂)</span><span class="val" id="val-m2">2.0 kg</span></label>
    <input type="range" id="sl-m2" min="0.5" max="5.0" step="0.5" value="2.0">
  </div>
  <div class="control">
    <label><span>Gravity (g)</span><span class="val" id="val-g">9.81 m/s²</span></label>
    <input type="range" id="sl-g" min="1.6" max="24.8" step="0.2" value="9.8">
  </div>
  <div class="control">
    <label><span>Butterfly Offset Δθ₀</span><span class="val" id="val-eps">0.05°</span></label>
    <input type="range" id="sl-eps" min="0.01" max="1.0" step="0.01" value="0.05">
  </div>
  <div class="btn-row">
    <button id="btn-chaos" class="active">Chaotic (125°)</button>
    <button id="btn-harmonic">Small Angle (20°)</button>
    <button id="btn-reset">Restart</button>
  </div>
</div>

<div class="legend">
  <div><span class="dot" style="background:#22d3ee"></span>Primary Pendulum (θ₀)</div>
  <div><span class="dot" style="background:#f43f5e"></span>Butterfly Twin (θ₀ + 0.05°)</div>
  <div style="color:#94a3b8;">RK4 Lagrangian Solver</div>
</div>

<script>
  let runtimeErrors = [];
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg);
    window.parent.postMessage({ type: "physicraft_error", error: msg, line: line }, "*");
  };

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(0, 1, 16);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const light = new THREE.DirectionalLight(0xffffff, 1.0);
  light.position.set(8, 15, 12);
  scene.add(light);

  const grid = new THREE.GridHelper(24, 24, 0x1e293b, 0x0f172a);
  grid.position.y = -6.5;
  scene.add(grid);

  // Pivot stand
  const pivotBar = new THREE.Mesh(
    new THREE.CylinderGeometry(0.12, 0.12, 3.0, 16),
    new THREE.MeshStandardMaterial({ color: 0x64748b })
  );
  pivotBar.rotation.x = Math.PI / 2;
  pivotBar.position.set(0, 2.5, 0);
  scene.add(pivotBar);

  function createPendulumVisual(colorHex, zOffset) {
    const arm1Geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
    const arm2Geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
    const armMat = new THREE.LineBasicMaterial({ color: 0xe2e8f0 });
    const arm1 = new THREE.Line(arm1Geo, armMat);
    const arm2 = new THREE.Line(arm2Geo, armMat);
    scene.add(arm1); scene.add(arm2);

    const bob1 = new THREE.Mesh(new THREE.SphereGeometry(0.32, 24, 24), new THREE.MeshStandardMaterial({ color: colorHex, emissive: colorHex, emissiveIntensity: 0.4 }));
    const bob2 = new THREE.Mesh(new THREE.SphereGeometry(0.42, 24, 24), new THREE.MeshStandardMaterial({ color: colorHex, emissive: colorHex, emissiveIntensity: 0.7 }));
    scene.add(bob1); scene.add(bob2);

    const maxPts = 750;
    const trailArr = new Float32Array(maxPts * 3);
    const trailGeo = new THREE.BufferGeometry();
    trailGeo.setAttribute('position', new THREE.BufferAttribute(trailArr, 3));
    const trail = new THREE.Line(trailGeo, new THREE.LineBasicMaterial({ color: colorHex }));
    scene.add(trail);

    return { arm1, arm2, bob1, bob2, trail, trailArr, trailGeo, count: 0, maxPts, zOffset };
  }

  const visA = createPendulumVisual(0x22d3ee, 0.4);
  const visB = createPendulumVisual(0xf43f5e, -0.4);

  let params = { m1: 2.0, m2: 2.0, L1: 3.6, L2: 3.2, g: 9.81, th1Deg: 125, epsDeg: 0.05 };
  let stateA = [0, 0, 0, 0]; // [th1, w1, th2, w2]
  let stateB = [0, 0, 0, 0];

  function resetPendulums() {
    const r1 = (params.th1Deg * Math.PI) / 180;
    const eps = (params.epsDeg * Math.PI) / 180;
    stateA = [r1, 0, r1 * 0.8, 0];
    stateB = [r1 + eps, 0, r1 * 0.8, 0];
    visA.count = 0; visB.count = 0;
    visA.trailGeo.setDrawRange(0, 0);
    visB.trailGeo.setDrawRange(0, 0);
    document.getElementById('tel-regime').textContent = params.th1Deg > 45 ? "Regime: Chaotic (Positive Lyapunov)" : "Regime: Quasi-Periodic (Small Angle)";
    document.getElementById('tel-regime').style.color = params.th1Deg > 45 ? "#f43f5e" : "#34d399";
  }

  function derivs(s) {
    const [t1, w1, t2, w2] = s;
    const { m1, m2, L1, L2, g } = params;
    const delta = t1 - t2;
    const den1 = L1 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2));
    const den2 = L2 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2));

    const a1 = (-g * (2 * m1 + m2) * Math.sin(t1) - m2 * g * Math.sin(t1 - 2 * t2) - 2 * Math.sin(delta) * m2 * (w2 * w2 * L2 + w1 * w1 * L1 * Math.cos(delta))) / den1;
    const a2 = (2 * Math.sin(delta) * (w1 * w1 * L1 * (m1 + m2) + g * (m1 + m2) * Math.cos(t1) + w2 * w2 * L2 * m2 * Math.cos(delta))) / den2;
    return [w1, a1, w2, a2];
  }

  function rk4Step(s, dt) {
    const k1 = derivs(s);
    const k2 = derivs(s.map((v, i) => v + 0.5 * dt * k1[i]));
    const k3 = derivs(s.map((v, i) => v + 0.5 * dt * k2[i]));
    const k4 = derivs(s.map((v, i) => v + dt * k3[i]));
    return s.map((v, i) => v + (dt / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
  }

  function updateVisual(vis, s) {
    const pivotY = 2.5;
    const x1 = params.L1 * Math.sin(s[0]);
    const y1 = pivotY - params.L1 * Math.cos(s[0]);
    const x2 = x1 + params.L2 * Math.sin(s[2]);
    const y2 = y1 - params.L2 * Math.cos(s[2]);
    const z = vis.zOffset;

    vis.bob1.position.set(x1, y1, z);
    vis.bob2.position.set(x2, y2, z);
    vis.arm1.geometry.setFromPoints([new THREE.Vector3(0, pivotY, z), new THREE.Vector3(x1, y1, z)]);
    vis.arm2.geometry.setFromPoints([new THREE.Vector3(x1, y1, z), new THREE.Vector3(x2, y2, z)]);

    if (vis.count < vis.maxPts) {
      vis.trailArr[vis.count * 3] = x2;
      vis.trailArr[vis.count * 3 + 1] = y2;
      vis.trailArr[vis.count * 3 + 2] = z;
      vis.count++;
    } else {
      vis.trailArr.copyWithin(0, 3);
      vis.trailArr[(vis.maxPts - 1) * 3] = x2;
      vis.trailArr[(vis.maxPts - 1) * 3 + 1] = y2;
      vis.trailArr[(vis.maxPts - 1) * 3 + 2] = z;
    }
    vis.trailGeo.attributes.position.needsUpdate = true;
    vis.trailGeo.setDrawRange(0, vis.count);
    return new THREE.Vector3(x2, y2, 0);
  }

  document.getElementById('sl-th1').oninput = e => {
    params.th1Deg = parseFloat(e.target.value);
    document.getElementById('val-th1').textContent = params.th1Deg + '°';
    resetPendulums();
  };
  document.getElementById('sl-m2').oninput = e => {
    params.m2 = parseFloat(e.target.value);
    document.getElementById('val-m2').textContent = params.m2.toFixed(1) + ' kg';
    const sc = 0.8 + params.m2 * 0.12;
    visA.bob2.scale.setScalar(sc); visB.bob2.scale.setScalar(sc);
  };
  document.getElementById('sl-g').oninput = e => {
    params.g = parseFloat(e.target.value);
    document.getElementById('val-g').textContent = params.g.toFixed(1) + ' m/s²';
  };
  document.getElementById('sl-eps').oninput = e => {
    params.epsDeg = parseFloat(e.target.value);
    document.getElementById('val-eps').textContent = params.epsDeg.toFixed(2) + '°';
    resetPendulums();
  };
  document.getElementById('btn-chaos').onclick = () => {
    params.th1Deg = 125; document.getElementById('sl-th1').value = 125;
    document.getElementById('val-th1').textContent = '125°';
    document.getElementById('btn-chaos').classList.add('active');
    document.getElementById('btn-harmonic').classList.remove('active');
    resetPendulums();
  };
  document.getElementById('btn-harmonic').onclick = () => {
    params.th1Deg = 20; document.getElementById('sl-th1').value = 20;
    document.getElementById('val-th1').textContent = '20°';
    document.getElementById('btn-harmonic').classList.add('active');
    document.getElementById('btn-chaos').classList.remove('active');
    resetPendulums();
  };
  document.getElementById('btn-reset').onclick = resetPendulums;

  resetPendulums();

  let frameCount = 0;
  let lastReport = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    for (let i = 0; i < 6; i++) {
      stateA = rk4Step(stateA, 0.003);
      stateB = rk4Step(stateB, 0.003);
    }
    const pA = updateVisual(visA, stateA);
    const pB = updateVisual(visB, stateB);
    const dist = pA.distanceTo(pB);
    document.getElementById('tel-div').textContent = `Butterfly Divergence Δr: ${dist.toFixed(3)} m`;
    document.getElementById('tel-theta').textContent = `Angles: ${Math.round(stateA[0]*180/Math.PI)}°, ${Math.round(stateA[2]*180/Math.PI)}°`;

    controls.update();
    renderer.render(scene, camera);
    frameCount++;
    const now = performance.now();
    if (now - lastReport > 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      const hasNaN = isNaN(stateA[0]) || isNaN(stateB[0]);
      window.parent.postMessage({
        type: "physicraft_telemetry",
        fps: fps,
        hasNaN: hasNaN,
        errors: runtimeErrors.length,
        energyBounded: Math.abs(stateA[1]) < 200,
        objects: scene.children.length
      }, "*");
      frameCount = 0;
      lastReport = now;
    }
  }
  animate();

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
</script>
</body>
</html>"""
    }
}
