"""FastAPI backend. Run: uvicorn app.api.main:app --reload --port 8000"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.db.db_manager import (
    add_turn,
    create_encounter,
    get_summary,
    get_turns,
    get_metrics,
    init_db,
    save_metrics,
    save_summary,
    update_encounter_state,
    update_encounter_status,
)
from app.engine.intake_engine import IntakeEngine, load_complaint, load_shared, project_root
from app.engine.module_runner import ModuleRunner
from app.engine.ros_runner import ROSRunner
from app.engine.summary_engine import ai_summarize, format_summary_text, generate_template_summary

ROOT = project_root()
COMPLAINTS_DIR = os.path.join(ROOT, "complaints_modules", "complaints")
# Modules are stored directly under complaints_modules/, not in a subdirectory.
MODULES_DIR = os.path.join(ROOT, "complaints_modules")
INDEX_PATH = os.path.join(ROOT, "complaints_modules", "index_v2.json")
SHARED = load_shared()

app = FastAPI(title="Clinical Intake API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_db()

_sessions: Dict[int, Dict[str, Any]] = {}


class StartReq(BaseModel):
    complaint_id: str
    patient_age: int
    patient_sex: str
    secondary_complaint: Optional[str] = None


class AnswerReq(BaseModel):
    question_id: str
    field: str
    answer: str
    phase: str


class DoctorSummaryReq(BaseModel):
    post_summary: str


def _load_index() -> Dict[str, Any]:
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _session_or_404(sid: int) -> Dict[str, Any]:
    if sid not in _sessions:
        raise HTTPException(404, "Session not found")
    return _sessions[sid]


def _phase_next(sess: Dict[str, Any]):
    phase = sess["phase"]
    if phase == "complaint":
        q = sess["engine"].get_next_question()
        if q is None:
            sess["phase"] = "ros"
            return _phase_next(sess)
        return q
    if phase == "ros":
        if sess["ros_runner"] is None:
            sess["ros_runner"] = ROSRunner(
                sess["engine"].state,
                sess["engine"].patient,
                sess["engine"].complaint,
                SHARED,
            )
        q = sess["ros_runner"].get_next_question()
        if q is None:
            sess["phase"] = "modules"
            return _phase_next(sess)
        return q
    if phase == "modules":
        if sess["module_runner"] is None:
            idx = _load_index()
            entry = next(
                (
                    c
                    for c in idx["active_complaints"]
                    if c["complaint_id"] == sess["engine"].complaint.get("complaint_id")
                ),
                {},
            )
            cond_mods = entry.get("conditional_session_modules", [])
            sess["module_runner"] = ModuleRunner(
                MODULES_DIR,
                sess["engine"].state,
                sess["engine"].patient,
                sess["engine"].complaint.get("complaint_id", ""),
                cond_mods,
                SHARED,
            )
        q = sess["module_runner"].get_next_question()
        if q is None:
            sess["phase"] = "complete_ready"
            return None
        return q
    return None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/complaints")
def list_complaints():
    result = []
    for fn in os.listdir(COMPLAINTS_DIR):
        if not fn.endswith("_v2.json"):
            continue
        with open(os.path.join(COMPLAINTS_DIR, fn), "r", encoding="utf-8") as f:
            data = json.load(f)
        result.append(
            {
                "complaint_id": data.get("complaint_id", fn.replace("_v2.json", "")),
                "display_name": data.get("display_name", ""),
                "primary_system": data.get("primary_system", ""),
                "question_count": len(data.get("questions_by_id", {})),
                "budget_target": data.get("question_budget", {})
                .get("primary_mode", {})
                .get("target_question_budget", 0),
            }
        )
    return sorted(result, key=lambda x: x["display_name"])


@app.post("/sessions")
def start_session(req: StartReq):
    try:
        complaint_data = load_complaint(req.complaint_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, f"Complaint {req.complaint_id} not found") from exc

    eligibility = complaint_data.get("eligibility", {})
    allowed_sexes = [str(x).lower() for x in eligibility.get("allowed_patient_sex", [])]
    if allowed_sexes and str(req.patient_sex).lower() not in allowed_sexes:
        raise HTTPException(
            400,
            eligibility.get(
                "message",
                "Selected complaint is not eligible for the chosen patient sex.",
            ),
        )

    engine = IntakeEngine(
        complaint_data, {"age": req.patient_age, "sex": req.patient_sex}, SHARED
    )
    engine.state["secondary_complaints"] = req.secondary_complaint or "None reported"

    session_name = (
        f"sess_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{req.complaint_id}"
    )
    session_id = create_encounter(
        session_name,
        req.complaint_id,
        req.patient_age,
        req.patient_sex,
        req.secondary_complaint or "[]",
    )
    _sessions[session_id] = {
        "engine": engine,
        "ros_runner": None,
        "module_runner": None,
        "phase": "complaint",
        "patient_age": req.patient_age,
        "patient_sex": req.patient_sex,
    }
    next_q = _phase_next(_sessions[session_id])
    return {
        "session_id": session_id,
        "next_question": next_q,
        "progress": engine.get_progress(),
        "phase": _sessions[session_id]["phase"],
    }


@app.get("/sessions/{sid}/next")
def next_question(sid: int):
    sess = _session_or_404(sid)
    nxt = _phase_next(sess)
    return {
        "next_question": nxt,
        "progress": sess["engine"].get_progress(),
        "phase": sess["phase"],
    }


def _lookup_question_text(
    sess: Dict[str, Any], phase: str, question_id: str, field: str
) -> str:
    """Resolve a human-readable question text for transcript logging."""
    if phase == "complaint":
        q = sess["engine"].questions.get(question_id, {})
        return q.get("text", "") or question_id
    if phase == "ros" and sess.get("ros_runner") is not None:
        q = sess["ros_runner"].questions.get(question_id, {})
        return q.get("text", "") or question_id
    if phase == "modules" and sess.get("module_runner") is not None:
        text = sess["module_runner"].get_question_text(field)
        if text:
            return text
    return question_id


def _full_question_dict(
    sess: Dict[str, Any], phase: str, question_id: str, field: str
) -> Dict[str, Any]:
    """Return the full question definition so record_answer sees detail_field,
    canonical_concept, response_type, etc. The UI only sends back {id, field, phase}."""
    if phase == "ros" and sess.get("ros_runner") is not None:
        q = sess["ros_runner"].questions.get(question_id)
        if q:
            return {
                "id": question_id,
                "field": q.get("field", field),
                "phase": phase,
                "response_type": q.get("response_type"),
                "canonical_concept": q.get("canonical_concept"),
                "detail_field": q.get("detail_field"),
            }
    if phase == "modules" and sess.get("module_runner") is not None:
        q = sess["module_runner"].get_question_definition(field)
        if q:
            return q
    return {"id": question_id, "field": field, "phase": phase}


@app.post("/sessions/{sid}/answer")
def answer_question(sid: int, req: AnswerReq):
    sess = _session_or_404(sid)
    phase = sess["phase"]
    if phase == "complaint":
        turn = sess["engine"].record_answer(
            req.question_id, req.field, req.answer, req.phase
        )
    elif phase == "ros":
        q = _full_question_dict(sess, "ros", req.question_id, req.field)
        sess["ros_runner"].record_answer(q, req.answer)
        turn = {"extracted_bonus_fields": {}}
    elif phase == "modules":
        q = _full_question_dict(sess, "modules", req.question_id, req.field)
        sess["module_runner"].record_answer(q, req.answer)
        turn = {"extracted_bonus_fields": {}}
    else:
        raise HTTPException(400, "Session is not accepting answers")

    question_text = _lookup_question_text(sess, phase, req.question_id, req.field)
    add_turn(sid, "system", question_text, req.question_id, req.phase)
    add_turn(sid, "patient", req.answer, req.question_id, req.phase)
    nxt = _phase_next(sess)
    return {
        "next_question": nxt,
        "progress": sess["engine"].get_progress(),
        "phase": sess["phase"],
        "extracted_bonus": turn.get("extracted_bonus_fields", {}),
    }


@app.post("/sessions/{sid}/skip")
def skip_question(sid: int, req: AnswerReq):
    sess = _session_or_404(sid)
    if sess["phase"] != "complaint":
        raise HTTPException(400, "Skipping is only supported during complaint clerking")
    turn = sess["engine"].skip_question(req.question_id, req.field, req.phase)
    question_text = _lookup_question_text(sess, "complaint", req.question_id, req.field)
    add_turn(sid, "system", question_text, req.question_id, req.phase)
    add_turn(sid, "patient", "not_assessed", req.question_id, req.phase)
    nxt = _phase_next(sess)
    return {
        "next_question": nxt,
        "progress": sess["engine"].get_progress(),
        "phase": sess["phase"],
        "turn": turn,
    }


@app.post("/sessions/{sid}/complete")
def complete_session(sid: int):
    sess = _session_or_404(sid)
    if sess["phase"] != "complete_ready":
        # Exhaust any remaining steps first
        nxt = _phase_next(sess)
        if nxt is not None:
            return {
                "next_question": nxt,
                "phase": sess["phase"],
                "progress": sess["engine"].get_progress(),
            }

    engine = sess["engine"]
    engine.completed = True
    summary = generate_template_summary(engine)
    # Add patient age/sex for the summary formatter
    summary["patient_age"] = sess["patient_age"]
    summary["patient_sex"] = sess["patient_sex"]
    pre = format_summary_text(summary)
    ai = ai_summarize(engine.state, summary)
    save_summary(sid, pre_summary=pre, ai_summary=ai)

    # Required fields come from the complaint's active profile.
    # Count both total and filled against the SAME set so completion_rate
    # stays in [0.0, 1.0].
    required_fields = {
        engine.questions.get(qid, {}).get("field", qid)
        for ids in engine.current_profile_data.values()
        for qid in ids
    }
    total = max(len(required_fields), 1)
    filled = sum(
        1
        for f in required_fields
        if engine.state.get(f) not in (None, "", "not_assessed")
    )
    all_turns = get_turns(sid)
    patient_turns = sum(1 for t in all_turns if t.get("speaker") == "patient")
    system_turns = sum(1 for t in all_turns if t.get("speaker") == "system")
    save_metrics(
        sid,
        {
            "patient_turn_count": patient_turns,
            "system_turn_count": system_turns,
            "required_fields_total": total,
            "required_fields_filled": filled,
            "completion_rate": round(filled / total, 3),
            "missing_fields_count": len(summary.get("missing_clarifications", [])),
            "missing_fields": json.dumps(summary.get("missing_clarifications", [])),
            "summary_length": len(pre),
        },
    )
    update_encounter_status(sid, "completed", ended_at=datetime.utcnow().isoformat())
    update_encounter_state(
        sid,
        engine.state,
        summary.get("pertinent_positives", []),
        summary.get("pertinent_negatives", []),
        engine.escalation_level,
    )

    return {
        "template_summary": summary,
        "pre_summary": pre,
        "ai_summary": ai,
        "extracted_state": engine.state,
        "progress": engine.get_progress(),
        "phase": "completed",
    }


@app.get("/sessions/{sid}")
def get_session(sid: int):
    sess = _session_or_404(sid)
    engine = sess["engine"]
    return {
        "state": engine.state,
        "turns": engine.turns,
        "red_flags": engine.red_flags,
        "escalation": engine.escalation_level,
        "progress": engine.get_progress(),
        "phase": sess["phase"],
        "summary": get_summary(sid),
    }


@app.put("/sessions/{sid}/doctor-summary")
def save_doctor_summary(sid: int, req: DoctorSummaryReq):
    _session_or_404(sid)
    save_summary(
        sid, post_summary=req.post_summary, reviewed_at=datetime.utcnow().isoformat()
    )
    update_encounter_status(sid, "reviewed")
    return {"status": "saved"}


@app.get("/sessions/{sid}/transcript")
def get_transcript(sid: int):
    _session_or_404(sid)
    return {"turns": get_turns(sid)}


@app.get("/sessions/{sid}/metrics")
def get_session_metrics(sid: int):
    _session_or_404(sid)
    metrics = get_metrics(sid)
    return metrics or {}

@app.post("/sessions/{sid}/abandon")
def abandon_session(sid: int):
    sess = _session_or_404(sid)
    update_encounter_status(sid, "abandoned", ended_at=datetime.utcnow().isoformat())
    if sid in _sessions:
        del _sessions[sid]
    return {"status": "abandoned"}

@app.post("/sessions/{sid}/force_complete")
def force_complete(sid: int):
    sess = _session_or_404(sid)
    engine = sess["engine"]
    engine.completed = True
    summary = generate_template_summary(engine)
    pre = format_summary_text(summary)
    ai = ai_summarize(engine.state, summary)
    save_summary(sid, pre_summary=pre, ai_summary=ai)
    update_encounter_status(sid, "force_completed", ended_at=datetime.utcnow().isoformat())
    update_encounter_state(sid, engine.state, summary.get("pertinent_positives", []), summary.get("pertinent_negatives", []), engine.escalation_level)
    return {
        "template_summary": summary,
        "pre_summary": pre,
        "ai_summary": ai,
        "phase": "completed",
    }
