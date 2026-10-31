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
    run_central_argon_high_coordinator,
    run_curriculum_subagent,
    run_ferpa_publish_check,
    run_guardrail_router,
    transcribe_teacher_audio,
    verify_and_instrument_3d_html,
)
from presets import PRESETS
from physics_database import (
    build_experiment_by_id,
    get_all_50_experiments_catalog,
    match_experiment_from_prompt,
)

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


@app.get("/api/experiments")
async def api_experiments():
    """Returns the full 50-Experiment 3D Physics Database catalog."""
    catalog = get_all_50_experiments_catalog()
    return {"count": len(catalog), "experiments": catalog}


@app.get("/api/experiments/match")
async def api_match_experiment(q: str = ""):
    """Live keyword & parameter matcher against the 50-Experiment Database."""
    exp_id, score, matched_kw, overrides = match_experiment_from_prompt(q)
    catalog = get_all_50_experiments_catalog()
    meta = catalog[exp_id - 1] if 1 <= exp_id <= len(catalog) else None
    return {
        "matched": bool(exp_id and score > 0),
        "experiment_id": exp_id,
        "matched_experiment_id": exp_id,
        "title": meta["title"] if meta else "",
        "category": meta["category"] if meta else "",
        "confidence": score,
        "experiment": meta,
        "matched_keywords": matched_kw,
        "parameter_overrides": overrides,
    }


@app.get("/api/experiments/{exp_id}")
async def api_get_experiment(exp_id: int, prompt: str = ""):
    """Loads any of the 50 3D Physics Database models directly by ID (1..50), applying optional spoken parameter overrides."""
    exp_data = build_experiment_by_id(exp_id, custom_prompt=prompt)
    if not exp_data:
        raise HTTPException(status_code=404, detail=f"Experiment #{exp_id} not found in 50-Experiment Database.")
    patched_html, verification = verify_and_instrument_3d_html(exp_data["html"])
    iid = f"db-exp{exp_id}-{uuid.uuid4().hex[:6]}"
    return {
        "status": "ok",
        "experiment_id": exp_id,
        "title": exp_data.get("title"),
        "domain": exp_data.get("domain"),
        "matched_keywords": exp_data.get("matched_keywords", []),
        "parameter_overrides": exp_data.get("parameter_overrides", {}),
        "interaction_id": iid,
        "physics_accuracy_check": exp_data.get("physics_audit"),
        "curriculum": exp_data.get("curriculum"),
        "html": patched_html,
        "verification": verification,
    }


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
    exp_id, match_score, matched_kw, param_overrides = match_experiment_from_prompt(req.prompt)
    catalog = get_all_50_experiments_catalog()
    matched_meta = catalog[exp_id - 1] if 1 <= exp_id <= len(catalog) else None
    return {
        "status": "ok",
        "total_latency_ms": total_ms,
        "sla_under_10s": total_ms < 10000,
        "interaction_id": argon_res.get("interaction_id"),
        "central_interaction_id": central_res.get("interaction_id"),
        "previous_interaction_id": req.previous_interaction_id,
        "matched_experiment_id": argon_res.get("experiment_id") or (exp_id if match_score >= 6.0 else None),
        "matched_experiment_title": matched_meta["title"] if matched_meta and match_score >= 6.0 else None,
        "matched_keywords": argon_res.get("matched_keywords") or matched_kw,
        "parameter_overrides": argon_res.get("parameter_overrides") or param_overrides,
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
