"""
hybrid_engine
=============
Combines the doctor's clinician-authored deterministic intake engine
(complaints_module/) with Claude Haiku LLM extraction.

The doctor's IntakeEngine owns all routing:
  - 7-phase ordered question scheduling
  - Parent / child question gating
  - ask_if / skip_if conditional logic
  - Question budget enforcement
  - Canonical concept deduplication
  - Red flag pattern detection and escalation tiers

HaikuAnswerExtractor owns all answer understanding:
  - Free-text → structured extraction via Claude Haiku API
  - Response-type-aware prompting (boolean, scale, temporal, narrative, text)
  - Inline detail pre-capture to suppress redundant follow-up questions
  - JSON parsing with fallback

Public API
----------
from hybrid_engine import HybridIntakeSession

session = HybridIntakeSession(complaint_id='headache', patient_context={'sex': 'female', 'age': 34})
question = session.next_question()          # returns question dict or None
result   = session.submit_answer(free_text) # returns ExtractionResult
summary  = session.get_summary()            # returns formatted HPI summary
"""

from hybrid_engine.session import HybridIntakeSession
from hybrid_engine.extractor import HaikuAnswerExtractor, ExtractionResult

__all__ = [
    "HybridIntakeSession",
    "HaikuAnswerExtractor",
    "ExtractionResult",
]
