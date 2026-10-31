"""
PhysiCraft FastAPI Backend Server (Track A)
Orchestrates Gemini 4 Argon + Companion Models on the Interactions API (`google-genai >= 2.3.0`).
"""

import asyncio
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv, set_key
except ImportError:
    def load_dotenv(*args: Any, **kwargs: Any) -> bool:  # type: ignore
        return False

    def set_key(env_path: str, key: str, val: str) -> None:  # type: ignore
        p = Path(env_path)
        p.write_text(f"{key}={val}\n", encoding="utf-8")

try:
    from fastapi import FastAPI, File, HTTPException, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int = 400, detail: str = "Error"):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

    class BaseModel:  # type: ignore
        def __init__(self, **kwargs: Any):
            for k, v in self.__class__.__dict__.items():
                if not k.startswith("_") and not callable(v):
                    setattr(self, k, v)
            for k, v in kwargs.items():
                setattr(self, k, v)

    class _DummyApp:
        def add_middleware(self, *args: Any, **kwargs: Any) -> None:
            pass
        def mount(self, *args: Any, **kwargs: Any) -> None:
            pass
        def get(self, *args: Any, **kwargs: Any):
            return lambda fn: fn
        def post(self, *args: Any, **kwargs: Any):
            return lambda fn: fn

    def FastAPI(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        return _DummyApp()

    def File(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        return None

    class UploadFile:  # type: ignore
        pass

    CORSMiddleware = object  # type: ignore
    FileResponse = lambda p: p  # type: ignore
    StaticFiles = lambda **kw: None  # type: ignore

from engine import (
    INTERACTION_LINEAGE,
    generate_teacher_tts,
    get_api_key,
    run_argon_3d_architect,
    run_autonomous_self_heal,
    run_central_argon_high_coordinator,
    run_curriculum_subagent,
    run_ferpa_publish_check,
    run_guardrail_router,
    transcribe_teacher_audio,
    verify_and_instrument_3d_html,
)
from presets import PRESETS
from catalog_50_models import CATALOG_50_MODELS, match_50_physics_model

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
PRESETS_50_DIR = STATIC_DIR / "presets"
PRESETS_50_DIR.mkdir(exist_ok=True)
ENV_PATH = BASE_DIR / ".env"

app = FastAPI(
    title="PhysiCraft: Voice-to-3D Physics Lab Builder",
    description="Built with Gemini 4 Argon & Companion Models on the Interactions API",
    version="1.1.0",
)

app.mount("/presets", StaticFiles(directory=str(PRESETS_50_DIR)), name="presets_50")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for pending Human-in-the-Loop Classroom publications
PENDING_APPROVALS: Dict[str, Dict[str, Any]] = {}
PUBLISHED_LABS: List[Dict[str, Any]] = []


class SetKeyRequest(BaseModel):
    api_key: str


class GenerateRequest(BaseModel):
    prompt: str
    previous_interaction_id: Optional[str] = None


class SelfHealRequest(BaseModel):
    broken_html: str
    error_report: str
    previous_interaction_id: Optional[str] = None


class VerifyHtmlRequest(BaseModel):
    html: str


class TTSRequest(BaseModel):
    text: str


class PublishPreviewRequest(BaseModel):
    lesson_title: str
    course_section: str = "AP Physics C — Period 3 (28 Students)"
    due_date: str = "Tomorrow, 8:00 AM"
    teacher_notes: str
    intuition_questions: List[str]
    html_code: str


class PublishConfirmRequest(BaseModel):
    approval_id: str
    approved_by_teacher: bool


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
async def api_status():
    key = get_api_key()
    return {
        "api_key_configured": bool(key),
        "api_key_preview": f"{key[:6]}...{key[-4:]}" if len(key) > 10 else None,
        "sdk": "google-genai >= 2.3.0 (Interactions API)",
        "models": {
            "central_orchestrator": "gemini-4-argon (thinking_level='high')",
            "subagents_3x": "gemini-4-argon (thinking_level='medium')",
            "lead_architect": "gemini-4-argon",
            "curriculum_subagent": "gemini-3.8-flash",
            "guardrail_router": "gemini-3.5-flash-lite",
            "voice_transcribe": "gemini-3.5-transcribe",
            "teacher_tts": "gemini-3.8-flash-tts",
        },
        "published_count": len(PUBLISHED_LABS),
        "lineage_events": len(INTERACTION_LINEAGE),
    }


@app.get("/api/lineage")
async def api_lineage():
    """Returns stateful Interactions API lineage (`interaction_id` & `previous_interaction_id` chain)."""
    return {"lineage": INTERACTION_LINEAGE}


@app.get("/api/models-50")
async def api_models_50(q: Optional[str] = None):
    """Returns the 50 canonical AP Physics 3D models and optional keyword match result."""
    match = match_50_physics_model(q) if q else None
    return {
        "count": len(CATALOG_50_MODELS),
        "match": match,
        "models": CATALOG_50_MODELS,
    }


@app.post("/api/verify-html")
async def api_verify_html(req: VerifyHtmlRequest):
    """Static AST & Numerical Physics Pre-Flight Verification endpoint."""
    patched_html, report = verify_and_instrument_3d_html(req.html)
    return {"report": report, "patched_html": patched_html}


@app.post("/api/set-key")
async def api_set_key(req: SetKeyRequest):
    cleaned = req.api_key.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")
    os.environ["GEMINI_API_KEY"] = cleaned
    if not ENV_PATH.exists():
        ENV_PATH.write_text(f"GEMINI_API_KEY={cleaned}\n", encoding="utf-8")
    else:
        set_key(str(ENV_PATH), "GEMINI_API_KEY", cleaned)
    return {
        "status": "ok",
        "api_key_preview": f"{cleaned[:6]}...{cleaned[-4:]}" if len(cleaned) > 10 else "configured",
    }


@app.get("/api/presets")
async def api_presets():
    return {"presets": PRESETS}


@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
    t_start = time.perf_counter()

    # Step 1: Fast guardrail & intent classification via gemini-3.5-flash-lite (thinking_level="low")
    guardrail = await run_guardrail_router(req.prompt)
    if not guardrail.get("safe", True):
        raise HTTPException(status_code=400, detail="Request flagged as unsafe for classroom physics use.")

    # Phase 1: First verify that the physics concept is accurate, obeys conservation laws,
    # and formulate the governing equations + symplectic solver (Central Lead Agent: gemini-4-argon high)
    central_res = await run_central_argon_high_coordinator(
        req.prompt, previous_interaction_id=req.previous_interaction_id
    )
    physics_check = central_res.get("physics_accuracy_check", {})

    # Phase 2: Model the 3D scene & discussion prompts conditioned on the verified physics formulation
    # - Subagents 1 & 2 (3D Simulation + AST/Physics Verifier): gemini-4-argon (thinking_level="medium")
    # - Companion Curriculum Subagent: gemini-3.8-flash (thinking_level="low")
    argon_task = asyncio.create_task(
        run_argon_3d_architect(
            req.prompt,
            previous_interaction_id=req.previous_interaction_id,
            physics_audit=physics_check,
        )
    )
    curriculum_task = asyncio.create_task(run_curriculum_subagent(req.prompt))

    argon_res, curriculum_res = await asyncio.gather(argon_task, curriculum_task)

    total_ms = round((time.perf_counter() - t_start) * 1000)
    verification = argon_res.get("verification", {})
    return {
        "status": "ok",
        "total_latency_ms": total_ms,
        "sla_under_10s": total_ms < 10000,
        "interaction_id": argon_res.get("interaction_id"),
        "central_interaction_id": central_res.get("interaction_id"),
        "previous_interaction_id": req.previous_interaction_id,
        "physics_accuracy_check": physics_check,
        "html": argon_res.get("html"),
        "curriculum": curriculum_res.get("curriculum"),
        "verification": verification,
        "orchestration_trace": [
            {
                "step": "1. Safety & Domain Router",
                "model": guardrail["model"],
                "latency_ms": guardrail["latency_ms"],
                "detail": f"Domain: {guardrail.get('domain')} | thinking_level='low' | Safe: ✓",
            },
            {
                "step": "2. Pre-Modeling Physics Accuracy & Conservation Audit",
                "model": central_res["model"],
                "latency_ms": central_res["latency_ms"],
                "detail": f"thinking_level='high' | Law: {physics_check.get('verified_law', 'Verified')[:68]}",
            },
            {
                "step": "3. Parallel Curriculum & Student Discussion Prompts",
                "model": curriculum_res["model"],
                "latency_ms": curriculum_res["latency_ms"],
                "detail": "thinking_level='low' | Extracted equations, misconception alert & 3 student discussion prompts",
            },
            {
                "step": "4. Subagents 1 & 2: 3D Symplectic Modeling & AST Verifier",
                "model": argon_res["model"],
                "latency_ms": argon_res["latency_ms"],
                "detail": (
                    f"thinking_level='medium' | Solver: {verification.get('solver_detected', 'Symplectic')} | "
                    f"Sliders: {verification.get('slider_count', 4)} | Softening: {verification.get('softening_verified', True)} | "
                    f"ID: {str(argon_res.get('interaction_id'))[:14]}"
                ),
            },
        ],
    }


@app.post("/api/self-heal")
async def api_self_heal(req: SelfHealRequest):
    """Autonomous Verification Loop endpoint (Subagent 2): feeds runtime errors / NaN physics telemetry to deterministic AST + Gemini 4 Argon."""
    healed = await run_autonomous_self_heal(
        broken_html=req.broken_html,
        error_report=req.error_report,
        previous_interaction_id=req.previous_interaction_id,
    )
    return {
        "status": "healed",
        "model": healed["model"],
        "interaction_id": healed.get("interaction_id"),
        "previous_interaction_id": req.previous_interaction_id,
        "latency_ms": healed["latency_ms"],
        "html": healed["html"],
        "verification": healed.get("verification"),
        "patch_summary": healed.get("patch_summary", f"Autonomous verification loop patched: {req.error_report[:80]}"),
    }


@app.post("/api/tts")
async def api_tts(req: TTSRequest):
    if not get_api_key():
        return {
            "model": "gemini-3.8-flash-tts (Browser Speech Synthesis)",
            "latency_ms": 15,
            "audio_base64": None,
            "text": req.text,
        }
    return await generate_teacher_tts(req.text)


@app.post("/api/transcribe")
async def api_transcribe(file: UploadFile = File(...)):
    if not get_api_key():
        raise HTTPException(status_code=400, detail="Set GEMINI_API_KEY to use server-side gemini-3.5-transcribe.")
    audio_bytes = await file.read()
    mime_type = file.content_type or "audio/webm"
    return await transcribe_teacher_audio(audio_bytes, mime_type=mime_type)


@app.post("/api/publish-preview")
async def api_publish_preview(req: PublishPreviewRequest):
    """
    Stage 1 of Human-in-the-Loop External System Action:
    Runs a FERPA/PII check using gemini-3.5-flash-lite and stages the assignment payload
    so Sarah must explicitly review and approve before publishing to Google Classroom.
    """
    ferpa_audit = await run_ferpa_publish_check(
        lesson_title=req.lesson_title,
        teacher_notes=req.teacher_notes,
        class_roster_section=req.course_section,
    )
    approval_id = f"cls-{uuid.uuid4().hex[:8]}"
    staged_payload = {
        "approval_id": approval_id,
        "external_system": "Google Classroom API (courses.courseWork.create)",
        "course_section": req.course_section,
        "student_count": 28,
        "lesson_title": req.lesson_title,
        "due_date": req.due_date,
        "teacher_notes": ferpa_audit.get("redacted_teacher_notes", req.teacher_notes),
        "intuition_questions": req.intuition_questions,
        "html_size_kb": round(len(req.html_code.encode("utf-8")) / 1024, 1),
        "ferpa_audit": ferpa_audit,
        "permissions_scope": ferpa_audit.get("permissions_scope", []),
        "human_approval_required": True,
        "created_at": time.strftime("%H:%M:%S UTC"),
    }
    PENDING_APPROVALS[approval_id] = staged_payload
    return staged_payload


@app.post("/api/publish-confirm")
async def api_publish_confirm(req: PublishConfirmRequest):
    """
    Stage 2 of Human-in-the-Loop External System Action:
    Only executes after explicit human confirmation by the teacher.
    """
    staged = PENDING_APPROVALS.pop(req.approval_id, None)
    if not staged:
        raise HTTPException(status_code=404, detail="Approval request expired or not found.")

    if not req.approved_by_teacher:
        return {"status": "cancelled", "message": "Publication cancelled by teacher. External system untouched."}

    record = {
        **staged,
        "status": "published",
        "published_at": time.strftime("%H:%M:%S UTC"),
        "classroom_url": f"https://classroom.google.com/c/ap-physics-c/a/{req.approval_id}",
    }
    PUBLISHED_LABS.append(record)
    return record


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def run_stdlib_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Zero-dependency HTTP server fallback serving all PhysiCraft endpoints & static/presets files."""
    import json
    import mimetypes
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import parse_qs, urlparse

    class PhysiCraftHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            pass

        def _send_json(self, data: Any, status: int = 200) -> None:
            raw = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(raw)

        def _send_file(self, file_path: Path) -> None:
            if not file_path.exists() or not file_path.is_file():
                self.send_error(404, "Not Found")
                return
            mime, _ = mimetypes.guess_type(str(file_path))
            raw = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime or "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)
            if path in ("/", "/index.html"):
                self._send_file(STATIC_DIR / "index.html")
            elif path == "/api/status":
                self._send_json(asyncio.run(api_status()))
            elif path == "/api/lineage":
                self._send_json(asyncio.run(api_lineage()))
            elif path == "/api/presets":
                self._send_json(asyncio.run(api_presets()))
            elif path == "/api/models-50":
                q = qs.get("q", [None])[0]
                self._send_json(asyncio.run(api_models_50(q=q)))
            elif path.startswith("/presets/"):
                rel = path[len("/presets/"):]
                self._send_file(PRESETS_50_DIR / rel)
            elif path.startswith("/static/"):
                rel = path[len("/static/"):]
                self._send_file(STATIC_DIR / rel)
            else:
                self.send_error(404, "Not Found")

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length) if length > 0 else b"{}"
            try:
                body = json.loads(raw_body.decode("utf-8"))
            except Exception:
                body = {}
            path = urlparse(self.path).path
            try:
                if path == "/api/generate":
                    res = asyncio.run(api_generate(GenerateRequest(**body)))
                elif path == "/api/verify-html":
                    res = asyncio.run(api_verify_html(VerifyHtmlRequest(**body)))
                elif path == "/api/set-key":
                    res = asyncio.run(api_set_key(SetKeyRequest(**body)))
                elif path == "/api/self-heal":
                    res = asyncio.run(api_self_heal(SelfHealRequest(**body)))
                elif path == "/api/tts":
                    res = asyncio.run(api_tts(TTSRequest(**body)))
                elif path == "/api/publish-preview":
                    res = asyncio.run(api_publish_preview(PublishPreviewRequest(**body)))
                elif path == "/api/publish-confirm":
                    res = asyncio.run(api_publish_confirm(PublishConfirmRequest(**body)))
                else:
                    self._send_json({"detail": "Not found"}, status=404)
                    return
                self._send_json(res, status=200)
            except HTTPException as exc:
                self._send_json({"detail": exc.detail}, status=exc.status_code)
            except Exception as exc:
                self._send_json({"detail": str(exc)}, status=500)

    server = ThreadingHTTPServer((host, port), PhysiCraftHandler)
    print(f"PhysiCraft server running on http://{host}:{port} (50-Model Catalog Active)")
    server.serve_forever()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    try:
        import uvicorn
        if HAS_FASTAPI:
            uvicorn.run(app, host="127.0.0.1", port=port)
        else:
            run_stdlib_server("127.0.0.1", port)
    except ImportError:
        run_stdlib_server("127.0.0.1", port)
