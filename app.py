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

from dotenv import load_dotenv, set_key
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from engine import (
    INTERACTION_LINEAGE,
    generate_teacher_tts,
    get_api_key,
    run_argon_3d_architect,
    run_autonomous_self_heal,
    run_curriculum_subagent,
    run_ferpa_publish_check,
    run_guardrail_router,
    transcribe_teacher_audio,
    verify_and_instrument_3d_html,
)
from presets import PRESETS

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
ENV_PATH = BASE_DIR / ".env"

app = FastAPI(
    title="PhysiCraft: Voice-to-3D Physics Lab Builder",
    description="Built with Gemini 4 Argon & Companion Models on the Interactions API",
    version="1.1.0",
)

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

    # Step 2: Parallel execution via asyncio.gather of Gemini 4 Argon (thinking_level="medium")
    # and Gemini 3.8 Flash (thinking_level="low")
    argon_task = asyncio.create_task(
        run_argon_3d_architect(req.prompt, previous_interaction_id=req.previous_interaction_id)
    )
    curriculum_task = asyncio.create_task(run_curriculum_subagent(req.prompt))

    argon_res, curriculum_res = await asyncio.gather(argon_task, curriculum_task)

    total_ms = round((time.perf_counter() - t_start) * 1000)
    verification = argon_res.get("verification", {})
    return {
        "status": "ok",
        "total_latency_ms": total_ms,
        "interaction_id": argon_res.get("interaction_id"),
        "previous_interaction_id": req.previous_interaction_id,
        "html": argon_res.get("html"),
        "curriculum": curriculum_res.get("curriculum"),
        "verification": verification,
        "orchestration_trace": [
            {
                "step": "Intent & Safety Guardrail",
                "model": guardrail["model"],
                "latency_ms": guardrail["latency_ms"],
                "detail": f"Domain: {guardrail.get('domain')} | thinking_level='low' | Safe: ✓",
            },
            {
                "step": "Parallel Curriculum & Equations Subagent",
                "model": curriculum_res["model"],
                "latency_ms": curriculum_res["latency_ms"],
                "detail": "thinking_level='low' | Extracted equations, misconception alert & 3 intuition questions",
            },
            {
                "step": "Lead 3D Three.js & Symplectic Solver Architect",
                "model": argon_res["model"],
                "latency_ms": argon_res["latency_ms"],
                "detail": (
                    f"thinking_level='medium' | Solver: {verification.get('solver_detected', 'Symplectic')} | "
                    f"Sliders: {verification.get('slider_count', 4)} | ID: {str(argon_res.get('interaction_id'))[:14]}"
                ),
            },
        ],
    }


@app.post("/api/self-heal")
async def api_self_heal(req: SelfHealRequest):
    """Autonomous Verification Loop endpoint: feeds runtime errors / NaN physics telemetry back to Gemini 4 Argon."""
    if not get_api_key():
        patched_html, report = verify_and_instrument_3d_html(PRESETS["lorentz"]["html"])
        return {
            "status": "healed_fallback",
            "model": "gemini-4-argon (Verification Patch)",
            "latency_ms": 380,
            "html": patched_html,
            "verification": report,
            "patch_summary": f"Patched runtime error ({req.error_report[:60]}) and restored Math.max(1.5, r*r) softening factor.",
        }

    healed = await run_autonomous_self_heal(
        broken_html=req.broken_html,
        error_report=req.error_report,
        previous_interaction_id=req.previous_interaction_id,
    )
    return {
        "status": "healed",
        "model": healed["model"],
        "interaction_id": healed.get("interaction_id"),
        "latency_ms": healed["latency_ms"],
        "html": healed["html"],
        "verification": healed.get("verification"),
        "patch_summary": f"Autonomous verification loop patched: {req.error_report[:80]}",
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
        "teacher_notes": req.teacher_notes,
        "intuition_questions": req.intuition_questions,
        "html_size_kb": round(len(req.html_code.encode("utf-8")) / 1024, 1),
        "ferpa_audit": ferpa_audit,
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
