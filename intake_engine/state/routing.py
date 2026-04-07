from intake_engine.policies.policy_selector import get_policy_for_complaint


OVERRIDE_RULES = [
    {
        "name": "user_requested_stop",
        "intent": "end_intake_early",
        "target": None,
        "source": "global_override",
        "requires_user_requested_stop": True,
    },
    {
        "name": "natural_intake_finished",
        "intent": "end_intake_naturally",
        "target": None,
        "source": "global_override",
        "requires_natural_completion": True,
    },
    {
        "name": "immediate_attention_from_acuity",
        "intent": "recommend_immediate_attention",
        "target": None,
        "source": "global_override",
        "requires_any_acuity_signals": [
            "active_breathing_difficulty",
            "syncope_or_presyncope",
        ],
    },
    {
        "name": "high_risk_chest_pain_flag",
        "intent": "escalate_high_risk_chest_pain",
        "target": None,
        "source": "global_override",
        "requires_any_flags": [
            "chest_pain_with_shortness_of_breath",
        ],
    },
    {
        "name": "severe_symptom_safety_check",
        "intent": "ask_immediate_safety_check",
        "target": None,
        "source": "global_override",
        "requires_any_flags": [
            "severe_symptom_intensity",
        ],
        "requires_chief_complaint": True,
    },
    {
        "name": "entry_question",
        "intent": "ask_main_reason_for_visit",
        "target": None,
        "source": "global_override",
        "requires_missing_chief_complaint": True,
    },
]


def override_rule_matches(data, rule):
    chief_complaint = data["chief_complaint_primary"]
    flags = set(data["flags"])
    acuity_signals = set(data["conversation_meta"]["acuity_signal"])

    required_flags = set(rule.get("requires_any_flags", []))
    required_acuity_signals = set(rule.get("requires_any_acuity_signals", []))

    if rule.get("requires_user_requested_stop"):
        if not data["conversation_meta"].get("user_requested_stop", False):
            return False

    if rule.get("requires_natural_completion"):
        if not data["conversation_meta"].get("natural_completion_ready", False):
            return False

    if required_flags and not (flags & required_flags):
        return False

    if required_acuity_signals and not (acuity_signals & required_acuity_signals):
        return False

    if rule.get("requires_chief_complaint") and not chief_complaint:
        return False

    if rule.get("requires_missing_chief_complaint") and chief_complaint:
        return False

    return True


def choose_global_override_step(data):
    for rule in OVERRIDE_RULES:
        if override_rule_matches(data, rule):
            return {
                "intent": rule["intent"],
                "target": rule.get("target"),
                "source": rule.get("source", "global_override"),
                "rule_name": rule["name"],
            }

    return None


def choose_policy_step(data, to_dict_callable):
    chief_complaint = data["chief_complaint_primary"]

    if not chief_complaint:
        return None

    policy = get_policy_for_complaint(chief_complaint)
    target = policy.choose_next_target(to_dict_callable())
    intent = policy.target_to_intent(target)

    return {
        "intent": intent,
        "target": target,
        "policy_name": getattr(policy, "policy_name", None),
    }


def determine_next_step(data, to_dict_callable):
    override_step = choose_global_override_step(data)

    if override_step is not None:
        return {
            "intent": override_step["intent"],
            "target": override_step["target"],
            "source": override_step["source"],
        }

    policy_step = choose_policy_step(data, to_dict_callable)

    if policy_step is not None and policy_step["intent"] is not None:
        return {
            "intent": policy_step["intent"],
            "target": policy_step["target"],
            "source": "policy",
        }

    return {
        "intent": "summarize_and_check_for_anything_else",
        "target": None,
        "source": "wrap_up",
    }