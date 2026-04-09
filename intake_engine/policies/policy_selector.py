"""
policy_selector.py
==================
Maps a raw chief complaint string to a BaseComplaintPolicy instance.

Matching runs four tiers in order, stopping at the first hit:

  1. Exact key match        -- complaint normalizes to a policy key directly
  2. Exact alias match      -- complaint normalizes to any listed alias
  3. Substring containment  -- any alias is a substring of the complaint
                               or the complaint is a substring of any alias
  4. Keyword scoring        -- count alias content-words (len >= 4) found in
                               the complaint; return best scorer if score >= 2

Falls back to the generic policy when no tier matches.

This is intentionally deterministic — no LLM call, no embeddings. The four
tiers handle the real-world variation seen in patient input (lateral
qualifiers like "left", inflected words, colloquial phrasing) without
needing an exhaustive alias list.
"""

from intake_engine.policies.base_complaint_policy import BaseComplaintPolicy
from intake_engine.policies.complaint_policies import COMPLAINT_POLICIES, get_policy_dict


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

_STRIP_PREFIXES = [
    "i have ",
    "i'm having ",
    "i am having ",
    "i've been having ",
    "ive been having ",
    "my ",
]


def _normalize(text: str) -> str:
    """
    Lowercase, strip common patient lead-ins, collapse punctuation.
    Returns a plain space-separated string ready for matching.
    """
    if text is None:
        return ""

    if isinstance(text, list):
        text = " ".join(str(x) for x in text if x)

    normalized = text.strip().lower()
    normalized = normalized.replace("-", " ").replace("_", " ")

    for prefix in _STRIP_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
            break

    return normalized.rstrip(" .,!?:;")


def _variants(text: str) -> set:
    """Return both space and underscore versions of a normalized string."""
    n = _normalize(text)
    return {n, n.replace(" ", "_")}


# ---------------------------------------------------------------------------
# Tier 4: keyword scoring
# ---------------------------------------------------------------------------

def _keyword_score(complaint_normalized: str, policy_dict: dict) -> int:
    """
    Count how many content words (len >= 4) from a policy's aliases appear
    in the normalized complaint string.
    """
    score = 0
    for alias in policy_dict.get("aliases", []):
        alias_n = _normalize(alias)
        for word in alias_n.split():
            if len(word) >= 4 and word in complaint_normalized:
                score += 1
    return score


# ---------------------------------------------------------------------------
# Generic fallback policy
# ---------------------------------------------------------------------------

_GENERIC_POLICY = {
    "policy_name": "generic",
    "display_name": "Generic Complaint",
    "aliases": [],
    "critical_followups": [],
    "must_characterize": [
        "onset",
        "location",
        "duration",
        "severity",
        "timing",
        "course",
        "character",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
    ],
    "red_flags": [],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": False,
        "required_characterization_targets": [
            "onset",
            "location",
            "duration",
            "severity",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 4,
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_policy_for_complaint(chief_complaint: str) -> BaseComplaintPolicy:
    """
    Return the best-matching BaseComplaintPolicy for a chief complaint string.

    Matching order
    --------------
    1. Exact key match on COMPLAINT_POLICIES
    2. Exact alias match (both space and underscore variants)
    3. Substring containment between complaint and any alias
    4. Keyword scoring — best policy wins if score >= 2
    5. Generic fallback
    """
    complaint_variants = _variants(chief_complaint)
    complaint_normalized = _normalize(chief_complaint)

    # --- Tier 1: exact policy key ---
    for variant in complaint_variants:
        if variant in COMPLAINT_POLICIES:
            return BaseComplaintPolicy(get_policy_dict(variant))

    # --- Tier 2: exact alias match ---
    for policy_name, policy_dict in COMPLAINT_POLICIES.items():
        alias_variants: set = set()
        for alias in policy_dict.get("aliases", []):
            alias_variants.update(_variants(alias))
        if complaint_variants & alias_variants:
            return BaseComplaintPolicy(get_policy_dict(policy_name))

    # --- Tier 3: substring containment ---
    for policy_name, policy_dict in COMPLAINT_POLICIES.items():
        for alias in policy_dict.get("aliases", []):
            alias_n = _normalize(alias)
            if alias_n in complaint_normalized or complaint_normalized in alias_n:
                return BaseComplaintPolicy(get_policy_dict(policy_name))

    # --- Tier 4: keyword scoring ---
    scores = {
        policy_name: _keyword_score(complaint_normalized, policy_dict)
        for policy_name, policy_dict in COMPLAINT_POLICIES.items()
    }
    best_policy_name = max(scores, key=scores.get)
    if scores[best_policy_name] >= 2:
        return BaseComplaintPolicy(get_policy_dict(best_policy_name))

    # --- Fallback: generic ---
    return BaseComplaintPolicy(_GENERIC_POLICY)
