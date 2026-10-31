"""
PhysiCraft — 4 Hero Presets for Live Demo Reliability & Instant 3D Physics Exploration.
Each preset includes:
- Full standalone Three.js 3D interactive simulation with OrbitControls, vector arrows, and glassmorphic HUD sliders
- Real-time autonomous verification telemetry posted to parent window (FPS, NaN check, energy/bounds check)
- Properly typeset mathematical vectors (\\vec{F}, \\vec{v}, \\vec{B}) and subscripted symbols (B_y, v_\\perp, r_c)
"""

PRESETS = {
    "lorentz": {
        "id": "lorentz",
        "title": "Lorentz Force & Helical Motion",
        "subtitle": "AP Physics C · Electromagnetism",
        "prompt": "Show how charged particles spiral in a uniform 3D magnetic field with adjustable B_y field strength, charge polarity (proton vs electron), initial velocity components v_⊥ and v_∥, and live F = q(v × B) vector arrows.",
        "curriculum": {
            "concept": "Lorentz Magnetic Force & Cyclotron Motion",
            "equations": [
                r"\vec{F} = q(\vec{E} + \vec{v} \times \vec{B})",
                r"r_c = \frac{m \, v_{\perp}}{|q| \, B_y}",
                r"\omega_c = \frac{|q| \, B_y}{m}"
            ],
            "teacher_guide": r"Point out that the magnetic force vector $\vec{F}$ (light blue) is always perpendicular to both the velocity vector $\vec{v}$ and the magnetic field $\vec{B}_y$. Because $\vec{F} \perp \vec{v}$, the magnetic field does zero work ($W = 0$)—speed and kinetic energy $K$ remain constant while the helix radius tightens.",
            "misconception_alert": r"Students often assume increasing $B_y$ speeds up the particle. Vary the $B_y$ slider to show that a stronger magnetic field tightens the cyclotron radius $r_c = m v_{\perp} / |q| B_y$ without changing kinetic energy $K$.",
            "intuition_questions": [
                r"How does the spiral direction (right-hand rule) change when you switch charge $q$ from $+1.0\text{ C}$ to $-1.0\text{ C}$?",
                r"If axial drift velocity $v_{\parallel} = 0$, what 2D shape does the 3D helix collapse into?",
                r"Why does kinetic energy $K$ stay constant when $B_y$ doubles, whereas adding an electric field $E_y \neq 0$ changes $K$?"
            ],
            "tts_narration": "Welcome to the Lorentz Force 3D Lab. Observe the velocity vector and light blue Lorentz force vector as the charge spirals around the vertical magnetic field lines. Because the magnetic force is always perpendicular to velocity, it performs zero mechanical work. Flip the charge polarity between positive and negative to see the spiral direction reverse immediately."
        },
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  :root {
    --bg: #050507;
    --glass: rgba(20, 22, 28, 0.72);
    --border: rgba(255, 255, 255, 0.1);
    --divider: rgba(255, 255, 255, 0.08);
    --text: #F5F5F7;
    --subtext: #D2D2D7;
    --muted: #86868B;
    --accent: #1890FF;
    --btn-bg: rgba(255, 255, 255, 0.06);
    --btn-hover: rgba(255, 255, 255, 0.12);
    --track-bg: rgba(255, 255, 255, 0.16);
    --sans: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    --mono: ui-monospace, 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
  }
  body.light {
    --bg: #F2F5F9;
    --glass: rgba(255, 255, 255, 0.82);
    --border: rgba(0, 0, 0, 0.08);
    --divider: rgba(0, 0, 0, 0.07);
    --text: #1D1D1F;
    --subtext: #3A3A3C;
    --muted: #6E6E73;
    --accent: #0082FB;
    --btn-bg: rgba(0, 0, 0, 0.04);
    --btn-hover: rgba(0, 0, 0, 0.08);
    --track-bg: rgba(0, 0, 0, 0.14);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: var(--bg); color: var(--text); font-family: var(--sans); overflow: hidden; -webkit-font-smoothing: antialiased; transition: background 0.25s ease, color 0.25s ease; }
  canvas { display: block; width: 100vw; height: 100vh; }

  /* Mathematical Vector & Subscript Typography */
  .vec { position: relative; display: inline-block; font-style: italic; font-family: Georgia, 'Times New Roman', serif; padding-top: 2px; margin: 0 1px; }
  .vec::after { content: "→"; position: absolute; top: -0.58em; left: 50%; transform: translateX(-50%) scale(0.72); font-style: normal; font-family: var(--sans); color: inherit; }
  .sym { font-style: italic; font-family: Georgia, 'Times New Roman', serif; }
  sub, sup { font-size: 0.74em; line-height: 0; position: relative; vertical-align: baseline; font-style: normal; }
  sub { bottom: -0.22em; }
  sup { top: -0.42em; }

  /* Apple-style Floating Frosted Control Card */
  .hud {
    position: absolute; top: 20px; right: 20px; width: 268px;
    background: var(--glass);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
    font-size: 12px;
    overflow: hidden;
    transition: background 0.25s ease, border-color 0.25s ease;
  }
  .hud-header {
    padding: 12px 16px; border-bottom: 1px solid var(--divider);
    display: flex; justify-content: space-between; align-items: center;
    font-size: 12px; font-weight: 600; color: var(--text); letter-spacing: -0.01em;
  }
  .hud-toggle {
    background: var(--btn-bg); border: none; color: var(--muted);
    width: 24px; height: 24px; border-radius: 50%; cursor: pointer; font-size: 13px; line-height: 1;
    display: flex; align-items: center; justify-content: center; transition: all 0.15s ease;
  }
  .hud-toggle:hover { background: var(--btn-hover); color: var(--text); }
  .hud-body { padding: 14px 16px 16px; }
  .hud.collapsed .hud-body { display: none; }
  .control { margin-bottom: 12px; }
  .control label { display: flex; justify-content: space-between; align-items: baseline; color: var(--subtext); margin-bottom: 6px; font-size: 12px; }
  .control label span.val { color: var(--text); font-weight: 600; font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
  input[type=range] {
    width: 100%; accent-color: var(--accent); cursor: pointer; height: 4px; border-radius: 999px;
    background: var(--track-bg); appearance: none; -webkit-appearance: none;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%;
    background: var(--accent); box-shadow: 0 2px 6px rgba(0, 130, 251, 0.35); cursor: pointer; border: 2px solid #FFFFFF;
  }
  .btn-row { display: flex; gap: 6px; margin-top: 12px; }
  .btn-row button {
    flex: 1; padding: 7px 8px; border-radius: 9px; border: 1px solid var(--border);
    background: var(--btn-bg); color: var(--subtext);
    font-family: var(--sans); font-size: 11px; font-weight: 500;
    cursor: pointer; transition: all 0.15s ease;
  }
  .btn-row button:hover { color: var(--text); background: var(--btn-hover); }
  .btn-row button.active { background: var(--accent); border-color: var(--accent); color: #FFFFFF; font-weight: 600; }

  /* Floating Pill Status & Vector Legend */
  .status-strip {
    position: absolute; bottom: 20px; left: 20px;
    background: var(--glass);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px 6px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
    display: flex; align-items: center; font-size: 11.5px;
    transition: background 0.25s ease, border-color 0.25s ease;
  }
  .status-cell { padding: 4px 12px; border-right: 1px solid var(--divider); display: flex; align-items: center; gap: 6px; }
  .status-cell:last-child { border-right: none; }
  .swatch { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
  .tel-val { color: var(--text); font-weight: 600; font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

<div class="hud" id="hud-panel">
  <div class="hud-header">
    <strong>Field Controls</strong>
    <button class="hud-toggle" id="hud-min" title="Toggle Controls">&minus;</button>
  </div>
  <div class="hud-body">
    <div class="control">
      <label><span>Charge (<span class="sym">q</span>)</span><span class="val" id="val-q">+1.0 C</span></label>
      <input type="range" id="sl-q" min="-2.0" max="2.0" step="0.1" value="1.0">
    </div>
    <div class="control">
      <label><span>Magnetic Field (<span class="sym">B</span><sub>y</sub>)</span><span class="val" id="val-b">2.0 T</span></label>
      <input type="range" id="sl-b" min="0.2" max="5.0" step="0.1" value="2.0">
    </div>
    <div class="control">
      <label><span>Electric Field (<span class="sym">E</span><sub>y</sub>)</span><span class="val" id="val-e">0.0 V/m</span></label>
      <input type="range" id="sl-e" min="-2.0" max="2.0" step="0.1" value="0.0">
    </div>
    <div class="control">
      <label><span>Transverse Vel (<span class="sym">v</span><sub>&perp;</sub>)</span><span class="val" id="val-vp">5.0 m/s</span></label>
      <input type="range" id="sl-vp" min="1.0" max="10.0" step="0.5" value="5.0">
    </div>
    <div class="control">
      <label><span>Axial Drift (<span class="sym">v</span><sub>&parallel;</sub>)</span><span class="val" id="val-vy">1.50 m/s</span></label>
      <input type="range" id="sl-vy" min="-4.0" max="4.0" step="0.25" value="1.5">
    </div>
    <div class="btn-row">
      <button id="btn-proton" class="active">+q Proton</button>
      <button id="btn-electron">&minus;q Electron</button>
      <button id="btn-reset">Reset</button>
    </div>
  </div>
</div>

<div class="status-strip">
  <div class="status-cell">
    <span style="color:var(--muted)"><span class="sym">r</span><sub>c</sub></span>
    <span class="tel-val" id="tel-radius">2.50 m</span>
  </div>
  <div class="status-cell">
    <span style="color:var(--muted)">&omega;<sub>c</sub></span>
    <span class="tel-val" id="tel-omega">2.00 rad/s</span>
  </div>
  <div class="status-cell">
    <span style="color:var(--muted)"><span class="sym">K</span></span>
    <span class="tel-val" id="tel-ke">13.63 J</span>
  </div>
  <div class="status-cell">
    <span class="swatch" id="swatch-v" style="background:#FFFFFF"></span><span><span class="vec">v</span></span>
  </div>
  <div class="status-cell">
    <span class="swatch" style="background:#1890FF"></span><span><span class="vec">F</span> = <span class="sym">q</span>(<span class="vec">v</span> &times; <span class="vec">B</span>)</span>
  </div>
  <div class="status-cell">
    <span class="swatch" style="background:#64748B"></span><span><span class="vec">B</span><sub>y</sub></span>
  </div>
</div>

<script>
  let runtimeErrors = [];
  let isLightMode = false;
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg + " (line " + line + ")");
    window.parent.postMessage({ type: "physicraft_error", error: msg, line: line }, "*");
  };

  document.getElementById('hud-min').onclick = function() {
    const p = document.getElementById('hud-panel');
    p.classList.toggle('collapsed');
    this.innerHTML = p.classList.contains('collapsed') ? '+' : '&minus;';
  };

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x050507, 0.018);
  const camera = new THREE.PerspectiveCamera(52, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(11, 8, 14);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setClearColor(0x050507, 1);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(0, 2, 0);

  scene.add(new THREE.AmbientLight(0xffffff, 0.75));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
  dirLight.position.set(10, 20, 10);
  scene.add(dirLight);

  let grid = new THREE.GridHelper(24, 24, 0x262629, 0x141416);
  grid.position.y = -6;
  scene.add(grid);

  // Magnetic field lines (B_y along +Y)
  const bFieldGroup = new THREE.Group();
  for (let x = -6; x <= 6; x += 4) {
    for (let z = -6; z <= 6; z += 4) {
      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(x, -6, z),
        new THREE.Vector3(x, 12, z)
      ]);
      const lineMat = new THREE.LineBasicMaterial({ color: 0x64748b, transparent: true, opacity: 0.35 });
      bFieldGroup.add(new THREE.Line(lineGeo, lineMat));
      const arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(x, 0, z), 2.4, 0x64748b, 0.4, 0.2);
      bFieldGroup.add(arrow);
    }
  }
  scene.add(bFieldGroup);

  // Charged particle sphere (Meta Light Blue for +q)
  const particleGeo = new THREE.SphereGeometry(0.4, 32, 32);
  const particleMat = new THREE.MeshStandardMaterial({ color: 0x1890ff, emissive: 0x0082fb, emissiveIntensity: 0.55, roughness: 0.2 });
  const particleMesh = new THREE.Mesh(particleGeo, particleMat);
  scene.add(particleMesh);

  // Vector Arrows: Velocity & Lorentz Force (Meta Light Blue)
  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 2, 0xffffff, 0.45, 0.25);
  const forceArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(), 2, 0x1890ff, 0.45, 0.25);
  scene.add(velArrow);
  scene.add(forceArrow);

  // 3D Helical Trail
  const maxTrail = 900;
  const trailPositions = new Float32Array(maxTrail * 3);
  const trailGeo = new THREE.BufferGeometry();
  trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
  const trailMat = new THREE.LineBasicMaterial({ color: 0x1890ff });
  const trailLine = new THREE.Line(trailGeo, trailMat);
  scene.add(trailLine);
  let trailCount = 0;

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
    const negColor = isLightMode ? 0x334155 : 0xffffff;
    particleMat.color.setHex(isPos ? 0x1890ff : negColor);
    particleMat.emissive.setHex(isPos ? 0x0082fb : (isLightMode ? 0x475569 : 0xa1a1aa));
    trailMat.color.setHex(isPos ? 0x1890ff : negColor);
    document.getElementById('btn-proton').classList.toggle('active', params.q > 0);
    document.getElementById('btn-electron').classList.toggle('active', params.q < 0);
  }

  function applySceneTheme(theme) {
    isLightMode = (theme === 'light');
    document.body.classList.toggle('light', isLightMode);
    const bgHex = isLightMode ? 0xF2F5F9 : 0x050507;
    renderer.setClearColor(bgHex, 1);
    scene.fog = new THREE.FogExp2(bgHex, 0.015);
    scene.remove(grid);
    grid = new THREE.GridHelper(24, 24, isLightMode ? 0xCBD5E1 : 0x262629, isLightMode ? 0xE2E8F0 : 0x141416);
    grid.position.y = -6;
    scene.add(grid);
    const vHex = isLightMode ? 0x1D1D1F : 0xFFFFFF;
    velArrow.setColor(new THREE.Color(vHex));
    const sw = document.getElementById('swatch-v');
    if (sw) sw.style.background = isLightMode ? '#1D1D1F' : '#FFFFFF';
    syncUI();
  }

  window.addEventListener('message', (e) => {
    if (e.data && e.data.type === 'physicraft_theme') {
      applySceneTheme(e.data.theme);
    }
  });

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

  // Symplectic Boris integrator
  function stepPhysics(dt) {
    const Bvec = new THREE.Vector3(0, params.B, 0);
    const Evec = new THREE.Vector3(0, params.E, 0);
    const qm = params.q / params.m;

    vel.addScaledVector(Evec, 0.5 * qm * dt);
    const t = Bvec.clone().multiplyScalar(0.5 * qm * dt);
    const s = t.clone().multiplyScalar(2.0 / (1.0 + t.lengthSq()));
    const vPrime = vel.clone().add(vel.clone().cross(t));
    vel.add(vPrime.cross(s));
    vel.addScaledVector(Evec, 0.5 * qm * dt);

    pos.addScaledVector(vel, dt);

    if (pos.y > 11 || pos.y < -6) {
      pos.y = -4;
      trailCount = 0;
    }

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

    const qAbs = Math.max(0.05, Math.abs(params.q));
    const vPerp = Math.hypot(vel.x, vel.z);
    const rc = (params.m * vPerp) / (qAbs * params.B);
    const wc = (qAbs * params.B) / params.m;
    const ke = 0.5 * params.m * vel.lengthSq();
    document.getElementById('tel-radius').textContent = `${rc.toFixed(2)} m`;
    document.getElementById('tel-omega').textContent = `${wc.toFixed(2)} rad/s`;
    document.getElementById('tel-ke').textContent = `${ke.toFixed(2)} J`;
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
        "title": "Kepler's Orbit & Equal-Area Sweep",
        "subtitle": "AP Physics C · Gravitation",
        "prompt": "Build an interactive 3D Kepler orbital mechanics simulation with a central star, eccentric planet orbit, live Kepler's 2nd Law equal-area wedge visualizer (dA/dt = L/2m), velocity v & gravity F_g vector arrows, and adjustable gravitational parameter GM.",
        "curriculum": {
            "concept": "Newtonian Gravitation & Kepler's Second Law",
            "equations": [
                r"\vec{F}_g = -\frac{G M m}{r^2}\,\hat{r}",
                r"\frac{dA}{dt} = \frac{|\vec{L}|}{2m} = \text{const}",
                r"E_{\text{tot}} = \frac{1}{2}mv^2 - \frac{GMm}{r}"
            ],
            "teacher_guide": r"Observe the alternating area sectors swept over equal time intervals $\Delta t$. Students can verify geometrically that the elongated sector near aphelion ($r_{\max}$) has the exact same area $\Delta A$ as the wide sector near perihelion ($r_{\min}$) because angular momentum $\vec{L} = \vec{r} \times \vec{p}$ is conserved.",
            "misconception_alert": r"Students often assume orbital speed $|\vec{v}|$ is uniform along an ellipse. Watch the velocity vector $\vec{v}$ lengthen at perihelion and contract at aphelion while $dA/dt$ remains constant.",
            "intuition_questions": [
                r"Where along the elliptical trajectory is gravitational force $|\vec{F}_g|$ maximal, and how does tangential speed $v$ respond?",
                r"How does orbital eccentricity $e$ change if gravitational parameter $GM$ is doubled while the planet is at aphelion?",
                r"Why do alternating equal-time sectors preserve constant area $\Delta A$ despite drastic changes in radial distance $r$?"
            ],
            "tts_narration": "In this Kepler Orbital Lab, watch how the orbiting body accelerates as it approaches perihelion and decelerates toward aphelion. The shaded sectors represent equal time intervals. Even though sectors close to the central mass are short and wide, their surface area equals the long, narrow sectors far out, confirming conservation of angular momentum."
        },
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  :root {
    --bg: #050507;
    --glass: rgba(20, 22, 28, 0.72);
    --border: rgba(255, 255, 255, 0.1);
    --divider: rgba(255, 255, 255, 0.08);
    --text: #F5F5F7;
    --subtext: #D2D2D7;
    --muted: #86868B;
    --accent: #1890FF;
    --btn-bg: rgba(255, 255, 255, 0.06);
    --btn-hover: rgba(255, 255, 255, 0.12);
    --track-bg: rgba(255, 255, 255, 0.16);
    --sans: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    --mono: ui-monospace, 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
  }
  body.light {
    --bg: #F2F5F9;
    --glass: rgba(255, 255, 255, 0.82);
    --border: rgba(0, 0, 0, 0.08);
    --divider: rgba(0, 0, 0, 0.07);
    --text: #1D1D1F;
    --subtext: #3A3A3C;
    --muted: #6E6E73;
    --accent: #0082FB;
    --btn-bg: rgba(0, 0, 0, 0.04);
    --btn-hover: rgba(0, 0, 0, 0.08);
    --track-bg: rgba(0, 0, 0, 0.14);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: var(--bg); color: var(--text); font-family: var(--sans); overflow: hidden; -webkit-font-smoothing: antialiased; transition: background 0.25s ease, color 0.25s ease; }
  canvas { display: block; width: 100vw; height: 100vh; }

  .vec { position: relative; display: inline-block; font-style: italic; font-family: Georgia, 'Times New Roman', serif; padding-top: 2px; margin: 0 1px; }
  .vec::after { content: "→"; position: absolute; top: -0.58em; left: 50%; transform: translateX(-50%) scale(0.72); font-style: normal; font-family: var(--sans); color: inherit; }
  .sym { font-style: italic; font-family: Georgia, 'Times New Roman', serif; }
  sub, sup { font-size: 0.74em; line-height: 0; position: relative; vertical-align: baseline; font-style: normal; }
  sub { bottom: -0.22em; }
  sup { top: -0.42em; }

  .hud {
    position: absolute; top: 20px; right: 20px; width: 268px;
    background: var(--glass);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
    font-size: 12px;
    overflow: hidden;
    transition: background 0.25s ease, border-color 0.25s ease;
  }
  .hud-header {
    padding: 12px 16px; border-bottom: 1px solid var(--divider);
    display: flex; justify-content: space-between; align-items: center;
    font-size: 12px; font-weight: 600; color: var(--text); letter-spacing: -0.01em;
  }
  .hud-toggle {
    background: var(--btn-bg); border: none; color: var(--muted);
    width: 24px; height: 24px; border-radius: 50%; cursor: pointer; font-size: 13px; line-height: 1;
    display: flex; align-items: center; justify-content: center; transition: all 0.15s ease;
  }
  .hud-toggle:hover { background: var(--btn-hover); color: var(--text); }
  .hud-body { padding: 14px 16px 16px; }
  .hud.collapsed .hud-body { display: none; }
  .control { margin-bottom: 12px; }
  .control label { display: flex; justify-content: space-between; align-items: baseline; color: var(--subtext); margin-bottom: 6px; font-size: 12px; }
  .control label span.val { color: var(--text); font-weight: 600; font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
  input[type=range] {
    width: 100%; accent-color: var(--accent); cursor: pointer; height: 4px; border-radius: 999px;
    background: var(--track-bg); appearance: none; -webkit-appearance: none;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%;
    background: var(--accent); box-shadow: 0 2px 6px rgba(0, 130, 251, 0.35); cursor: pointer; border: 2px solid #FFFFFF;
  }
  .btn-row { display: flex; gap: 6px; margin-top: 8px; }
  .btn-row button {
    flex: 1; padding: 7px 8px; border-radius: 9px; border: 1px solid var(--border);
    background: var(--btn-bg); color: var(--subtext);
    font-family: var(--sans); font-size: 11px; font-weight: 500;
    cursor: pointer; transition: all 0.15s ease;
  }
  .btn-row button:hover { color: var(--text); background: var(--btn-hover); }
  .btn-row button.active { background: var(--accent); border-color: var(--accent); color: #FFFFFF; font-weight: 600; }

  .status-strip {
    position: absolute; bottom: 20px; left: 20px;
    background: var(--glass);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px 6px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
    display: flex; align-items: center; font-size: 11.5px;
    transition: background 0.25s ease, border-color 0.25s ease;
  }
  .status-cell { padding: 4px 12px; border-right: 1px solid var(--divider); display: flex; align-items: center; gap: 6px; }
  .status-cell:last-child { border-right: none; }
  .swatch { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
  .tel-val { color: var(--text); font-weight: 600; font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

<div class="hud" id="hud-panel">
  <div class="hud-header">
    <strong>Orbital Controls</strong>
    <button class="hud-toggle" id="hud-min" title="Toggle Controls">&minus;</button>
  </div>
  <div class="hud-body">
    <div class="control">
      <label><span>Gravitational Param (<span class="sym">GM</span>)</span><span class="val" id="val-gm">120</span></label>
      <input type="range" id="sl-gm" min="40" max="320" step="5" value="120">
    </div>
    <div class="control">
      <label><span>Tangential Vel (<span class="sym">v</span><sub>0</sub>)</span><span class="val" id="val-v0">3.10</span></label>
      <input type="range" id="sl-v0" min="1.4" max="4.5" step="0.05" value="3.10">
    </div>
    <div class="control">
      <label><span>Inclination (&iota;)</span><span class="val" id="val-inc">15&deg;</span></label>
      <input type="range" id="sl-inc" min="0" max="45" step="1" value="15">
    </div>
    <div class="btn-row">
      <button id="btn-wedges" class="active">Area Sectors</button>
      <button id="btn-crash">High GM</button>
    </div>
    <div class="btn-row">
      <button id="btn-circular">Circular</button>
      <button id="btn-elliptical" class="active">Eccentric</button>
      <button id="btn-reset">Reset</button>
    </div>
  </div>
</div>

<div class="status-strip">
  <div class="status-cell">
    <span style="color:var(--muted)"><span class="sym">r</span></span>
    <span class="tel-val" id="tel-r">8.00 AU</span>
  </div>
  <div class="status-cell">
    <span style="color:var(--muted)">|<span class="vec">v</span>|</span>
    <span class="tel-val" id="tel-v">3.20 km/s</span>
  </div>
  <div class="status-cell">
    <span style="color:var(--muted)"><span class="sym">dA</span>/<span class="sym">dt</span></span>
    <span class="tel-val" id="tel-da">12.80 AU<sup>2</sup>/s</span>
  </div>
  <div class="status-cell">
    <span class="tel-val" id="tel-status" style="color:var(--accent)">BOUND ELLIPSE</span>
  </div>
  <div class="status-cell">
    <span class="swatch" id="swatch-v" style="background:#FFFFFF"></span><span><span class="vec">v</span></span>
  </div>
  <div class="status-cell">
    <span class="swatch" style="background:#1890FF"></span><span><span class="vec">F</span><sub>g</sub></span>
  </div>
</div>

<script>
  let runtimeErrors = [];
  let isLightMode = false;
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg);
    window.parent.postMessage({ type: "physicraft_error", error: msg, line: line }, "*");
  };

  document.getElementById('hud-min').onclick = function() {
    const p = document.getElementById('hud-panel');
    p.classList.toggle('collapsed');
    this.innerHTML = p.classList.contains('collapsed') ? '+' : '&minus;';
  };

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 300);
  camera.position.set(0, 18, 22);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setClearColor(0x050507, 1);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  const starLight = new THREE.PointLight(0x1890ff, 2.2, 100);
  scene.add(starLight);

  let grid = new THREE.GridHelper(32, 32, 0x262629, 0x141416);
  grid.position.y = -3;
  scene.add(grid);

  const starsGeo = new THREE.BufferGeometry();
  const starPts = [];
  for (let i = 0; i < 500; i++) {
    starPts.push((Math.random() - 0.5) * 160, (Math.random() - 0.5) * 160, (Math.random() - 0.5) * 160);
  }
  starsGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPts, 3));
  const starsMat = new THREE.PointsMaterial({ color: 0x52525b, size: 0.3 });
  scene.add(new THREE.Points(starsGeo, starsMat));

  // Central Star (Meta Light Blue core)
  const starMesh = new THREE.Mesh(
    new THREE.SphereGeometry(1.3, 32, 32),
    new THREE.MeshBasicMaterial({ color: 0x1890ff })
  );
  scene.add(starMesh);
  const starHalo = new THREE.Mesh(
    new THREE.SphereGeometry(1.85, 32, 32),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.24 })
  );
  scene.add(starHalo);

  // Planet
  const planetMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xd4d4d8, emissiveIntensity: 0.45, roughness: 0.25 });
  const planetMesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.5, 32, 32),
    planetMat
  );
  scene.add(planetMesh);

  const velArrow = new THREE.ArrowHelper(new THREE.Vector3(0,0,1), new THREE.Vector3(), 2, 0xffffff, 0.45, 0.25);
  const gravArrow = new THREE.ArrowHelper(new THREE.Vector3(-1,0,0), new THREE.Vector3(), 2, 0x1890ff, 0.45, 0.25);
  scene.add(velArrow);
  scene.add(gravArrow);

  const maxTrail = 1000;
  const trailPos = new Float32Array(maxTrail * 3);
  const trailGeo = new THREE.BufferGeometry();
  trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPos, 3));
  const trailMat = new THREE.LineBasicMaterial({ color: 0x94a3b8 });
  const trailLine = new THREE.Line(trailGeo, trailMat);
  scene.add(trailLine);
  let trailCount = 0;

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

  function applySceneTheme(theme) {
    isLightMode = (theme === 'light');
    document.body.classList.toggle('light', isLightMode);
    renderer.setClearColor(isLightMode ? 0xF2F5F9 : 0x050507, 1);
    scene.remove(grid);
    grid = new THREE.GridHelper(32, 32, isLightMode ? 0xCBD5E1 : 0x262629, isLightMode ? 0xE2E8F0 : 0x141416);
    grid.position.y = -3;
    scene.add(grid);
    starsMat.color.setHex(isLightMode ? 0xCBD5E1 : 0x52525b);
    const vHex = isLightMode ? 0x1D1D1F : 0xFFFFFF;
    velArrow.setColor(new THREE.Color(vHex));
    planetMat.color.setHex(isLightMode ? 0x1E293B : 0xFFFFFF);
    planetMat.emissive.setHex(isLightMode ? 0x334155 : 0xD4D4D8);
    const sw = document.getElementById('swatch-v');
    if (sw) sw.style.background = isLightMode ? '#1D1D1F' : '#FFFFFF';
  }

  window.addEventListener('message', (e) => {
    if (e.data && e.data.type === 'physicraft_theme') {
      applySceneTheme(e.data.theme);
    }
  });

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
    document.getElementById('tel-status').textContent = "BOUND ELLIPSE";
    document.getElementById('tel-status').style.color = "var(--accent)";
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
  };
  document.getElementById('btn-crash').onclick = () => {
    params.GM = 290;
    document.getElementById('sl-gm').value = 290;
    document.getElementById('val-gm').textContent = "290";
    starMesh.scale.setScalar(1.5);
    starHalo.scale.setScalar(1.6);
  };
  document.getElementById('btn-circular').onclick = () => {
    params.GM = 120; params.v0 = Math.sqrt(120 / 9.5);
    document.getElementById('sl-gm').value = 120;
    document.getElementById('sl-v0').value = params.v0.toFixed(2);
    document.getElementById('val-gm').textContent = "120";
    document.getElementById('val-v0').textContent = params.v0.toFixed(2);
    document.getElementById('btn-circular').classList.add('active');
    document.getElementById('btn-elliptical').classList.remove('active');
    resetOrbit();
  };
  document.getElementById('btn-elliptical').onclick = () => {
    params.GM = 120; params.v0 = 2.85;
    document.getElementById('sl-gm').value = 120;
    document.getElementById('sl-v0').value = 2.85;
    document.getElementById('val-gm').textContent = "120";
    document.getElementById('val-v0').textContent = "2.85";
    document.getElementById('btn-elliptical').classList.add('active');
    document.getElementById('btn-circular').classList.remove('active');
    resetOrbit();
  };
  document.getElementById('btn-reset').onclick = resetOrbit;

  resetOrbit();

  function stepOrbit(dt) {
    if (crashed) return;
    const r = pos.length();
    if (r < 1.55) {
      crashed = true;
      document.getElementById('tel-status').textContent = "PERIHELION IMPACT";
      document.getElementById('tel-status').style.color = "var(--accent)";
      return;
    }

    const rSq = Math.max(2.0, r * r);
    const acc1 = pos.clone().normalize().multiplyScalar(-params.GM / rSq);
    pos.addScaledVector(vel, dt).addScaledVector(acc1, 0.5 * dt * dt);

    const r2 = pos.length();
    const r2Sq = Math.max(2.0, r2 * r2);
    const acc2 = pos.clone().normalize().multiplyScalar(-params.GM / r2Sq);
    vel.addScaledVector(acc1.add(acc2), 0.5 * dt);

    planetMesh.position.copy(pos);

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
      const altColor = isLightMode ? 0x64748b : 0xffffff;
      const wMat = new THREE.MeshBasicMaterial({
        color: wedgeColorToggle ? 0x1890ff : altColor,
        transparent: true,
        opacity: wedgeColorToggle ? 0.26 : 0.14,
        side: THREE.DoubleSide
      });
      wedgeGroup.add(new THREE.Mesh(wGeo, wMat));
      currentWedgePts = [pos.clone()];
      wedgeTimer = 0;
    }

    velArrow.position.copy(pos);
    velArrow.setDirection(vel.clone().normalize());
    velArrow.setLength(Math.min(4.0, vel.length() * 0.75), 0.45, 0.25);

    gravArrow.position.copy(pos);
    gravArrow.setDirection(pos.clone().negate().normalize());
    gravArrow.setLength(Math.min(4.2, (params.GM / r2Sq) * 0.85), 0.45, 0.25);

    const L = pos.clone().cross(vel).length();
    document.getElementById('tel-r').textContent = `${r2.toFixed(2)} AU`;
    document.getElementById('tel-v').textContent = `${vel.length().toFixed(2)} km/s`;
    document.getElementById('tel-da').innerHTML = `${(0.5 * L).toFixed(2)} AU<sup>2</sup>/s`;
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
        "title": "Double Pendulum & Chaos",
        "subtitle": "AP Physics C · Lagrangian Mechanics",
        "prompt": "Create a 3D double pendulum chaos simulation with a twin perturbation pendulum offset by Δθ_0 = 0.05° so students can observe positive Lyapunov exponent divergence (Δr(t) ∝ e^(λt)) with RK4 integration.",
        "curriculum": {
            "concept": "Coupled Nonlinear Oscillators & Sensitive Dependence",
            "equations": [
                r"\mathcal{L} = T - V, \quad \frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{\theta}_i}\right) - \frac{\partial \mathcal{L}}{\partial \theta_i} = 0",
                r"|\Delta \vec{r}(t)| \approx |\Delta \vec{r}_0| \, e^{\lambda t} \quad (\lambda > 0)",
                r"E_{\text{tot}} = T_1 + T_2 + V_1 + V_2 = \text{const}"
            ],
            "teacher_guide": r"This simulation integrates two coupled pendulums concurrently via 4th-order Runge-Kutta (RK4): the primary trajectory ($\theta_0$) and the perturbed trajectory ($\theta_0 + \Delta\theta_0$, light blue) separated by $\Delta\theta_0 = 0.05^\circ$. They track identically for ~4 seconds before diverging exponentially.",
            "misconception_alert": r"Students often confuse deterministic chaos with randomness or energy loss. Compare the high-angle chaotic regime ($\theta_1 = 125^\circ$, $\lambda > 0$) against the small-angle linear regime ($\theta_1 = 20^\circ$, $\lambda \approx 0$).",
            "intuition_questions": [
                r"At small release angles ($\theta_1 < 25^\circ$), do the primary and $\Delta\theta_0$-perturbed pendulums diverge exponentially or stay in sync?",
                r"How does increasing the lower bob mass $m_2$ relative to $m_1$ alter momentum transfer between the coupled arms?",
                r"Why does 4th-order Runge-Kutta (RK4) preserve bounded mechanical energy $E_{\text{tot}}$ where first-order Euler integration drifts?"
            ],
            "tts_narration": "Welcome to the Double Pendulum Chaos Lab. Two coupled pendulums are released simultaneously with an initial angular separation of just five hundredths of a degree. Watch how both trajectories remain superimposed during the initial oscillations before diverging rapidly—demonstrating sensitive dependence on initial conditions in a deterministic Lagrangian system."
        },
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  :root {
    --bg: #050507;
    --glass: rgba(20, 22, 28, 0.72);
    --border: rgba(255, 255, 255, 0.1);
    --divider: rgba(255, 255, 255, 0.08);
    --text: #F5F5F7;
    --subtext: #D2D2D7;
    --muted: #86868B;
    --accent: #1890FF;
    --btn-bg: rgba(255, 255, 255, 0.06);
    --btn-hover: rgba(255, 255, 255, 0.12);
    --track-bg: rgba(255, 255, 255, 0.16);
    --sans: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    --mono: ui-monospace, 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
  }
  body.light {
    --bg: #F2F5F9;
    --glass: rgba(255, 255, 255, 0.82);
    --border: rgba(0, 0, 0, 0.08);
    --divider: rgba(0, 0, 0, 0.07);
    --text: #1D1D1F;
    --subtext: #3A3A3C;
    --muted: #6E6E73;
    --accent: #0082FB;
    --btn-bg: rgba(0, 0, 0, 0.04);
    --btn-hover: rgba(0, 0, 0, 0.08);
    --track-bg: rgba(0, 0, 0, 0.14);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: var(--bg); color: var(--text); font-family: var(--sans); overflow: hidden; -webkit-font-smoothing: antialiased; transition: background 0.25s ease, color 0.25s ease; }
  canvas { display: block; width: 100vw; height: 100vh; }

  .vec { position: relative; display: inline-block; font-style: italic; font-family: Georgia, 'Times New Roman', serif; padding-top: 2px; margin: 0 1px; }
  .vec::after { content: "→"; position: absolute; top: -0.58em; left: 50%; transform: translateX(-50%) scale(0.72); font-style: normal; font-family: var(--sans); color: inherit; }
  .sym { font-style: italic; font-family: Georgia, 'Times New Roman', serif; }
  sub, sup { font-size: 0.74em; line-height: 0; position: relative; vertical-align: baseline; font-style: normal; }
  sub { bottom: -0.22em; }
  sup { top: -0.42em; }

  .hud {
    position: absolute; top: 20px; right: 20px; width: 268px;
    background: var(--glass);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
    font-size: 12px;
    overflow: hidden;
    transition: background 0.25s ease, border-color 0.25s ease;
  }
  .hud-header {
    padding: 12px 16px; border-bottom: 1px solid var(--divider);
    display: flex; justify-content: space-between; align-items: center;
    font-size: 12px; font-weight: 600; color: var(--text); letter-spacing: -0.01em;
  }
  .hud-toggle {
    background: var(--btn-bg); border: none; color: var(--muted);
    width: 24px; height: 24px; border-radius: 50%; cursor: pointer; font-size: 13px; line-height: 1;
    display: flex; align-items: center; justify-content: center; transition: all 0.15s ease;
  }
  .hud-toggle:hover { background: var(--btn-hover); color: var(--text); }
  .hud-body { padding: 14px 16px 16px; }
  .hud.collapsed .hud-body { display: none; }
  .control { margin-bottom: 12px; }
  .control label { display: flex; justify-content: space-between; align-items: baseline; color: var(--subtext); margin-bottom: 6px; font-size: 12px; }
  .control label span.val { color: var(--text); font-weight: 600; font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
  input[type=range] {
    width: 100%; accent-color: var(--accent); cursor: pointer; height: 4px; border-radius: 999px;
    background: var(--track-bg); appearance: none; -webkit-appearance: none;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%;
    background: var(--accent); box-shadow: 0 2px 6px rgba(0, 130, 251, 0.35); cursor: pointer; border: 2px solid #FFFFFF;
  }
  .btn-row { display: flex; gap: 6px; margin-top: 12px; }
  .btn-row button {
    flex: 1; padding: 7px 8px; border-radius: 9px; border: 1px solid var(--border);
    background: var(--btn-bg); color: var(--subtext);
    font-family: var(--sans); font-size: 11px; font-weight: 500;
    cursor: pointer; transition: all 0.15s ease;
  }
  .btn-row button:hover { color: var(--text); background: var(--btn-hover); }
  .btn-row button.active { background: var(--accent); border-color: var(--accent); color: #FFFFFF; font-weight: 600; }

  .status-strip {
    position: absolute; bottom: 20px; left: 20px;
    background: var(--glass);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px 6px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
    display: flex; align-items: center; font-size: 11.5px;
    transition: background 0.25s ease, border-color 0.25s ease;
  }
  .status-cell { padding: 4px 12px; border-right: 1px solid var(--divider); display: flex; align-items: center; gap: 6px; }
  .status-cell:last-child { border-right: none; }
  .swatch { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
  .tel-val { color: var(--text); font-weight: 600; font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

<div class="hud" id="hud-panel">
  <div class="hud-header">
    <strong>Pendulum Controls</strong>
    <button class="hud-toggle" id="hud-min" title="Toggle Controls">&minus;</button>
  </div>
  <div class="hud-body">
    <div class="control">
      <label><span>Release Angle (&theta;<sub>1</sub>)</span><span class="val" id="val-th1">125&deg;</span></label>
      <input type="range" id="sl-th1" min="15" max="170" step="1" value="125">
    </div>
    <div class="control">
      <label><span>Distal Mass (<span class="sym">m</span><sub>2</sub>)</span><span class="val" id="val-m2">2.0 kg</span></label>
      <input type="range" id="sl-m2" min="0.5" max="5.0" step="0.5" value="2.0">
    </div>
    <div class="control">
      <label><span>Gravity (<span class="sym">g</span>)</span><span class="val" id="val-g">9.81 m/s<sup>2</sup></span></label>
      <input type="range" id="sl-g" min="1.6" max="24.8" step="0.2" value="9.8">
    </div>
    <div class="control">
      <label><span>Perturbation (&Delta;&theta;<sub>0</sub>)</span><span class="val" id="val-eps">0.05&deg;</span></label>
      <input type="range" id="sl-eps" min="0.01" max="1.0" step="0.01" value="0.05">
    </div>
    <div class="btn-row">
      <button id="btn-chaos" class="active">Chaotic 125&deg;</button>
      <button id="btn-harmonic">Linear 20&deg;</button>
      <button id="btn-reset">Reset</button>
    </div>
  </div>
</div>

<div class="status-strip">
  <div class="status-cell">
    <span style="color:var(--muted)">|&Delta;<span class="vec">r</span>|</span>
    <span class="tel-val" id="tel-div">0.002 m</span>
  </div>
  <div class="status-cell">
    <span style="color:var(--muted)">(&theta;<sub>1</sub>, &theta;<sub>2</sub>)</span>
    <span class="tel-val" id="tel-theta">125&deg;, 100&deg;</span>
  </div>
  <div class="status-cell">
    <span class="tel-val" id="tel-regime" style="color:var(--accent)">LYAPUNOV &lambda; &gt; 0</span>
  </div>
  <div class="status-cell">
    <span class="swatch" id="swatch-a" style="background:#FFFFFF"></span><span>&theta;<sub>0</sub></span>
  </div>
  <div class="status-cell">
    <span class="swatch" style="background:#1890FF"></span><span>&theta;<sub>0</sub> + &Delta;&theta;<sub>0</sub></span>
  </div>
</div>

<script>
  let runtimeErrors = [];
  let isLightMode = false;
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg);
    window.parent.postMessage({ type: "physicraft_error", error: msg, line: line }, "*");
  };

  document.getElementById('hud-min').onclick = function() {
    const p = document.getElementById('hud-panel');
    p.classList.toggle('collapsed');
    this.innerHTML = p.classList.contains('collapsed') ? '+' : '&minus;';
  };

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(0, 1, 16);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setClearColor(0x050507, 1);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  const light = new THREE.DirectionalLight(0xffffff, 1.0);
  light.position.set(8, 15, 12);
  scene.add(light);

  let grid = new THREE.GridHelper(24, 24, 0x262629, 0x141416);
  grid.position.y = -6.5;
  scene.add(grid);

  const pivotBar = new THREE.Mesh(
    new THREE.CylinderGeometry(0.1, 0.1, 3.0, 16),
    new THREE.MeshStandardMaterial({ color: 0x64748b })
  );
  pivotBar.rotation.x = Math.PI / 2;
  pivotBar.position.set(0, 2.5, 0);
  scene.add(pivotBar);

  function createPendulumVisual(colorHex, zOffset) {
    const arm1Geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
    const arm2Geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
    const armMat = new THREE.LineBasicMaterial({ color: 0x94a3b8 });
    const arm1 = new THREE.Line(arm1Geo, armMat);
    const arm2 = new THREE.Line(arm2Geo, armMat);
    scene.add(arm1); scene.add(arm2);

    const bob1Mat = new THREE.MeshStandardMaterial({ color: colorHex, emissive: colorHex, emissiveIntensity: 0.35 });
    const bob2Mat = new THREE.MeshStandardMaterial({ color: colorHex, emissive: colorHex, emissiveIntensity: 0.65 });
    const bob1 = new THREE.Mesh(new THREE.SphereGeometry(0.3, 24, 24), bob1Mat);
    const bob2 = new THREE.Mesh(new THREE.SphereGeometry(0.4, 24, 24), bob2Mat);
    scene.add(bob1); scene.add(bob2);

    const maxPts = 750;
    const trailArr = new Float32Array(maxPts * 3);
    const trailGeo = new THREE.BufferGeometry();
    trailGeo.setAttribute('position', new THREE.BufferAttribute(trailArr, 3));
    const trailMat = new THREE.LineBasicMaterial({ color: colorHex });
    const trail = new THREE.Line(trailGeo, trailMat);
    scene.add(trail);

    return { arm1, arm2, bob1, bob2, bob1Mat, bob2Mat, trail, trailMat, trailArr, trailGeo, count: 0, maxPts, zOffset };
  }

  const visA = createPendulumVisual(0xffffff, 0.4);
  const visB = createPendulumVisual(0x1890ff, -0.4);

  let params = { m1: 2.0, m2: 2.0, L1: 3.6, L2: 3.2, g: 9.81, th1Deg: 125, epsDeg: 0.05 };
  let stateA = [0, 0, 0, 0];
  let stateB = [0, 0, 0, 0];

  function applySceneTheme(theme) {
    isLightMode = (theme === 'light');
    document.body.classList.toggle('light', isLightMode);
    renderer.setClearColor(isLightMode ? 0xF2F5F9 : 0x050507, 1);
    scene.remove(grid);
    grid = new THREE.GridHelper(24, 24, isLightMode ? 0xCBD5E1 : 0x262629, isLightMode ? 0xE2E8F0 : 0x141416);
    grid.position.y = -6.5;
    scene.add(grid);
    const colorA = isLightMode ? 0x1E293B : 0xFFFFFF;
    visA.bob1Mat.color.setHex(colorA);
    visA.bob1Mat.emissive.setHex(colorA);
    visA.bob2Mat.color.setHex(colorA);
    visA.bob2Mat.emissive.setHex(colorA);
    visA.trailMat.color.setHex(colorA);
    const sw = document.getElementById('swatch-a');
    if (sw) sw.style.background = isLightMode ? '#1E293B' : '#FFFFFF';
  }

  window.addEventListener('message', (e) => {
    if (e.data && e.data.type === 'physicraft_theme') {
      applySceneTheme(e.data.theme);
    }
  });

  function resetPendulums() {
    const r1 = (params.th1Deg * Math.PI) / 180;
    const eps = (params.epsDeg * Math.PI) / 180;
    stateA = [r1, 0, r1 * 0.8, 0];
    stateB = [r1 + eps, 0, r1 * 0.8, 0];
    visA.count = 0; visB.count = 0;
    visA.trailGeo.setDrawRange(0, 0);
    visB.trailGeo.setDrawRange(0, 0);
    document.getElementById('tel-regime').innerHTML = params.th1Deg > 45 ? "LYAPUNOV &lambda; &gt; 0" : "QUASI-PERIODIC (&lambda; &approx; 0)";
    document.getElementById('tel-regime').style.color = params.th1Deg > 45 ? "var(--accent)" : "var(--text)";
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
    document.getElementById('val-th1').innerHTML = params.th1Deg + '&deg;';
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
    document.getElementById('val-g').innerHTML = params.g.toFixed(1) + ' m/s<sup>2</sup>';
  };
  document.getElementById('sl-eps').oninput = e => {
    params.epsDeg = parseFloat(e.target.value);
    document.getElementById('val-eps').innerHTML = params.epsDeg.toFixed(2) + '&deg;';
    resetPendulums();
  };
  document.getElementById('btn-chaos').onclick = () => {
    params.th1Deg = 125; document.getElementById('sl-th1').value = 125;
    document.getElementById('val-th1').innerHTML = '125&deg;';
    document.getElementById('btn-chaos').classList.add('active');
    document.getElementById('btn-harmonic').classList.remove('active');
    resetPendulums();
  };
  document.getElementById('btn-harmonic').onclick = () => {
    params.th1Deg = 20; document.getElementById('sl-th1').value = 20;
    document.getElementById('val-th1').innerHTML = '20&deg;';
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
    document.getElementById('tel-div').textContent = `${dist.toFixed(3)} m`;
    document.getElementById('tel-theta').innerHTML = `${Math.round(stateA[0]*180/Math.PI)}&deg;, ${Math.round(stateA[2]*180/Math.PI)}&deg;`;

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
    },

    "waves": {
        "id": "waves",
        "title": "Wave Superposition & Interference",
        "subtitle": "AP Physics 2 & C · Physical Optics",
        "prompt": "Show 3D wave interference from two coherent point sources S_1 and S_2 in a ripple tank with adjustable source separation d, wavelength λ, relative phase Δφ, and hyperbolic nodal channels of destructive interference.",
        "curriculum": {
            "concept": "Superposition Principle & Two-Source Interference",
            "equations": [
                r"\Delta r = |r_1 - r_2| \approx d \sin\theta",
                r"\text{Constructive: } \Delta r = m\lambda \quad (m \in \mathbb{Z})",
                r"\text{Destructive: } \Delta r = \left(m + \tfrac{1}{2}\right)\lambda"
            ],
            "teacher_guide": r"Switch to Top View so students can trace the stationary hyperbolic nodal channels radiating between coherent emitters $S_1$ and $S_2$. Along every nodal locus, path-length difference satisfies $\Delta r = (m + \frac{1}{2})\lambda$, yielding permanent destructive cancellation ($y_{\text{net}} = 0$).",
            "misconception_alert": r"Students often think stationary nodal lines are static regions with no wave motion. Toggle Single Source mode to show that individual circular wavefronts pass continuously across nodal channels.",
            "intuition_questions": [
                r"When emitter separation $d$ increases at fixed wavelength $\lambda$, does the maximum constructive order $m_{\max} = \lfloor d/\lambda \rfloor$ increase or decrease?",
                r"How does the central $\theta = 0^\circ$ axis behave when relative phase $\Delta\phi$ shifts from $0^\circ$ to $180^\circ$ ($\pi\text{ rad}$)?",
                r"Why does surface wave amplitude attenuate with radial distance $r$ from each coherent point source?"
            ],
            "tts_narration": "Welcome to the 3D Wave Superposition Lab. Two coherent point emitters oscillate on the surface, generating intersecting wavefronts. Notice the calm hyperbolic lanes between bright antinodal crests—these are nodal lines where path difference equals a half-integer multiple of wavelength. Adjust separation and phase shift to steer the interference fringes in real time."
        },
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  :root {
    --bg: #050507;
    --glass: rgba(20, 22, 28, 0.72);
    --border: rgba(255, 255, 255, 0.1);
    --divider: rgba(255, 255, 255, 0.08);
    --text: #F5F5F7;
    --subtext: #D2D2D7;
    --muted: #86868B;
    --accent: #1890FF;
    --btn-bg: rgba(255, 255, 255, 0.06);
    --btn-hover: rgba(255, 255, 255, 0.12);
    --track-bg: rgba(255, 255, 255, 0.16);
    --sans: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    --mono: ui-monospace, 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
  }
  body.light {
    --bg: #F2F5F9;
    --glass: rgba(255, 255, 255, 0.82);
    --border: rgba(0, 0, 0, 0.08);
    --divider: rgba(0, 0, 0, 0.07);
    --text: #1D1D1F;
    --subtext: #3A3A3C;
    --muted: #6E6E73;
    --accent: #0082FB;
    --btn-bg: rgba(0, 0, 0, 0.04);
    --btn-hover: rgba(0, 0, 0, 0.08);
    --track-bg: rgba(0, 0, 0, 0.14);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body { background: var(--bg); color: var(--text); font-family: var(--sans); overflow: hidden; -webkit-font-smoothing: antialiased; transition: background 0.25s ease, color 0.25s ease; }
  canvas { display: block; width: 100vw; height: 100vh; }

  .vec { position: relative; display: inline-block; font-style: italic; font-family: Georgia, 'Times New Roman', serif; padding-top: 2px; margin: 0 1px; }
  .vec::after { content: "→"; position: absolute; top: -0.58em; left: 50%; transform: translateX(-50%) scale(0.72); font-style: normal; font-family: var(--sans); color: inherit; }
  .sym { font-style: italic; font-family: Georgia, 'Times New Roman', serif; }
  sub, sup { font-size: 0.74em; line-height: 0; position: relative; vertical-align: baseline; font-style: normal; }
  sub { bottom: -0.22em; }
  sup { top: -0.42em; }

  .hud {
    position: absolute; top: 20px; right: 20px; width: 268px;
    background: var(--glass);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
    font-size: 12px;
    overflow: hidden;
    transition: background 0.25s ease, border-color 0.25s ease;
  }
  .hud-header {
    padding: 12px 16px; border-bottom: 1px solid var(--divider);
    display: flex; justify-content: space-between; align-items: center;
    font-size: 12px; font-weight: 600; color: var(--text); letter-spacing: -0.01em;
  }
  .hud-toggle {
    background: var(--btn-bg); border: none; color: var(--muted);
    width: 24px; height: 24px; border-radius: 50%; cursor: pointer; font-size: 13px; line-height: 1;
    display: flex; align-items: center; justify-content: center; transition: all 0.15s ease;
  }
  .hud-toggle:hover { background: var(--btn-hover); color: var(--text); }
  .hud-body { padding: 14px 16px 16px; }
  .hud.collapsed .hud-body { display: none; }
  .control { margin-bottom: 12px; }
  .control label { display: flex; justify-content: space-between; align-items: baseline; color: var(--subtext); margin-bottom: 6px; font-size: 12px; }
  .control label span.val { color: var(--text); font-weight: 600; font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
  input[type=range] {
    width: 100%; accent-color: var(--accent); cursor: pointer; height: 4px; border-radius: 999px;
    background: var(--track-bg); appearance: none; -webkit-appearance: none;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%;
    background: var(--accent); box-shadow: 0 2px 6px rgba(0, 130, 251, 0.35); cursor: pointer; border: 2px solid #FFFFFF;
  }
  .btn-row { display: flex; gap: 6px; margin-top: 12px; }
  .btn-row button {
    flex: 1; padding: 7px 8px; border-radius: 9px; border: 1px solid var(--border);
    background: var(--btn-bg); color: var(--subtext);
    font-family: var(--sans); font-size: 11px; font-weight: 500;
    cursor: pointer; transition: all 0.15s ease;
  }
  .btn-row button:hover { color: var(--text); background: var(--btn-hover); }
  .btn-row button.active { background: var(--accent); border-color: var(--accent); color: #FFFFFF; font-weight: 600; }

  .status-strip {
    position: absolute; bottom: 20px; left: 20px;
    background: var(--glass);
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px 6px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
    display: flex; align-items: center; font-size: 11.5px;
    transition: background 0.25s ease, border-color 0.25s ease;
  }
  .status-cell { padding: 4px 12px; border-right: 1px solid var(--divider); display: flex; align-items: center; gap: 6px; }
  .status-cell:last-child { border-right: none; }
  .swatch { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
  .tel-val { color: var(--text); font-weight: 600; font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

<div class="hud" id="hud-panel">
  <div class="hud-header">
    <strong>Wave Controls</strong>
    <button class="hud-toggle" id="hud-min" title="Toggle Controls">&minus;</button>
  </div>
  <div class="hud-body">
    <div class="control">
      <label><span>Emitter Separation (<span class="sym">d</span>)</span><span class="val" id="val-d">5.00 m</span></label>
      <input type="range" id="sl-d" min="1.5" max="9.0" step="0.25" value="5.0">
    </div>
    <div class="control">
      <label><span>Wavelength (&lambda;)</span><span class="val" id="val-lam">2.0 m</span></label>
      <input type="range" id="sl-lam" min="0.8" max="4.5" step="0.1" value="2.0">
    </div>
    <div class="control">
      <label><span>Phase Shift (&Delta;&phi;)</span><span class="val" id="val-phi">0&deg;</span></label>
      <input type="range" id="sl-phi" min="0" max="180" step="15" value="0">
    </div>
    <div class="control">
      <label><span>Amplitude (<span class="sym">A</span>)</span><span class="val" id="val-amp">0.65 m</span></label>
      <input type="range" id="sl-amp" min="0.2" max="1.2" step="0.05" value="0.65">
    </div>
    <div class="btn-row">
      <button id="btn-dual" class="active">Dual S₁+S₂</button>
      <button id="btn-single">Single S₁</button>
      <button id="btn-top">Top View</button>
    </div>
  </div>
</div>

<div class="status-strip">
  <div class="status-cell">
    <span style="color:var(--muted)"><span class="sym">d</span>/&lambda;</span>
    <span class="tel-val" id="tel-ratio">2.50</span>
  </div>
  <div class="status-cell">
    <span style="color:var(--muted)"><span class="sym">m</span><sub>max</sub></span>
    <span class="tel-val" id="tel-orders">2</span>
  </div>
  <div class="status-cell">
    <span class="tel-val" id="tel-phase" style="color:var(--accent)">&theta;=0: ANTINODE</span>
  </div>
  <div class="status-cell">
    <span class="swatch" style="background:#1890FF"></span><span>Crest (+2<span class="sym">A</span>)</span>
  </div>
  <div class="status-cell">
    <span class="swatch" style="background:#64748B"></span><span>Nodal (<span class="sym">y</span>=0)</span>
  </div>
  <div class="status-cell">
    <span class="swatch" style="background:#E2E8F0;border:1px solid #94A3B8"></span><span>Trough (&minus;2<span class="sym">A</span>)</span>
  </div>
</div>

<script>
  let runtimeErrors = [];
  let isLightMode = false;
  window.onerror = function(msg, src, line) {
    runtimeErrors.push(msg);
    window.parent.postMessage({ type: "physicraft_error", error: msg, line: line }, "*");
  };

  document.getElementById('hud-min').onclick = function() {
    const p = document.getElementById('hud-panel');
    p.classList.toggle('collapsed');
    this.innerHTML = p.classList.contains('collapsed') ? '+' : '&minus;';
  };

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(0, 14, 16);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setClearColor(0x050507, 1);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  scene.add(new THREE.AmbientLight(0xffffff, 0.72));
  const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
  dirLight.position.set(10, 18, 12);
  scene.add(dirLight);

  const segs = 110;
  const size = 22;
  const geo = new THREE.PlaneGeometry(size, size, segs, segs);
  geo.rotateX(-Math.PI / 2);

  const count = geo.attributes.position.count;
  const colors = new Float32Array(count * 3);
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const mat = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.28,
    metalness: 0.15,
    side: THREE.DoubleSide
  });
  const waterMesh = new THREE.Mesh(geo, mat);
  scene.add(waterMesh);

  const emitterGeo = new THREE.SphereGeometry(0.32, 20, 20);
  const emitterMat = new THREE.MeshStandardMaterial({ color: 0x1890ff, emissive: 0x0082fb, emissiveIntensity: 0.75 });
  const source1 = new THREE.Mesh(emitterGeo, emitterMat);
  const source2 = new THREE.Mesh(emitterGeo, emitterMat);
  scene.add(source1);
  scene.add(source2);

  let params = { d: 5.0, lam: 2.0, phiDeg: 0, amp: 0.65, dual: true };
  let simTime = 0;

  function applySceneTheme(theme) {
    isLightMode = (theme === 'light');
    document.body.classList.toggle('light', isLightMode);
    renderer.setClearColor(isLightMode ? 0xF2F5F9 : 0x050507, 1);
  }

  window.addEventListener('message', (e) => {
    if (e.data && e.data.type === 'physicraft_theme') {
      applySceneTheme(e.data.theme);
    }
  });

  function updateTelemetryLabels() {
    const ratio = params.d / params.lam;
    const mMax = Math.floor(ratio);
    document.getElementById('tel-ratio').textContent = ratio.toFixed(2);
    document.getElementById('tel-orders').textContent = String(mMax);
    document.getElementById('tel-phase').innerHTML = params.phiDeg === 180
      ? '&theta;=0: NODE (0)'
      : (params.phiDeg === 0 ? '&theta;=0: ANTINODE' : `&Delta;&phi;=${params.phiDeg}&deg;`);
  }

  document.getElementById('sl-d').oninput = e => {
    params.d = parseFloat(e.target.value);
    document.getElementById('val-d').textContent = params.d.toFixed(2) + ' m';
    updateTelemetryLabels();
  };
  document.getElementById('sl-lam').oninput = e => {
    params.lam = parseFloat(e.target.value);
    document.getElementById('val-lam').textContent = params.lam.toFixed(1) + ' m';
    updateTelemetryLabels();
  };
  document.getElementById('sl-phi').oninput = e => {
    params.phiDeg = parseFloat(e.target.value);
    document.getElementById('val-phi').innerHTML = params.phiDeg + '&deg;';
    updateTelemetryLabels();
  };
  document.getElementById('sl-amp').oninput = e => {
    params.amp = parseFloat(e.target.value);
    document.getElementById('val-amp').textContent = params.amp.toFixed(2) + ' m';
  };
  document.getElementById('btn-dual').onclick = () => {
    params.dual = true;
    source2.visible = true;
    document.getElementById('btn-dual').classList.add('active');
    document.getElementById('btn-single').classList.remove('active');
  };
  document.getElementById('btn-single').onclick = () => {
    params.dual = false;
    source2.visible = false;
    document.getElementById('btn-single').classList.add('active');
    document.getElementById('btn-dual').classList.remove('active');
  };
  document.getElementById('btn-top').onclick = () => {
    camera.position.set(0, 22, 0.01);
    controls.target.set(0, 0, 0);
  };

  updateTelemetryLabels();

  let frameCount = 0;
  let lastReport = performance.now();

  function animate() {
    requestAnimationFrame(animate);
    simTime += 0.065;

    const k = (2 * Math.PI) / params.lam;
    const phi = (params.phiDeg * Math.PI) / 180;
    const x1 = params.dual ? -params.d / 2 : 0;
    const x2 = params.d / 2;

    source1.position.set(x1, Math.sin(-simTime) * params.amp, 0);
    source2.position.set(x2, Math.sin(-simTime + phi) * params.amp, 0);

    const pos = geo.attributes.position;
    const col = geo.attributes.color;

    for (let i = 0; i < count; i++) {
      const vx = pos.getX(i);
      const vz = pos.getZ(i);

      const r1Sq = Math.max(1.5, (vx - x1) * (vx - x1) + vz * vz);
      const r1 = Math.sqrt(r1Sq);
      const w1 = params.amp * Math.sin(k * r1 - simTime) / Math.pow(r1Sq, 0.22);

      let y = w1;
      if (params.dual) {
        const r2Sq = Math.max(1.5, (vx - x2) * (vx - x2) + vz * vz);
        const r2 = Math.sqrt(r2Sq);
        const w2 = params.amp * Math.sin(k * r2 - simTime + phi) / Math.pow(r2Sq, 0.22);
        y += w2;
      }

      pos.setY(i, y);

      // Meta Light Blue (#1890FF) crest mapping with Light & Dark mode support
      const norm = Math.max(-1, Math.min(1, y / (params.amp * 1.4)));
      const intensity = Math.abs(norm);
      if (isLightMode) {
        if (intensity < 0.12) {
          col.setXYZ(i, 0.85, 0.89, 0.94);
        } else if (norm > 0) {
          col.setXYZ(i, 0.85 - 0.80 * norm, 0.89 - 0.35 * norm, 0.95 + 0.05 * norm);
        } else {
          const n = -norm;
          col.setXYZ(i, 0.88 + 0.11 * n, 0.91 + 0.08 * n, 0.95 + 0.04 * n);
        }
      } else {
        if (intensity < 0.12) {
          col.setXYZ(i, 0.05, 0.06, 0.09);
        } else if (norm > 0) {
          col.setXYZ(i, 0.05 + 0.08 * norm, 0.12 + 0.48 * norm, 0.22 + 0.78 * norm);
        } else {
          const n = -norm;
          col.setXYZ(i, 0.08 + 0.72 * n, 0.10 + 0.74 * n, 0.14 + 0.78 * n);
        }
      }
    }

    pos.needsUpdate = true;
    col.needsUpdate = true;
    geo.computeVertexNormals();

    controls.update();
    renderer.render(scene, camera);

    frameCount++;
    const now = performance.now();
    if (now - lastReport > 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastReport));
      const sampleY = pos.getY(0);
      window.parent.postMessage({
        type: "physicraft_telemetry",
        fps: fps,
        hasNaN: isNaN(sampleY),
        errors: runtimeErrors.length,
        energyBounded: Math.abs(sampleY) < 20,
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
