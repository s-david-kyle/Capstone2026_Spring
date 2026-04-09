"""
hybrid_engine/session.py
========================
HybridIntakeSession — the single public interface for running a hybrid intake.

Wraps the doctor's IntakeEngine and HaikuAnswerExtractor together so the
caller never needs to touch either directly.

Typical usage
-------------
session = HybridIntakeSession('headache', patient_context={'sex': 'female', 'age': 34})

while True:
    question = session.next_question()
    if question is None:
        break
    patient_text = input(question['display_text'] + '  ')
    result = session.submit_answer(patient_text)

summary = session.get_summary()
print(summary['summary_text'])
"""

from __future__ import annotations

import os
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Path bootstrap — complaints_module lives at the project root.
# This lets hybrid_engine be imported from anywhere under CAPSTONE2026_SPRING/
# ---------------------------------------------------------------------------

def _project_root() -> str:
    """Walk up from this file to find the CAPSTONE2026_SPRING root."""
    here = os.path.dirname(os.path.abspath(__file__))
    # hybrid_engine/ sits directly under the project root
    return os.path.dirname(here)


_ROOT = _project_root()
_COMPLAINTS_DIR = os.path.join(_ROOT, "complaints_module", "complaints")
_ENGINE_DIR = os.path.join(_ROOT, "complaints_module", "engine")

# Ensure complaints_module is importable
_COMPLAINTS_MODULE_ROOT = os.path.join(_ROOT, "complaints_module")
if _COMPLAINTS_MODULE_ROOT not in sys.path:
    sys.path.insert(0, _COMPLAINTS_MODULE_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from engine.intake_engine import IntakeEngine, load_complaint, complaint_eligibility_warning  # noqa: E402
from engine.summary_engine import generate_template_summary, format_summary_text             # noqa: E402

from hybrid_engine.extractor import HaikuAnswerExtractor, ExtractionResult                   # noqa: E402


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

class HybridIntakeSession:
    """
    A single patient intake session using the hybrid engine.

    Parameters
    ----------
    complaint_id:     One of the complaint IDs in complaints_module/complaints/
                      (e.g. 'headache', 'chest_pain', 'seizure')
    patient_context:  Optional dict with 'sex' and 'age' keys used for
                      ask_if eligibility rules (e.g. SEX_FEMALE_REPRODUCTIVE_AGE)
    verbose:          Print turn-by-turn progress to stdout

    Attributes
    ----------
    engine:    The underlying IntakeEngine — access .state, .red_flags,
               .escalation_level, .get_progress() directly if needed
    extractor: The HaikuAnswerExtractor — stateless, shared across turns
    turns:     List of turn dicts recorded by the engine
    """

    def __init__(
        self,
        complaint_id: str,
        patient_context: Optional[dict] = None,
        verbose: bool = False,
    ):
        self.complaint_id = complaint_id
        self.patient_context = patient_context or {}
        self.verbose = verbose

        complaint_data = load_complaint(_COMPLAINTS_DIR, complaint_id)

        # Eligibility check — warns but does not block
        warning = complaint_eligibility_warning(
            complaint_data, self.patient_context.get("sex")
        )
        if warning:
            print(f"[hybrid_engine] Eligibility warning: {warning}")

        self.engine = IntakeEngine(complaint_data, patient_context=self.patient_context)
        self.extractor = HaikuAnswerExtractor()

        self._current_question: Optional[dict] = None
        self._last_result: Optional[ExtractionResult] = None

        if self.verbose:
            budget = self.engine.budget
            print(
                f"[hybrid_engine] Loaded '{complaint_data['display_name']}' — "
                f"{len(self.engine.questions)} questions in library, "
                f"budget {budget.get('target_question_budget')}-{budget.get('max_questions')}"
            )

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def next_question(self) -> Optional[dict]:
        """
        Advance to the next question.

        Returns a question dict with:
            id, field, text, display_text, phase, response_type,
            sensitive_topic, compound_question

        Returns None when the session is complete.
        """
        q = self.engine.get_next_question()
        self._current_question = q

        if q is None:
            return None

        # Add a display_text alias so callers don't need to know
        # whether to use 'text' or 'ui_label'
        q["display_text"] = q.get("text", q.get("ui_label", ""))

        return q

    def submit_answer(self, patient_answer: str) -> ExtractionResult:
        """
        Submit a free-text patient answer for the current question.

        Runs Haiku extraction, pre-populates any inline detail, then
        records the answer in the engine.

        Returns the ExtractionResult for logging or inspection.

        Raises RuntimeError if called before next_question().
        """
        if self._current_question is None:
            raise RuntimeError(
                "No current question. Call next_question() before submit_answer()."
            )

        q = self._current_question
        result = self.extractor.extract(
            question=q,
            patient_answer=patient_answer,
            engine_state=self.engine.state,
        )

        # Pre-populate detail field from inline Haiku extraction.
        # This prevents the engine from firing a redundant detail follow-up
        # when the patient already answered it in the same breath.
        if result.detail_value and q.get("detail_field"):
            detail_field = q["detail_field"]
            if self.engine.state.get(detail_field) is None:
                self.engine.state[detail_field] = result.detail_value
                if self.verbose:
                    print(
                        f"  [detail pre-captured → {detail_field}]: {result.detail_value}"
                    )

        self.engine.record_answer(
            question_id=q["id"],
            field=q["field"],
            answer=result.canonical_answer,
            phase=q["phase"],
        )

        self._last_result = result

        if self.verbose:
            progress = self.engine.get_progress()
            print(
                f"  [{q['phase']}] {q['text']}\n"
                f"  Patient: {patient_answer}\n"
                f"  → {result.canonical_answer!r} "
                f"(conf: {result.confidence}) | "
                f"Q {progress['questions_asked']}/{progress['budget_target']} | "
                f"escalation: {progress['escalation_level']}"
            )
            if progress["red_flags"]:
                flags = [f["pattern"] for f in progress["red_flags"]]
                print(f"  ⚠️  RED FLAGS: {flags}")

        return result

    def is_complete(self) -> bool:
        """True when the engine has no more questions."""
        return self.engine.completed

    # ------------------------------------------------------------------
    # Progress and output
    # ------------------------------------------------------------------

    def get_progress(self) -> dict:
        """Return the engine's progress dict."""
        return self.engine.get_progress()

    def get_summary(self) -> dict:
        """
        Generate the clinician summary.

        Returns a dict with:
            summary_text   Formatted plain-text HPI summary
            structured     Full structured summary dict from summary_engine
            progress       Engine progress dict
        """
        structured = generate_template_summary(self.engine)
        return {
            "summary_text": format_summary_text(structured),
            "structured": structured,
            "progress": self.engine.get_progress(),
        }

    @property
    def turns(self) -> list:
        return self.engine.turns

    @property
    def red_flags(self) -> list:
        return self.engine.red_flags

    @property
    def escalation_level(self) -> str:
        return self.engine.escalation_level

    @property
    def state(self) -> dict:
        return self.engine.state

    # ------------------------------------------------------------------
    # Class methods
    # ------------------------------------------------------------------

    @classmethod
    def available_complaints(cls) -> list[dict]:
        """List all available complaint IDs and display names."""
        from engine.intake_engine import list_complaints
        return list_complaints(_COMPLAINTS_DIR)
