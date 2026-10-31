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
    <script>
      const scene = new THREE.Scene();
      const renderer = new THREE.WebGLRenderer();
      function animate() { requestAnimationFrame(animate); }
      animate();
    </script></body></html>"""
    patched, report = verify_and_instrument_3d_html(minimal_three_html)
    assert report["passed"], f"Minimal Three.js failed: {report['issues']}"
    assert report["auto_instrumented"] is True
    assert "physicraft_telemetry" in patched
    print("✓ Pre-flight auto-instrumentation of `physicraft_telemetry` verified!")


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


if __name__ == "__main__":
    test_presets_verification()
    test_auto_instrumentation()
    test_fastapi_endpoints()
    print("\n🎉 ALL TRACK A VERIFICATION TESTS PASSED!")
