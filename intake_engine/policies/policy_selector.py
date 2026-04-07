from intake_engine.policies.base_complaint_policy import BaseComplaintPolicy
from intake_engine.policies.complaint_policies import COMPLAINT_POLICIES, get_policy_dict


def _normalize_complaint_name(text):
    if text is None:
        return ""

    normalized = text.strip().lower()
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("_", " ")

    prefixes = [
        "i have ",
        "i'm having ",
        "i am having ",
        "i've been having ",
        "ive been having ",
        "my ",
    ]

    for prefix in prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
            break

    normalized = normalized.rstrip(" .,!?:;")
    return normalized


def _make_lookup_variants(text):
    normalized = _normalize_complaint_name(text)

    space_version = normalized
    underscore_version = normalized.replace(" ", "_")

    return {
        space_version,
        underscore_version,
    }


def get_policy_for_complaint(chief_complaint):
    lookup_variants = _make_lookup_variants(chief_complaint)

    for variant in lookup_variants:
        policy_dict = get_policy_dict(variant)
        if policy_dict is not None:
            return BaseComplaintPolicy(policy_dict)

    for policy_name, policy_dict in COMPLAINT_POLICIES.items():
        aliases = policy_dict.get("aliases", [])

        normalized_aliases = set()
        for alias in aliases:
            normalized_aliases.update(_make_lookup_variants(alias))

        if lookup_variants & normalized_aliases:
            return BaseComplaintPolicy(get_policy_dict(policy_name))

    generic_policy = {
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

    return BaseComplaintPolicy(generic_policy)