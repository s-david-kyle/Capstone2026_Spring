"""
hybrid_engine/extractor.py
==========================
Claude Haiku extraction layer.

Converts a free-text patient answer into a canonical value that the
doctor's IntakeEngine can record via record_answer().

Response-type-aware prompting ensures Haiku knows whether it's
extracting a boolean, a pain scale, a time phrase, or free narrative —
rather than applying one generic prompt to everything.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intake_engine.config import API_KEYS

import anthropic


# ---------------------------------------------------------------------------
# Response type → extraction strategy
# ---------------------------------------------------------------------------

_STRATEGY = {
    "BOOLEAN_WITH_OPTIONAL_DETAILS": "boolean",
    "SHORT_TEXT":                    "short_text",
    "NARRATIVE_FREE_TEXT":           "narrative",
    "TEMPORAL_WITH_UNIT_OR_SHORT_TEXT": "temporal",
    "TEMPORAL_OR_SHORT_TEXT":        "temporal",
    "SCALE_0_10":                    "scale",
    "NUMERIC_OR_SHORT_TEXT":         "numeric",
    "COUNT_OR_SHORT_TEXT":           "numeric",
}

_STRATEGY_INSTRUCTIONS = {
    "boolean": """\
Extract the patient's yes/no answer.

Return:
{
  "canonical_answer": "yes" | "no" | "unknown",
  "detail_value": "<detail string if positive answer includes specifics, else null>",
  "confidence": "high" | "medium" | "low"
}

Rules:
- canonical_answer must be exactly "yes", "no", or "unknown"
- "yes"     = patient clearly affirms the question
- "no"      = patient clearly denies the question
- "unknown" = genuinely unsure, not assessed, or ambiguous
- detail_value: only set when canonical_answer is "yes" AND the patient
  provided descriptive detail in the same answer beyond a bare "yes".
  Example: "Yes, mostly on the left side" → detail_value = "mostly on the left side"
  Example: "Yes" → detail_value = null
- confidence: "high" if boolean is unambiguous, "medium" if inferred, "low" if very unclear
""",

    "scale": """\
Extract a numeric severity rating.

Return:
{
  "canonical_answer": "<number as string, e.g. '7' or '8/10'>",
  "detail_value": null,
  "confidence": "high" | "medium" | "low"
}

Rules:
- "7 out of 10", "about a 7", "7/10" → canonical_answer = "7"
- A range like "6 or 7" → "6-7"
- Verbal descriptors without numbers (e.g. "severe") → use the patient's exact words
""",

    "temporal": """\
Extract a time phrase.

Return:
{
  "canonical_answer": "<cleaned temporal phrase, e.g. '2 hours ago', 'three days', 'this morning'>",
  "detail_value": null,
  "confidence": "high" | "medium" | "low"
}

Rules:
- Preserve the patient's own words, cleaned of filler
- Include unit (minutes, hours, days, weeks) if stated
- If vague (e.g. "a while back"), record as-is
""",

    "narrative": """\
Extract the patient's narrative.

Return:
{
  "canonical_answer": "<patient's answer with only true filler removed>",
  "detail_value": null,
  "confidence": "high"
}

Rules:
- Preserve clinical meaning exactly — do not summarise or paraphrase
- Remove only: "um", "uh", "like", "you know", "sort of", "kind of"
- Keep all clinical content verbatim
""",

    "numeric": """\
Extract a number or count.

Return:
{
  "canonical_answer": "<number or numeric phrase>",
  "detail_value": null,
  "confidence": "high" | "medium" | "low"
}
""",

    "short_text": """\
Extract the patient's answer concisely.

Return:
{
  "canonical_answer": "<patient's answer, clinically accurate and concise>",
  "detail_value": null,
  "confidence": "high" | "medium" | "low"
}

Rules:
- Preserve clinical meaning
- Remove only filler words
- Do not interpret or rephrase beyond what the patient said
""",
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ExtractionResult:
    """
    Structured output of Haiku extraction for one patient answer.

    canonical_answer  Value to pass to engine.record_answer().
                      For BOOLEAN types: "yes", "no", or "unknown".
                      For all others: the cleaned free-text value.

    detail_value      If a boolean parent answer is positive AND the patient
                      included inline detail, this holds that detail string.
                      The session layer pre-populates the engine's detail_field
                      with this value before the engine's follow-up fires,
                      preventing a redundant question.

    confidence        "high" | "medium" | "low"

    raw_llm_output    Full JSON Haiku returned, for logging/debugging.
    """
    canonical_answer: str
    detail_value: Optional[str] = None
    confidence: str = "high"
    raw_llm_output: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

class HaikuAnswerExtractor:
    """
    Wraps the Anthropic Claude Haiku API to extract structured data
    from free-text patient answers.

    Stateless — safe to share across sessions.
    """

    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        self.client = anthropic.Anthropic(api_key=API_KEYS["anthropic"])
        self.model = model

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def extract(
        self,
        question: dict,
        patient_answer: str,
        engine_state: Optional[dict] = None,
    ) -> ExtractionResult:
        """
        Extract structured data from a patient's free-text answer.

        Args:
            question:       Question dict from engine.get_next_question()
            patient_answer: Raw free-text patient answer
            engine_state:   engine.state dict for context (optional)

        Returns:
            ExtractionResult — canonical_answer is ready for record_answer()
        """
        state = engine_state or {}
        response_type = question.get("response_type", "SHORT_TEXT")
        strategy = _STRATEGY.get(response_type, "short_text")

        user_prompt = self._build_prompt(question, patient_answer, strategy, state)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=(
                "You are a clinical intake extraction assistant. "
                "Your only job is to convert a patient's free-text answer into structured data. "
                "You do not diagnose. You do not choose the next question. "
                "Return only valid JSON. No markdown fences, no explanation."
            ),
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = message.content[0].text.strip()
        parsed = self._parse(raw_text)

        return ExtractionResult(
            canonical_answer=str(parsed.get("canonical_answer", patient_answer)),
            detail_value=parsed.get("detail_value") or None,
            confidence=parsed.get("confidence", "high"),
            raw_llm_output=parsed,
        )

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        question: dict,
        patient_answer: str,
        strategy: str,
        engine_state: dict,
    ) -> str:
        question_block = (
            f"Question field:     {question.get('field', '')}\n"
            f"Question text:      {question.get('text', '')}\n"
            f"Response type:      {question.get('response_type', '')}\n"
            f"Phase:              {question.get('phase', '')}\n"
            f"Canonical concept:  {question.get('canonical_concept', '')}"
        )

        # Minimal state context — only already-captured non-null values
        context = {
            k: v for k, v in engine_state.items()
            if v is not None
            and not k.startswith("_")
            and k != "covered_concepts"
            and v not in ("not_assessed", "unknown")
        }

        instructions = _STRATEGY_INSTRUCTIONS[strategy]

        return (
            f"{question_block}\n\n"
            f"Patient answer:\n{patient_answer}\n\n"
            f"Already captured in session:\n{json.dumps(context, indent=2)}\n\n"
            f"{instructions}\n"
            "Return only the JSON object."
        )

    # ------------------------------------------------------------------
    # JSON parsing with fallback
    # ------------------------------------------------------------------

    def _parse(self, raw_text: str) -> dict:
        cleaned = raw_text.strip()

        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if fenced:
            cleaned = fenced.group(1)
        else:
            first = cleaned.find("{")
            last = cleaned.rfind("}")
            if first != -1 and last != -1 and last > first:
                cleaned = cleaned[first : last + 1]

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "canonical_answer": raw_text,
                "detail_value": None,
                "confidence": "low",
            }
