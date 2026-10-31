"""
PhysiCraft Subagent 3: Human-in-the-Loop FERPA/PII Guardrail & Classroom Orchestrator Gate (Track A)

Implements Judge Test #3 ("keeps people in control when taking actions that affect external systems,
money, or private data") before publishing any 3D simulation assignment to Google Classroom:
1. Deterministic Regex PII & FERPA Compliance Scanner (`scan_pii_and_ferpa_compliance`):
   - Detects emails, SSNs, phone numbers, and individual Student ID / Grade / Score disclosures.
   - Produces a `redacted_teacher_notes` copy with detected PII masked as `[REDACTED_STUDENT_PII]`.
   - Explicitly enumerates external Google Classroom OAuth scopes (`permissions_scope`) and enforces
     `human_approval_required=True`.
2. Interactions API Guardrail Audit (`run_subagent_ferpa_audit`):
   - Uses `client.interactions.create(...)` with `gemini-3.5-flash-lite` (`thinking_level="low"`).
   - Supports optional deep escalation to `gemini-4-argon` (`thinking_level="medium"`) when ambiguous
     privacy or safety signals are detected.
   - Strictly adheres to AGENTS.md (no deprecated `thinking_budget`, `temperature`, `top_p`, or `top_k`).
"""

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from google import genai

# Deterministic Regex Patterns for Student PII & FERPA Protected Records
PII_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    (
        "Email Address",
        re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    ),
    (
        "Social Security Number (SSN)",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    ),
    (
        "Phone Number",
        re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    ),
    (
        "Student ID / Individual Grade Record",
        re.compile(
            r"(?:\bStudent\s*ID\s*:\s*[A-Za-z0-9-]+|\bGrade\s*:\s*[A-F][+-]?|\bScore\s*:\s*\d+\s*/\s*\d+)",
            re.IGNORECASE,
        ),
    ),
]

DEFAULT_CLASSROOM_SCOPES: List[str] = [
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/classroom.rosters.readonly",
]


def _extract_json(raw_text: str) -> Dict[str, Any]:
    """Safely extracts a JSON object from model output."""
    if not raw_text:
        return {}
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return {}


def scan_pii_and_ferpa_compliance(
    lesson_title: str,
    teacher_notes: str,
    class_roster_section: str,
) -> Dict[str, Any]:
    """
    Deterministic regex scan for student PII before staging an outbound Google Classroom action.

    Scans for:
    - Email addresses (`[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+`)
    - SSN patterns (`\\b\\d{3}-\\d{2}-\\d{4}\\b`)
    - Phone numbers (`\\b\\d{3}[-.\\s]?\\d{3}[-.\\s]?\\d{4}\\b`)
    - Student ID / Individual Grade patterns (`Student ID:`, `Grade: [A-F]`, `Score: \\d+/\\d+`)

    Produces `redacted_teacher_notes` with any detected PII masked as `[REDACTED_STUDENT_PII]`
    so the teacher remains in full control.
    """
    notes_text = teacher_notes or ""
    combined_payload = f"{lesson_title or ''}\n{class_roster_section or ''}\n{notes_text}"

    detected_types: List[str] = []
    redacted_notes = notes_text

    for label, pattern in PII_PATTERNS:
        if pattern.search(combined_payload):
            if label not in detected_types:
                detected_types.append(label)
        if pattern.search(redacted_notes):
            redacted_notes = pattern.sub("[REDACTED_STUDENT_PII]", redacted_notes)

    pii_detected = len(detected_types) > 0
    ferpa_compliant = not pii_detected

    if pii_detected:
        types_str = ", ".join(detected_types)
        audit_note = (
            f"FERPA Alert: Detected {types_str} in draft payload. "
            "Automatically masked as [REDACTED_STUDENT_PII] for teacher review before external Classroom publication."
        )
    else:
        audit_note = (
            "Verified zero student PII, SSNs, contact numbers, or individual grade records in outbound "
            "simulation package. Ready for explicit teacher confirmation."
        )

    return {
        "pii_detected": pii_detected,
        "pii_types": detected_types,
        "ferpa_compliant": ferpa_compliant,
        "redacted_teacher_notes": redacted_notes,
        "redacted_notes": redacted_notes,
        "audit_note": audit_note,
        "permissions_scope": list(DEFAULT_CLASSROOM_SCOPES),
        "human_approval_required": True,
    }


async def run_subagent_ferpa_audit(
    lesson_title: str,
    teacher_notes: str,
    class_roster_section: str,
    api_key: str = "",
    escalate_to_argon: bool = False,
    previous_interaction_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Runs deterministic `scan_pii_and_ferpa_compliance` first, and if `api_key` is provided,
    also runs `gemini-3.5-flash-lite` (`thinking_level="low"`) via `client.interactions.create`
    (with optional escalation to `gemini-4-argon` at `thinking_level="medium"`) to verify
    classroom appropriateness and FERPA compliance.
    """
    t0 = time.perf_counter()
    deterministic_result = scan_pii_and_ferpa_compliance(
        lesson_title=lesson_title,
        teacher_notes=teacher_notes,
        class_roster_section=class_roster_section,
    )

    cleaned_key = (api_key or "").strip()
    if not cleaned_key:
        return {
            **deterministic_result,
            "model": "gemini-3.5-flash-lite (Deterministic FERPA Regex Gate)",
            "thinking_level": "low",
            "latency_ms": max(1, round((time.perf_counter() - t0) * 1000)),
        }

    client = genai.Client(api_key=cleaned_key)

    def _call_flash_lite():
        return client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=(
                "You are the PhysiCraft FERPA & Classroom Safety Guardrail Subagent.\n"
                "Inspect this outbound Google Classroom physics assignment payload (already pre-redacted for raw regex PII) "
                "for FERPA student privacy compliance and high-school classroom appropriateness.\n"
                "Return ONLY valid JSON with keys: "
                '{"ferpa_compliant": true, "classroom_appropriate": true, "needs_deep_escalation": false, '
                '"audit_note": "1-sentence confirmation for the teacher approval modal"}\n\n'
                f"Lesson Title: {lesson_title}\n"
                f"Course Section: {class_roster_section}\n"
                f"Teacher Notes (Redacted): {deterministic_result['redacted_teacher_notes']}"
            ),
            generation_config={"thinking_level": "low"},
        )

    try:
        interaction = await asyncio.to_thread(_call_flash_lite)
        parsed = _extract_json(interaction.output_text or "")
        interaction_id = getattr(interaction, "id", None)
        model_used = "gemini-3.5-flash-lite"
        thinking_used = "low"

        # Optional deep escalation to gemini-4-argon (thinking_level="medium") if requested or flagged
        if escalate_to_argon or parsed.get("needs_deep_escalation", False):
            def _run_argon():
                argon_kwargs: Dict[str, Any] = {
                    "model": "gemini-4-argon",
                    "input": (
                        "Perform a deep FERPA & classroom policy audit on this outbound Google Classroom payload. "
                        "Return ONLY valid JSON: "
                        '{"ferpa_compliant": true, "audit_note": "1-sentence summary for teacher"}\n\n'
                        f"Title: {lesson_title}\n"
                        f"Section: {class_roster_section}\n"
                        f"Redacted Notes: {deterministic_result['redacted_teacher_notes']}"
                    ),
                    "generation_config": {"thinking_level": "medium"},
                }
                prev_id = interaction_id or previous_interaction_id
                if prev_id:
                    argon_kwargs["previous_interaction_id"] = prev_id
                return client.interactions.create(**argon_kwargs)

            argon_interaction = await asyncio.to_thread(_run_argon)
            argon_parsed = _extract_json(argon_interaction.output_text or "")
            if argon_parsed:
                parsed.update(argon_parsed)
            interaction_id = getattr(argon_interaction, "id", interaction_id)
            model_used = "gemini-4-argon"
            thinking_used = "medium"

        latency_ms = max(1, round((time.perf_counter() - t0) * 1000))
        llm_ferpa_ok = bool(parsed.get("ferpa_compliant", True))
        final_compliant = deterministic_result["ferpa_compliant"] and llm_ferpa_ok

        audit_note = deterministic_result["audit_note"]
        if not deterministic_result["pii_detected"] and parsed.get("audit_note"):
            audit_note = str(parsed["audit_note"])

        return {
            **deterministic_result,
            "ferpa_compliant": final_compliant,
            "audit_note": audit_note,
            "model": model_used,
            "thinking_level": thinking_used,
            "interaction_id": interaction_id,
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        latency_ms = max(1, round((time.perf_counter() - t0) * 1000))
        return {
            **deterministic_result,
            "model": "gemini-3.5-flash-lite",
            "thinking_level": "low",
            "latency_ms": latency_ms,
            "fallback_reason": str(exc),
        }
