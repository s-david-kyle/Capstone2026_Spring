from intake_engine.policies.complaint_policies import HeadachePolicy, ChestPainPolicy
from intake_engine.policies.base_complaint_policy import BaseComplaintPolicy


class GenericPolicy(BaseComplaintPolicy):
    policy_name = "generic"

    must_characterize = [
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
    ]

    high_priority_followups = [
        "medications",
        "allergies",
    ]


POLICY_REGISTRY = [
    {
        "policy_class": HeadachePolicy,
        "match_terms": ["headache", "migraine", "head pain"],
    },
    {
        "policy_class": ChestPainPolicy,
        "match_terms": ["chest pain", "chest pressure", "chest tightness"],
    },
]


def _normalize_complaint(chief_complaint):
    return (chief_complaint or "").strip().lower()


def get_policy_for_complaint(chief_complaint):
    complaint = _normalize_complaint(chief_complaint)

    for entry in POLICY_REGISTRY:
        if any(term in complaint for term in entry["match_terms"]):
            return entry["policy_class"]()

    return GenericPolicy()