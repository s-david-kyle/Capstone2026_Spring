
"""
Clinical Intake Runtime Engine v2.4
- complaint-owned deterministic scheduling
- parent/detail gating
- shared ask_if evaluation fallback
- concept coverage tracking to suppress near-duplicate questions
- complaint metadata eligibility checks
"""
from __future__ import annotations
import json, os, re
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

PHASE_ORDER = [
    "opening","core_characterize","early_danger_screen","extended_characterize",
    "critical_followup","high_priority_followup","context_and_history",
]

ESCALATION_TIERS = {
    "immediate_alert": {"label": "Immediate Alert", "priority": 0, "color": "#dc2626"},
    "urgent_escalation": {"label": "Urgent Escalation", "priority": 1, "color": "#ea580c"},
    "priority_clinician_review": {"label": "Priority Review", "priority": 2, "color": "#ca8a04"},
    "same_day_clinician_review": {"label": "Same-Day Review", "priority": 3, "color": "#2563eb"},
    "none": {"label": "No Escalation", "priority": 4, "color": "#16a34a"},
}

PHASE_LABELS = {
    "opening": "Opening", "core_characterize": "Core Characterize", "early_danger_screen": "⚠️ Danger Screen",
    "extended_characterize": "Extended Characterize", "critical_followup": "Critical Followup",
    "high_priority_followup": "High Priority Followup", "context_and_history": "Context & History", "complete": "✅ Complete",
}

_POS = frozenset(["yes","yeah","yep","yea","y","positive","present","true","correct","sure","definitely"])
_NEG = frozenset(["no","nope","nah","n","none","nil","nothing","negative","denied","never","not at all","false","neither","not really","n/a"])
_UNKNOWN = frozenset(["unknown","not_assessed","not assessed","not sure","unsure","uncertain","dont know","don't know","maybe","already responded"])

def normalize_boolean(raw: str | None) -> Optional[bool]:
    if raw is None:
        return None
    low = str(raw).strip().lower()
    if low in _POS: return True
    if low in _NEG: return False
    for pw in ("yes ","yeah ","yep ","y,"):
        if low.startswith(pw): return True
    for nw in ("no ","no,","no.","nope ","none ","not "):
        if low.startswith(nw): return False
    return None

def is_unknown_answer(raw: str | None) -> bool:
    return str(raw or '').strip().lower() in _UNKNOWN

def is_positive_answer(raw: str | None) -> bool:
    b = normalize_boolean(raw)
    if b is not None: return b
    low = str(raw or "").strip().lower()
    return low not in ("", *tuple(_UNKNOWN))

def is_negative_answer(raw: str | None) -> bool:
    return normalize_boolean(raw) is False

def _load_shared_contract() -> dict:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    p = os.path.join(root, 'shared', 'shared_v2.json')
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

_SHARED = _load_shared_contract()
_CONCEPT_MAP = _SHARED.get('concept_dedup_map', {})
_ASK_IF_REGISTRY = _SHARED.get('ask_if_registry', {})

def _canon_concept(name: str | None) -> str:
    nm = str(name or '').replace('_details','').strip()
    for canon, aliases in _CONCEPT_MAP.items():
        if nm == canon or nm in aliases:
            return canon
    return nm

class IntakeEngine:
    def __init__(self, complaint_data: dict, patient_context: Optional[dict] = None):
        self.complaint = complaint_data
        self.patient = patient_context or {}
        self.state: Dict[str, Any] = {}
        self.state_bool: Dict[str, Optional[bool]] = {}
        self.turns: List[dict] = []
        self.questions = complaint_data.get('questions_by_id', {})
        self.budget = complaint_data.get('question_budget', {}).get('primary_mode', {})
        self.phase_order = complaint_data.get('question_schedule', {}).get('enforced_phase_order', PHASE_ORDER)
        self.active_profile_name = 'default_profile'
        self.schedule = deepcopy(complaint_data.get('question_schedule', {}).get(self.active_profile_name, {}))
        self._phase_idx = 0
        self._q_idx = 0
        self.questions_asked = 0
        self.red_flags: List[dict] = []
        self.escalation_level = 'none'
        self.completed = False
        self.started_at = datetime.utcnow().isoformat()
        self._detail_queue: List[str] = []
        self._detail_to_parent: Dict[str, str] = {}
        self.covered_concepts: set[str] = set()
        self.concept_sources: Dict[str, str] = {}
        for qid, q in self.questions.items():
            detail_field = q.get('detail_field')
            if detail_field:
                self._detail_to_parent[detail_field] = q.get('field', qid)
            if q.get('parent_field'):
                self._detail_to_parent[q.get('field', qid)] = q['parent_field']
        self._apply_profile_switch()

    def _question_concepts(self, qid: str, q: dict) -> List[str]:
        field = q.get('field', qid)
        concepts = []
        main = q.get('canonical_concept') or field.replace('_details','')
        concepts.append(_canon_concept(main))
        for extra in q.get('resolves_concepts', []):
            concepts.append(_canon_concept(extra))
        return [c for c in dict.fromkeys(concepts) if c]

    def _mark_covered(self, qid: str, q: dict, answer: str) -> None:
        if answer is None:
            return
        field = q.get('field', qid)
        concepts = list(self._question_concepts(qid, q))
        if is_positive_answer(answer):
            for extra in q.get('resolves_concepts_if_positive', []):
                concepts.append(_canon_concept(extra))
        for c in [c for c in dict.fromkeys(concepts) if c]:
            self.covered_concepts.add(c)
            self.concept_sources.setdefault(c, field)
        if is_positive_answer(answer) and 'pain_timing_pattern' in q.get('resolves_concepts_if_positive', []):
            self.state['pain_timing_pattern_resolved'] = True

    def _apply_profile_switch(self) -> None:
        schedules = self.complaint.get('question_schedule', {})
        for rule in schedules.get('profile_switch_rules', []):
            action = rule.get('action', '')
            if not action.startswith('use '):
                continue
            target = action.replace('use ', '').strip()
            if target == self.active_profile_name or target not in schedules:
                continue
            trig = rule.get('trigger')
            matched = self._eval_trigger_string(trig) if isinstance(trig, str) else self._eval_logic(trig) if isinstance(trig, dict) else False
            if matched:
                self.active_profile_name = target
                self.schedule = deepcopy(schedules.get(target, {}))
                return

    def _eval_trigger_string(self, trigger: str) -> bool:
        text = ' '.join(str(v) for v in self.state.values() if v).lower()
        trigger = trigger.lower()
        if 'no alternate profile' in trigger: return False
        keywords = ['sudden','worst','collapse','anticoagulant','trauma','recurrent','similar','no active danger']
        return any(k in text for k in keywords if k in trigger)

    def _eval_logic(self, logic: dict) -> bool:
        if not logic: return True
        op = logic.get('op')
        if op == 'custom_runtime':
            name = logic.get('name')
            fn = getattr(self, f'_{name}', None) or getattr(self, name, None)
            return fn() if callable(fn) else True
        if op == 'field_not_true':
            return bool(self.state.get(logic.get('field_ref'))) is False
        if op == 'all': return all(self._eval_logic(c) for c in logic.get('conditions', []))
        if op == 'any': return any(self._eval_logic(c) for c in logic.get('conditions', []))
        if op == 'field_equals':
            fld = logic.get('field_ref')
            if fld in self.state_bool: return self.state_bool.get(fld) == logic.get('value')
            return str(self.state.get(fld,'')) == str(logic.get('value'))
        if op == 'field_text_contains':
            return str(logic.get('value','')).lower() in str(self.state.get(logic.get('field_ref'), '')).lower()
        if op == 'field_text_contains_any':
            val = str(self.state.get(logic.get('field_ref'), '')).lower()
            return any(str(v).lower() in val for v in logic.get('value', []))
        if op == 'field_contains':
            return str(logic.get('value','')).lower() in str(self.state.get(logic.get('field_ref'), '')).lower()
        if op == 'field_gte':
            try: return float(self.patient.get(logic.get('field_ref'), self.state.get(logic.get('field_ref')))) >= float(logic.get('value'))
            except Exception: return False
        if op == 'duration_gte':
            txt = str(self.state.get(logic.get('field_ref'), '')).lower()
            value = float(logic.get('value', 0)); unit = logic.get('unit','weeks')
            if unit == 'weeks':
                if re.search(r'month|year', txt): return True
                m = re.search(r'(\d+)\s*week', txt)
                return bool(m) and int(m.group(1)) >= value
        return False

    def _fresh_blood_stool_relevant(self) -> bool:
        value = str(self.state.get('hematemesis_or_melena') or '').strip().lower()
        detail = str(self.state.get('hematemesis_or_melena_details') or '').strip().lower()
        melena_words = ('black tarry', 'black stool', 'tarry stool', 'melena')
        if value in {'yes', 'true'} and any(w in detail for w in melena_words):
            return False
        return True

    def _eval_ask_if(self, cond: Optional[str]) -> bool:
        if not cond: return True
        if cond == 'NEVER': return False
        sex = self.patient.get('sex', 'unknown')
        age = int(self.patient.get('age', 30) or 30)
        local = {
            'SEX_FEMALE_REPRODUCTIVE_AGE': lambda: sex == 'female' and 12 <= age <= 55,
            'SEX_FEMALE': lambda: sex == 'female',
            'AGE_GTE_50': lambda: age >= 50,
            'AGE_GTE_65': lambda: age >= 65,
            'INFECTIOUS_OR_GU_PRESENTATION': lambda: self.complaint.get('complaint_id') in {'fever','cough','sore_throat','rash','vomiting','loose_stool','dysuria','hematuria','vaginal_discharge'},
            'SEXUAL_HISTORY_RELEVANT_SESSION': lambda: self.complaint.get('complaint_id') in {'vaginal_discharge','dysuria','hematuria','abdominal_pain','sore_throat'},
            'GYNECOLOGIC_CONTEXT_RELEVANT': lambda: self.complaint.get('complaint_id') in {'vaginal_discharge','abdominal_pain','vomiting','dysuria','hematuria','constipation','fatigue','weight_loss'},
            'PATIENT_PEDIATRIC_OR_CAREGIVER_HISTORY_RELEVANT': lambda: age < 18,
            'SUSPECTED_INFECTIOUS_PRESENTATION_OR_RESPIRATORY': lambda: self.complaint.get('complaint_id') in {'fever','cough','sore_throat','rash','shortness_of_breath'},
            'ELDERLY_OR_HIGH_RISK_RESPIRATORY_PRESENTATION': lambda: age >= 65,
            'POSSIBLE_TB_PRESENTATION': lambda: bool(self.state.get('hemoptysis') or self.state.get('night_sweats') or self.complaint.get('complaint_id') == 'cough'),
            'POSSIBLE_CNS_INFECTION_PRESENTATION': lambda: bool(self.state.get('neck_stiffness') or self.state.get('fever') or self.complaint.get('complaint_id') in {'headache','fever'}),
            'AURA_STATUS_POSITIVE': lambda: self.state_bool.get('aura_status') is True,
            'PAIN_TIMING_UNRESOLVED': lambda: not bool(self.state.get('pain_timing_pattern_resolved')),
            'FRESH_BLOOD_STOOL_RELEVANT': self._fresh_blood_stool_relevant,
            'CHANGE_IN_BOWEL_HABIT_POSITIVE': lambda: self.state_bool.get('change_in_bowel_habit') is True,
        }
        if cond in local: return local[cond]()
        shared = _ASK_IF_REGISTRY.get(cond, {})
        if shared.get('logic'): return self._eval_logic(shared['logic'])
        return True

    def _should_skip(self, qid: str, q: dict) -> bool:
        field = q.get('field', qid)
        if self.state.get(field) is not None:
            return True
        if not self._eval_ask_if(q.get('ask_if')):
            return True
        # concept coverage skip for near-duplicate prompts.
        q_concepts = self._question_concepts(qid, q)
        parent_field = q.get('parent_field') or self._detail_to_parent.get(field)
        if any(c in self.covered_concepts for c in q_concepts):
            if field.endswith('_details') or q.get('parent_field'):
                # allow the intended child detail prompt only when its parent just opened that detail path
                src_fields = {self.concept_sources.get(c) for c in q_concepts if self.concept_sources.get(c)}
                if parent_field not in src_fields and field not in src_fields:
                    return True
            else:
                return True
        for rule in q.get('skip_if', []):
            if rule == 'FIELD_ALREADY_CAPTURED' and self.state.get(field) is not None:
                return True
            if rule == 'DETAIL_ALREADY_CAPTURED':
                detail = q.get('detail_field')
                if detail and self.state.get(detail) is not None: return True
            if rule == 'PARENT_NEGATIVE':
                parent_field = q.get('parent_field') or self._detail_to_parent.get(field) or field.replace('_details', '')
                parent_answer = self.state.get(parent_field)
                if parent_answer is None or is_negative_answer(str(parent_answer)) or is_unknown_answer(str(parent_answer)):
                    return True
            if rule == 'SEVERITY_BELOW_7':
                sev = self.state.get('severity')
                try:
                    if sev is not None and float(str(sev).split('/')[0].strip()) < 7:
                        return True
                except Exception:
                    pass
        return False

    def _make_question(self, qid: str, q: dict) -> dict:
        return {'id': qid, 'field': q.get('field', qid), 'text': q.get('text', ''), 'ui_label': q.get('ui_label', qid), 'phase': q.get('phase', ''), 'response_type': q.get('response_type', 'SHORT_TEXT'), 'sensitive_topic': q.get('sensitive_topic', False), 'compound_question': q.get('compound_question', False)}

    def get_next_question(self) -> Optional[dict]:
        if self.completed: return None
        self._apply_profile_switch()
        max_q = self.budget.get('max_questions', 50)
        while self._detail_queue:
            qid = self._detail_queue.pop(0)
            q = self.questions.get(qid)
            if q and not self._should_skip(qid, q) and self.questions_asked < max_q:
                return self._make_question(qid, q)
        while self._phase_idx < len(self.phase_order):
            phase = self.phase_order[self._phase_idx]
            ids = self.schedule.get(phase, [])
            while self._q_idx < len(ids):
                qid = ids[self._q_idx]; self._q_idx += 1
                q = self.questions.get(qid)
                if not q or self._should_skip(qid, q):
                    continue
                if self.questions_asked >= max_q:
                    self.completed = True; return None
                return self._make_question(qid, q)
            self._phase_idx += 1; self._q_idx = 0
        self.completed = True
        return None

    def record_answer(self, question_id: str, field: str, answer: str, phase: str) -> dict:
        self.state[field] = answer
        self.state_bool[field] = normalize_boolean(answer)
        self.questions_asked += 1
        turn = {'turn_number': len(self.turns)+1, 'question_id': question_id, 'field': field, 'phase': phase, 'question_text': self.questions.get(question_id, {}).get('text', question_id), 'answer': answer, 'timestamp': datetime.utcnow().isoformat(), 'skipped': False}
        self.turns.append(turn)
        q_def = self.questions.get(question_id, {})
        self._mark_covered(question_id, q_def, answer)
        self._queue_positive_detail_followups(question_id, answer)
        self._check_red_flags(field, answer)
        return turn

    def skip_question(self, question_id: str, field: str, phase: str) -> dict:
        self.state[field] = 'not_assessed'; self.state_bool[field] = None; self.questions_asked += 1
        turn = {'turn_number': len(self.turns)+1, 'question_id': question_id, 'field': field, 'phase': phase, 'question_text': self.questions.get(question_id, {}).get('text', question_id), 'answer': 'not_assessed', 'timestamp': datetime.utcnow().isoformat(), 'skipped': True}
        self.turns.append(turn)
        q_def = self.questions.get(question_id,{})
        self._mark_covered(question_id, q_def, 'not_assessed')
        return turn

    def _queue_positive_detail_followups(self, question_id: str, answer: str) -> None:
        q_def = self.questions.get(question_id, {})
        if not is_positive_answer(answer): return
        if q_def.get('capture_detail_if_positive') and q_def.get('detail_field'):
            detail_field = q_def['detail_field']
            detail_val = answer
            low = str(answer).lower().strip()
            for pfx in ('yes -','yes,','yes.','yeah -','yeah,','yep -','yep,'):
                if low.startswith(pfx):
                    detail_val = str(answer)[len(pfx):].strip(); break
            # only auto-capture detail when the patient already provided actual detail in the same answer
            if detail_val.lower() not in ('yes','yeah','yep','y','') and normalize_boolean(detail_val) is None and not is_unknown_answer(detail_val) and self.state.get(detail_field) is None:
                self.state[detail_field] = detail_val
                self.covered_concepts.add(_canon_concept(q_def.get('canonical_concept') or detail_field.replace('_details','')))
                self.concept_sources.setdefault(_canon_concept(q_def.get('canonical_concept') or detail_field.replace('_details','')), detail_field)
        for followup_qid in q_def.get('if_positive_ask', []):
            if followup_qid in self.questions and followup_qid not in self._detail_queue:
                followup_field = self.questions[followup_qid].get('field', followup_qid)
                if self.state.get(followup_field) is None:
                    self._detail_queue.append(followup_qid)

    def _check_red_flags(self, field: str, answer: str) -> None:
        if not is_positive_answer(answer): return
        patterns = self.complaint.get('derived_red_flag_patterns', {})
        for pattern_name, pattern_def in patterns.items():
            fields = pattern_def if isinstance(pattern_def, list) else pattern_def.get('fields', [])
            if field in fields and not any(f['pattern'] == pattern_name for f in self.red_flags):
                self.red_flags.append({'pattern': pattern_name, 'trigger_field': field, 'value': answer, 'timestamp': datetime.utcnow().isoformat()})
                self._update_escalation(pattern_name)

    def _update_escalation(self, pattern_name: str) -> None:
        current_priority = ESCALATION_TIERS.get(self.escalation_level, {}).get('priority', 4)
        pattern_low = pattern_name.lower()
        if any(k in pattern_low for k in ('immediate','haemodynamic','anaphylaxis')):
            new_level = 'immediate_alert'
        elif any(k in pattern_low for k in ('obstruction','bleeding','dvt','thunderclap','aortic','embolus','eclampsia')):
            new_level = 'urgent_escalation'
        else:
            new_level = 'priority_clinician_review'
        if ESCALATION_TIERS.get(new_level, {}).get('priority', 4) < current_priority:
            self.escalation_level = new_level

    def get_progress(self) -> dict:
        total = sum(len(ids) for ids in self.schedule.values())
        return {'questions_asked': self.questions_asked, 'total_scheduled': total, 'progress_pct': round(self.questions_asked / max(total, 1) * 100), 'current_phase': self.phase_order[self._phase_idx] if self._phase_idx < len(self.phase_order) else 'complete', 'budget_target': self.budget.get('target_question_budget'), 'budget_max': self.budget.get('max_questions'), 'red_flags_count': len(self.red_flags), 'red_flags': self.red_flags, 'escalation_level': self.escalation_level, 'completed': self.completed, 'active_profile': self.active_profile_name, 'covered_concepts': sorted(self.covered_concepts), 'covered_concept_count': len(self.covered_concepts)}

def complaint_eligibility_warning(complaint_data: dict, patient_sex: str | None) -> str | None:
    eligibility = complaint_data.get('eligibility', {})
    allowed = eligibility.get('allowed_patient_sex')
    if not allowed: return None
    sex = (patient_sex or 'unknown').lower()
    if sex not in {str(x).lower() for x in allowed}:
        return eligibility.get('message') or 'This complaint is not currently enabled for the selected sex in this build.'
    return None

def load_complaint(complaints_dir: str, complaint_id: str) -> dict:
    path = os.path.join(complaints_dir, f'{complaint_id}_v2.json')
    if not os.path.exists(path): raise FileNotFoundError(path)
    with open(path, 'r', encoding='utf-8') as handle: return json.load(handle)

def list_complaints(complaints_dir: str) -> list[dict]:
    rows=[]
    if not os.path.isdir(complaints_dir): return rows
    for filename in sorted(os.listdir(complaints_dir)):
        if not filename.endswith('_v2.json'): continue
        path = os.path.join(complaints_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8') as handle: data=json.load(handle)
            rows.append({'complaint_id': data.get('complaint_id', filename.replace('_v2.json','')), 'display_name': data.get('display_name',''), 'primary_system': data.get('primary_system',''), 'question_count': len(data.get('questions_by_id',{})), 'budget_target': data.get('question_budget',{}).get('primary_mode',{}).get('target_question_budget',0), 'eligibility': data.get('eligibility')})
        except Exception:
            continue
    return rows
