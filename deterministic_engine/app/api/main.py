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
MODULES_DIR = os.path.join(ROOT, "complaints_modules", "modules")
INDEX_PATH = os.path.join(ROOT, "complaints_modules", "index_v2.json")
SHARED = load_shared()

app = FastAPI(title="Clinical Intake API", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_db()

_sessions: Dict[int, Dict[str, Any]] = {}

# -------------------- Pydantic models --------------------
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

class RosBatchAnswerReq(BaseModel):
    answers: Dict[str, str]          # field -> answer (e.g., "fever": "yes")
    details: Optional[Dict[str, str]] = None  # field -> detail text


# -------------------- Helpers --------------------
def _load_index() -> Dict[str, Any]:
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _session_or_404(sid: int) -> Dict[str, Any]:
    if sid not in _sessions:
        raise HTTPException(404, "Session not found")
    return _sessions[sid]


def _allowed_sexes_from_eligibility(eligibility: Dict[str, Any]) -> list[str]:
    allowed = [str(x).lower() for x in eligibility.get("allowed_patient_sex", [])]
    if allowed:
        return allowed
    sex_required = str(eligibility.get("sex_required", "")).strip().lower()
    return [sex_required] if sex_required else []



def _get_conditional_modules_for_complaint(complaint_id: str) -> list[str]:
    """Return conditional module names for a complaint from index_v2.json.

    General modules are always loaded by ModuleRunner from shared_v2.json /
    modules_dir. This only discovers conditional modules such as gynecologic or
    immunization history.
    """
    try:
        idx = _load_index()
    except Exception:
        return []
    cond_mods: list[str] = []
    for section_name in ("active_complaints", "complaint_registry"):
        section = idx.get(section_name)
        if isinstance(section, list):
            entry = next((c for c in section if c.get("complaint_id") == complaint_id), {})
            cond_mods = entry.get("conditional_session_modules", []) or entry.get("conditional_modules", [])
            if cond_mods or entry:
                break
    return cond_mods or []


def _ensure_module_runner(sess: Dict[str, Any]) -> ModuleRunner:
    """Create the module runner once and mark that the module phase was attempted.

    This protects the app from moving straight from ROS to complete_ready when a
    caller refreshes/continues at the phase boundary.
    """
    if sess.get("module_runner") is None:
        complaint_id = sess["engine"].complaint.get("complaint_id") or ""
        sess["module_runner"] = ModuleRunner(
            MODULES_DIR,
            sess["engine"].state,
            sess["engine"].patient,
            complaint_id,
            _get_conditional_modules_for_complaint(complaint_id),
            SHARED,
        )
    sess["modules_started"] = True
    return sess["module_runner"]

def _phase_next(sess: Dict[str, Any]):
    """
    Orchestrate the phases and return either a single question or a ROS batch.

    Order is strict:
      complaint -> ROS batch blocks -> history modules -> complete_ready

    The module phase is intentionally independent from the complaint question
    cap. General history modules (PMH/PSH, drug/allergy, social/family) must be
    attempted after ROS unless their fields were already captured.
    """
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
        batch = sess["ros_runner"].get_next_batch()
        if batch is None:
            sess["phase"] = "modules"
            return _phase_next(sess)
        return batch

    if phase == "modules":
        runner = _ensure_module_runner(sess)
        q = runner.get_next_question()
        if q is None:
            sess["modules_completed"] = True
            sess["phase"] = "complete_ready"
            return None
        return q

    return None


def _lookup_question_text(sess: Dict[str, Any], phase: str, question_id: str, field: str) -> str:
    """Helper to get display text for a question (for DB transcript)."""
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


def _full_question_dict(sess: Dict[str, Any], phase: str, question_id: str, field: str) -> Dict[str, Any]:
    """Get full question definition for answer recording."""
    if phase == "ros" and sess.get("ros_runner") is not None:
        q = sess["ros_runner"].questions.get(question_id)
        if q:
            return {
                "id": question_id,
                "field": q.get("field", field),
                "phase": phase,
                "response_type": q.get("response_type"),
                "canonical_concept": q.get("canonical_concept"),
                "dedup_family": q.get("dedup_family"),
                "dedup_families": q.get("dedup_families", []),
                "question_role": q.get("question_role", "ros_question"),
                "detail_field": q.get("detail_field"),
            }
    if phase == "modules" and sess.get("module_runner") is not None:
        q = sess["module_runner"].get_question_definition(field)
        if q:
            return q
    return {"id": question_id, "field": field, "phase": phase}


# -------------------- API Endpoints --------------------
@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/complaints')
def list_complaints():
    results_by_id: Dict[str, Dict[str, Any]] = {}
    if not os.path.exists(COMPLAINTS_DIR):
        return []
    for fn in os.listdir(COMPLAINTS_DIR):
        if not fn.endswith('.json'):
            continue
        path = os.path.join(COMPLAINTS_DIR, fn)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        complaint_id = data.get('complaint_id', fn.replace('_v2.json', '').replace('.json', ''))
        current = results_by_id.get(complaint_id)
        record = {
            'complaint_id': complaint_id,
            'display_name': data.get('display_name', complaint_id.replace('_', ' ').title()),
            'primary_system': data.get('primary_system', ''),
            'question_count': len(data.get('questions_by_id', {})),
            'budget_target': data.get('question_budget', {}).get('primary_mode', {}).get('target_question_budget', 0),
            'filename': fn,
        }
        if current is None or (current['filename'].endswith('_v2.json') and fn.endswith('.json') and not fn.endswith('_v2.json')):
            results_by_id[complaint_id] = record
    return sorted([
        {k: v for k, v in r.items() if k != 'filename'} for r in results_by_id.values()
    ], key=lambda x: x['display_name'])


@app.post('/sessions')
def start_session(req: StartReq):
    try:
        complaint_data = load_complaint(req.complaint_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, f'Complaint {req.complaint_id} not found') from exc
    eligibility = complaint_data.get('eligibility', {})
    allowed_sexes = _allowed_sexes_from_eligibility(eligibility)
    if allowed_sexes and str(req.patient_sex).lower() not in allowed_sexes:
        raise HTTPException(400, eligibility.get('message', 'Selected complaint is not eligible for the chosen patient sex.'))
    engine = IntakeEngine(complaint_data, {'age': req.patient_age, 'sex': req.patient_sex}, SHARED)
    engine.state['secondary_complaints'] = req.secondary_complaint or 'None reported'
    session_name = f"sess_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{req.complaint_id}"
    session_id = create_encounter(session_name, req.complaint_id, req.patient_age, req.patient_sex, req.secondary_complaint or '[]')
    _sessions[session_id] = {
        'engine': engine,
        'ros_runner': None,
        'module_runner': None,
        'phase': 'complaint',
        'patient_age': req.patient_age,
        'patient_sex': req.patient_sex,
        'modules_started': False,
        'modules_completed': False
    }
    next_item = _phase_next(_sessions[session_id])
    if isinstance(next_item, dict) and next_item.get('type') == 'ros_batch':
        return {'next_batch': next_item, 'session_id': session_id, 'progress': engine.get_progress(), 'phase': _sessions[session_id]['phase']}
    return {'next_question': next_item, 'session_id': session_id, 'progress': engine.get_progress(), 'phase': _sessions[session_id]['phase']}


@app.get('/sessions/{sid}/next')
def next_question(sid: int):
    sess = _session_or_404(sid)
    nxt = _phase_next(sess)
    if isinstance(nxt, dict) and nxt.get('type') == 'ros_batch':
        return {'next_batch': nxt, 'progress': sess['engine'].get_progress(), 'phase': sess['phase']}
    return {'next_question': nxt, 'progress': sess['engine'].get_progress(), 'phase': sess['phase']}


@app.get('/sessions/{sid}/current')
def current_question(sid: int):
    """Return the current question or batch (for UI preview)."""
    sess = _session_or_404(sid)
    engine = sess['engine']
    current = None
    if sess['phase'] == 'complaint':
        current = engine.peek_current_question()
    elif sess['phase'] == 'ros':
        if sess.get('ros_runner') is None:
            sess['ros_runner'] = ROSRunner(engine.state, engine.patient, engine.complaint, SHARED)
        current = sess['ros_runner'].peek_current_batch()
    elif sess['phase'] == 'modules':
        current = _ensure_module_runner(sess).peek_current_question()
    return {
        'current': current,
        'progress': engine.get_progress(),
        'phase': sess['phase'],
        'modules_started': bool(sess.get('modules_started')),
        'modules_completed': bool(sess.get('modules_completed')),
    }


@app.get('/sessions/{sid}/next_batch')
def next_ros_batch(sid: int):
    """Return the next ROS batch (preview, without consuming)."""
    sess = _session_or_404(sid)
    if sess['phase'] != 'ros' or sess['ros_runner'] is None:
        raise HTTPException(400, 'ROS not active')
    batch = sess['ros_runner'].peek_current_batch()
    return {'next_batch': batch, 'phase': sess['phase'], 'progress': sess['engine'].get_progress()}


@app.post('/sessions/{sid}/ros_batch')
def answer_ros_batch(sid: int, req: RosBatchAnswerReq):
    """Submit answers for a ROS batch."""
    sess = _session_or_404(sid)
    if sess['phase'] != 'ros':
        raise HTTPException(400, 'Not in ROS phase')
    if sess['ros_runner'] is None:
        raise HTTPException(400, 'ROS runner not initialised')
    
    sess['ros_runner'].record_batch_answers(req.answers, req.details)
    for _field, _answer in req.answers.items():
        sess['engine'].evaluate_shared_escalation_rules(_field, _answer)
    
    # Add turns to the database for auditing
    for field, answer in req.answers.items():
        q = next((q for q in sess['ros_runner'].questions.values() if q.get('field') == field), None)
        question_text = q.get('text', field) if q else field
        add_turn(sid, 'system', question_text, field, 'ros')
        add_turn(sid, 'patient', answer, field, 'ros')
        if req.details and field in req.details:
            add_turn(sid, 'patient', f"Detail: {req.details[field]}", f"{field}_detail", 'ros')
    
    # Get next batch or move to modules
    nxt = sess['ros_runner'].get_next_batch()
    if nxt is None:
        sess['phase'] = 'modules'
        next_q = _phase_next(sess)
        return {
            'next_question': next_q,
            'phase': sess['phase'],
            'progress': sess['engine'].get_progress(),
            'extracted_state': sess['engine'].state,
            'modules_started': bool(sess.get('modules_started')),
            'modules_completed': bool(sess.get('modules_completed')),
        }
    else:
        return {'next_batch': nxt, 'phase': sess['phase'], 'progress': sess['engine'].get_progress(), 'extracted_state': sess['engine'].state}


@app.post('/sessions/{sid}/answer')
def answer_question(sid: int, req: AnswerReq):
    sess = _session_or_404(sid)
    phase = sess['phase']
    if phase == 'complaint':
        turn = sess['engine'].record_answer(req.question_id, req.field, req.answer, req.phase)
    elif phase == 'ros':
        q = _full_question_dict(sess, 'ros', req.question_id, req.field)
        sess['ros_runner'].record_answer(q, req.answer)
        sess['engine'].evaluate_shared_escalation_rules(req.field, req.answer)
        turn = {'extracted_bonus_fields': {}}
    elif phase == 'modules':
        q = _full_question_dict(sess, 'modules', req.question_id, req.field)
        sess['module_runner'].record_answer(q, req.answer)
        sess['engine'].evaluate_shared_escalation_rules(req.field, req.answer)
        turn = {'extracted_bonus_fields': {}}
    else:
        raise HTTPException(400, 'Session is not accepting answers')
    question_text = _lookup_question_text(sess, phase, req.question_id, req.field)
    add_turn(sid, 'system', question_text, req.question_id, req.phase)
    add_turn(sid, 'patient', req.answer, req.question_id, req.phase)
    nxt = _phase_next(sess)
    if isinstance(nxt, dict) and nxt.get('type') == 'ros_batch':
        return {'next_batch': nxt, 'progress': sess['engine'].get_progress(), 'phase': sess['phase'], 'extracted_bonus': turn.get('extracted_bonus_fields', {}), 'extracted_state': sess['engine'].state}
    return {'next_question': nxt, 'progress': sess['engine'].get_progress(), 'phase': sess['phase'], 'extracted_bonus': turn.get('extracted_bonus_fields', {}), 'extracted_state': sess['engine'].state}


@app.post('/sessions/{sid}/skip')
def skip_question(sid: int, req: AnswerReq):
    sess = _session_or_404(sid)
    phase = sess['phase']
    if phase == 'complaint':
        turn = sess['engine'].skip_question(req.question_id, req.field, req.phase)
        question_text = _lookup_question_text(sess, 'complaint', req.question_id, req.field)
    elif phase == 'modules':
        q = _full_question_dict(sess, 'modules', req.question_id, req.field)
        if sess.get('module_runner') is not None:
            sess['module_runner'].record_answer(q, 'not_assessed')
        sess['engine'].state[req.field] = 'not_assessed'
        question_text = _lookup_question_text(sess, 'modules', req.question_id, req.field)
        turn = {'extracted_bonus_fields': {}}
    else:
        raise HTTPException(400, 'Skipping is supported during complaint clerking and history modules')
    add_turn(sid, 'system', question_text, req.question_id, req.phase)
    add_turn(sid, 'patient', 'not_assessed', req.question_id, req.phase)
    nxt = _phase_next(sess)
    if isinstance(nxt, dict) and nxt.get('type') == 'ros_batch':
        return {'next_batch': nxt, 'progress': sess['engine'].get_progress(), 'phase': sess['phase'], 'turn': turn, 'extracted_bonus': turn.get('extracted_bonus_fields', {}), 'extracted_state': sess['engine'].state}
    return {'next_question': nxt, 'progress': sess['engine'].get_progress(), 'phase': sess['phase'], 'turn': turn, 'extracted_bonus': turn.get('extracted_bonus_fields', {}), 'extracted_state': sess['engine'].state}


@app.post('/sessions/{sid}/complete')
def complete_session(sid: int):
    sess = _session_or_404(sid)
    if sess['phase'] != 'complete_ready':
        nxt = _phase_next(sess)
        if nxt is not None:
            if isinstance(nxt, dict) and nxt.get('type') == 'ros_batch':
                return {'next_batch': nxt, 'phase': sess['phase'], 'progress': sess['engine'].get_progress()}
            return {'next_question': nxt, 'phase': sess['phase'], 'progress': sess['engine'].get_progress()}
    engine = sess['engine']
    engine.completed = True
    summary = generate_template_summary(engine)
    summary['patient_age'] = sess['patient_age']
    summary['patient_sex'] = sess['patient_sex']
    pre = format_summary_text(summary)
    ai = ai_summarize(engine.state, summary)
    save_summary(sid, pre_summary=pre, ai_summary=ai)
    required_fields = {engine.questions.get(qid, {}).get('field', qid) for ids in engine.current_profile_data.values() for qid in ids}
    total = max(len(required_fields), 1)
    filled = sum(1 for f in required_fields if engine.state.get(f) not in (None, '', 'not_assessed'))
    all_turns = get_turns(sid)
    patient_turns = sum(1 for t in all_turns if t.get('speaker') == 'patient')
    system_turns = sum(1 for t in all_turns if t.get('speaker') == 'system')
    save_metrics(sid, {
        'patient_turn_count': patient_turns,
        'system_turn_count': system_turns,
        'required_fields_total': total,
        'required_fields_filled': filled,
        'completion_rate': round(filled / total, 3),
        'missing_fields_count': len(summary.get('missing_clarifications', [])),
        'missing_fields': json.dumps(summary.get('missing_clarifications', [])),
        'summary_length': len(pre)
    })
    update_encounter_status(sid, 'completed', ended_at=datetime.utcnow().isoformat())
    update_encounter_state(
        sid,
        engine.state,
        summary.get('pertinent_positives', []),
        summary.get('pertinent_negatives', []),
        engine.escalation_level
    )
    return {
        'template_summary': summary,
        'pre_summary': pre,
        'ai_summary': ai,
        'extracted_state': engine.state,
        'progress': engine.get_progress(),
        'phase': 'completed'
    }


@app.get('/sessions/{sid}')
def get_session(sid: int):
    sess = _session_or_404(sid)
    engine = sess['engine']
    return {
        'state': engine.state,
        'turns': engine.turns,
        'red_flags': engine.red_flags,
        'escalation': engine.escalation_level,
        'progress': engine.get_progress(),
        'phase': sess['phase'],
        'summary': get_summary(sid)
    }


@app.put('/sessions/{sid}/doctor-summary')
def save_doctor_summary_endpoint(sid: int, req: DoctorSummaryReq):
    _session_or_404(sid)
    save_summary(sid, post_summary=req.post_summary, reviewed_at=datetime.utcnow().isoformat())
    update_encounter_status(sid, 'reviewed')
    return {'status': 'saved'}


@app.get('/sessions/{sid}/transcript')
def get_transcript(sid: int):
    _session_or_404(sid)
    return {'turns': get_turns(sid)}


@app.get('/sessions/{sid}/metrics')
def get_session_metrics(sid: int):
    _session_or_404(sid)
    metrics = get_metrics(sid)
    return metrics or {}


@app.post('/sessions/{sid}/abandon')
def abandon_session(sid: int):
    _session_or_404(sid)
    update_encounter_status(sid, 'abandoned', ended_at=datetime.utcnow().isoformat())
    if sid in _sessions:
        del _sessions[sid]
    return {'status': 'abandoned'}


@app.post('/sessions/{sid}/force_complete')
def force_complete(sid: int):
    sess = _session_or_404(sid)
    engine = sess['engine']
    engine.completed = True
    summary = generate_template_summary(engine)
    pre = format_summary_text(summary)
    ai = ai_summarize(engine.state, summary)
    save_summary(sid, pre_summary=pre, ai_summary=ai)
    update_encounter_status(sid, 'force_completed', ended_at=datetime.utcnow().isoformat())
    update_encounter_state(
        sid,
        engine.state,
        summary.get('pertinent_positives', []),
        summary.get('pertinent_negatives', []),
        engine.escalation_level
    )
    return {
        'template_summary': summary,
        'pre_summary': pre,
        'ai_summary': ai,
        'phase': 'completed'
    }