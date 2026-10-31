"""
Automated Verification Suite for Track A (`engine.py` & `app.py`).
Tests:
1. All 3 Hero Presets pass static AST, Three.js, slider, and telemetry heartbeat checks.
2. Auto-instrumentation injects `physicraft_telemetry` into un-instrumented Three.js HTML.
3. Parametric 3D Physics Synthesizer generates valid 3D Ripple Tank Wave Interference & 3D Magnus Projectile labs.
4. FastAPI endpoints (`/api/status`, `/api/generate`, `/api/self-heal`, `/api/publish-preview`, `/api/publish-confirm`, `/api/lineage`) pass end-to-end.
"""

import asyncio
from fastapi.testclient import TestClient

import app as fastapi_app
from engine import synthesize_parametric_3d_lab, verify_and_instrument_3d_html
from presets import PRESETS


def test_presets_verification():
    for key, preset in PRESETS.items():
        patched, report = verify_and_instrument_3d_html(preset["html"])
        assert report["passed"], f"Preset {key} failed verification: {report['issues']}"
        assert report["slider_count"] >= 3, f"Preset {key} should have >= 3 sliders"
        assert report["has_orbit_controls"], f"Preset {key} missing OrbitControls"
        assert "physicraft_telemetry" in patched, f"Preset {key} missing telemetry heartbeat"
    print("✓ All 3 Hero Presets passed static AST & numerical physics verification!")


def test_auto_instrumentation():
    minimal_three_html = """<!DOCTYPE html><html><body>
    <input type="range" min="0" max="10" />
    <input type="range" min="0" max="10" />
    <input type="range" min="0" max="10" />
    <script>
      const scene = new THREE.Scene();
      const renderer = new THREE.WebGLRenderer();
      const r = 0.5;
      const F = 10.0 / (r * r);
      function animate() { requestAnimationFrame(animate); }
      animate();
    </script></body></html>"""
    patched, report = verify_and_instrument_3d_html(minimal_three_html)
    assert report["passed"], f"Minimal Three.js failed: {report['issues']}"
    assert report["auto_instrumented"] is True
    assert report["softening_verified"] is True
    assert "Math.max(1.5, r * r)" in patched
    assert "physicraft_telemetry" in patched
    print("✓ Pre-flight auto-instrumentation of `physicraft_telemetry` & `Math.max(1.5, r * r)` singularity softening verified!")


def test_voice_to_3d_magnetic_flux_and_rutherford():
    client = TestClient(fastapi_app.app)

    # 0. Verify Voice-to-3D Hero Launchpad is served on startup without a default preset
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert 'id="voice-hero-stage"' in root_res.text
    assert 'id="btn-hero-mic"' in root_res.text

    # 1. Teacher speaks into microphone: "Explain magnetic flux and Faraday's law of induction"
    flux_res = client.post(
        "/api/generate",
        json={"prompt": "Explain magnetic flux and Faraday's law of induction with a rotating coil"},
    )
    assert flux_res.status_code == 200
    flux_data = flux_res.json()
    assert flux_data["sla_under_10s"] is True
    assert flux_data["total_latency_ms"] < 10000
    # Verify Step 1: Pre-Modeling Physics Accuracy Audit (Argon High)
    physics_audit = flux_data["physics_accuracy_check"]
    assert physics_audit["physically_accurate"] is True
    assert "Faraday" in physics_audit["verified_law"]
    assert len(physics_audit["conservation_invariants"]) >= 2
    assert len(physics_audit["vector_visualizers"]) >= 2
    assert "Φ_B" in flux_data["curriculum"]["concept"]
    assert flux_data["verification"]["passed"] is True
    assert flux_data["verification"]["slider_count"] >= 5
    assert "ArrowHelper" in flux_data["html"]
    flux_id = flux_data["interaction_id"]

    # 2. Multi-turn voice refinement using previous_interaction_id
    refine_res = client.post(
        "/api/generate",
        json={
            "prompt": "Now double the magnetic field and add a reference ring",
            "previous_interaction_id": flux_id,
        },
    )
    assert refine_res.status_code == 200
    refine_data = refine_res.json()
    assert refine_data["previous_interaction_id"] == flux_id
    assert "pc-refinement-banner" in refine_data["html"]

    # 3. Teacher speaks: "Show Rutherford alpha particle Coulomb scattering"
    ruth_res = client.post(
        "/api/generate",
        json={"prompt": "Show 3D Rutherford alpha particle Coulomb scattering off a gold nucleus"},
    )
    assert ruth_res.status_code == 200
    ruth_data = ruth_res.json()
    assert ruth_data["verification"]["passed"] is True
    assert "Math.max(1.5, r * r)" in ruth_data["html"]
    print("✓ Voice-to-3D (<10s SLA) Magnetic Flux, Multi-turn refinement, and Rutherford Scattering verified!")


def test_ferpa_pii_redaction_gate():
    client = TestClient(fastapi_app.app)
    pii_res = client.post(
        "/api/publish-preview",
        json={
            "lesson_title": "Magnetic Flux Lab",
            "teacher_notes": "Follow up with alex@school.edu (SSN 123-45-6789, Grade: B+) on Lenz's Law.",
            "intuition_questions": ["Q1"],
            "html_code": "<!DOCTYPE html><html></html>",
        },
    )
    assert pii_res.status_code == 200
    staged = pii_res.json()
    audit = staged["ferpa_audit"]
    assert audit["pii_detected"] is True
    assert audit["ferpa_compliant"] is False
    assert "[REDACTED_STUDENT_PII]" in staged["teacher_notes"]
    assert "alex@school.edu" not in staged["teacher_notes"]
    assert "123-45-6789" not in staged["teacher_notes"]
    assert staged["human_approval_required"] is True
    print("✓ Subagent 3 FERPA/PII detection, automatic redaction, and Human-in-the-Loop gate verified!")


def test_fastapi_endpoints():
    client = TestClient(fastapi_app.app)

    # 1. Status
    res = client.get("/api/status")
    assert res.status_code == 200
    assert res.json()["models"]["lead_architect"] == "gemini-4-argon"

    # 2. Generate Wave Interference Lab
    gen_res = client.post("/api/generate", json={"prompt": "Show 3D two-source ripple tank wave interference with wavelength slider"})
    assert gen_res.status_code == 200
    data = gen_res.json()
    assert data["status"] == "ok"
    assert "THREE.Scene" in data["html"]
    assert data["verification"]["passed"] is True
    first_id = data["interaction_id"]

    # 3. Multi-turn follow-up with previous_interaction_id
    gen_res2 = client.post(
        "/api/generate",
        json={"prompt": "Now show 3D projectile motion with Magnus spin", "previous_interaction_id": first_id},
    )
    assert gen_res2.status_code == 200
    assert gen_res2.json()["previous_interaction_id"] == first_id

    # 4. Autonomous Self-Heal endpoint
    heal_res = client.post(
        "/api/self-heal",
        json={
            "broken_html": data["html"],
            "error_report": "Simulated NaN in r=0 division",
            "previous_interaction_id": first_id,
        },
    )
    assert heal_res.status_code == 200
    assert "THREE.Scene" in heal_res.json()["html"]

    # 5. Human-in-the-Loop Google Classroom Gate
    pub_prev = client.post(
        "/api/publish-preview",
        json={
            "lesson_title": "Lorentz Force 3D Spiral",
            "teacher_notes": "Observe F = qv x B chirality.",
            "intuition_questions": ["Q1", "Q2"],
            "html_code": data["html"],
        },
    )
    assert pub_prev.status_code == 200
    approval_id = pub_prev.json()["approval_id"]
    assert pub_prev.json()["ferpa_audit"]["ferpa_compliant"] is True

    pub_conf = client.post(
        "/api/publish-confirm",
        json={"approval_id": approval_id, "approved_by_teacher": True},
    )
    assert pub_conf.status_code == 200
    assert pub_conf.json()["status"] == "published"

    # 6. Lineage tracking
    lin_res = client.get("/api/lineage")
    assert lin_res.status_code == 200
    assert len(lin_res.json()["lineage"]) >= 2
    print("✓ All FastAPI Track A endpoints (generate, multi-turn, self-heal, FERPA gate, lineage) verified!")


def test_universal_physics_concepts_and_zero_missing_glyphs():
    client = TestClient(fastapi_app.app)
    prompts_and_expectations = [
        ("show box moving down a ramp", "Inclined Plane", "F_N = m*g*cos(θ)"),
        ("explain a mass on a spring Hooke's law harmonic oscillator", "Spring", "Hooke"),
        ("show elastic collision conservation of momentum between two spheres", "Collision", "Momentum"),
        ("explain torque and moment of inertia on a spinning flywheel", "Torque", "τ = r × F"),
        ("demonstrate Snell's law laser refraction and total internal reflection", "Snell", "sin(θ"),
        ("show ideal gas molecules in a piston cylinder", "Ideal Gas", "N*k_B*T"),
        ("explain electric dipole field lines and equipotential surfaces", "3D Interactive Lab", "Symplectic"),
    ]

    for prompt, expected_concept_substr, expected_law_substr in prompts_and_expectations:
        res = client.post("/api/generate", json={"prompt": prompt})
        assert res.status_code == 200, f"Failed on prompt: {prompt}"
        payload = res.json()
        assert payload["verification"]["passed"] is True, f"Verification failed on {prompt}: {payload['verification']}"
        assert expected_concept_substr.lower() in payload["curriculum"]["concept"].lower(), (
            f"Expected '{expected_concept_substr}' in '{payload['curriculum']['concept']}' for prompt '{prompt}'"
        )
        combined_audit_text = (
            payload["physics_accuracy_check"]["verified_law"]
            + " "
            + payload["physics_accuracy_check"]["required_solver"]
            + " "
            + " ".join(payload["physics_accuracy_check"].get("conservation_invariants", []))
        ).lower()
        assert expected_law_substr.lower() in combined_audit_text, (
            f"Expected '{expected_law_substr}' in '{combined_audit_text}' for prompt '{prompt}'"
        )
        assert "ArrowHelper" in payload["html"], f"Missing 3D vector ArrowHelper in {prompt}"
        # Ensure ZERO combining right arrow characters (U+20D7) anywhere in response
        raw_text = res.text
        assert "\u20d7" not in raw_text, f"Found U+20D7 combining arrow in response for: {prompt}"

    print("✓ Universal Physics Compiler (Ramp/FBD, Spring SHM, Collisions, Torque, Optics, Ideal Gas, Custom) & Zero U+20D7 verified!")


if __name__ == "__main__":
    test_presets_verification()
    test_auto_instrumentation()
    test_voice_to_3d_magnetic_flux_and_rutherford()
    test_ferpa_pii_redaction_gate()
    test_fastapi_endpoints()
    test_universal_physics_concepts_and_zero_missing_glyphs()
    print("\n🎉 ALL TRACK A VERIFICATION TESTS PASSED!")
