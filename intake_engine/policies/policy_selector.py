from intake_engine.policies.base_complaint_policy import BaseComplaintPolicy
from intake_engine.policies.complaint_policies import get_all_policy_dicts, get_policy_dict


GENERIC_POLICY = {
    "policy_name": "generic",
    "display_name": "Generic",
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
        "min_required_characterization_count": 3,
    },
}


def _normalize_complaint(chief_complaint):
    return (chief_complaint or "").strip().lower()


def get_policy_for_complaint(chief_complaint):
    complaint = _normalize_complaint(chief_complaint)

    if not complaint:
        return BaseComplaintPolicy(GENERIC_POLICY)

    normalized_policy_name = complaint.replace(" ", "_")
    policy_definition = get_policy_dict(normalized_policy_name)

    if policy_definition is not None:
        return BaseComplaintPolicy(policy_definition)

    all_policies = get_all_policy_dicts()

    for policy_definition in all_policies.values():
        aliases = [alias.lower() for alias in policy_definition.get("aliases", [])]

        if complaint in aliases:
            return BaseComplaintPolicy(policy_definition)

        if any(alias in complaint for alias in aliases):
            return BaseComplaintPolicy(policy_definition)

    return BaseComplaintPolicy(GENERIC_POLICY)