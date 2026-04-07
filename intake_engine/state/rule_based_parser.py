from intake_engine.policies.target_specs import TARGET_SPECS


def normalize_chief_complaint(text):
    complaint = text.strip().lower()

    prefixes = [
        "i have ",
        "i'm having ",
        "i am having ",
        "i've been having ",
        "ive been having ",
        "my ",
        "it is ",
        "it's ",
    ]

    for prefix in prefixes:
        if complaint.startswith(prefix):
            complaint = complaint[len(prefix):].strip()
            break

    for article in ["a ", "an "]:
        if complaint.startswith(article):
            complaint = complaint[len(article):].strip()

    complaint = complaint.rstrip(" .,!?:;")

    return complaint


def split_free_text_list(text):
    normalized = text.strip().lower()
    normalized = normalized.replace(", and ", ", ")
    normalized = normalized.replace(" and ", ", ")

    parts = [part.strip() for part in normalized.split(",")]
    cleaned_parts = []

    for part in parts:
        if part.startswith("and "):
            part = part[4:].strip()

        if part:
            cleaned_parts.append(part)

    return cleaned_parts


def extract_severity(text):
    answer = text.strip().lower()

    for value in range(11):
        if f"{value}/10" in answer:
            return f"{value}/10"
        if f"{value} out of 10" in answer:
            return f"{value}/10"

    tokens = answer.replace(",", " ").split()
    for token in tokens:
        if token.isdigit():
            numeric_value = int(token)
            if 0 <= numeric_value <= 10:
                return f"{numeric_value}/10"

    return text.strip()


def extract_duration(text):
    answer = text.strip().lower()

    replacements = {
        "an hour": "1 hour",
        "a hour": "1 hour",
        "a day": "1 day",
        "a week": "1 week",
        "a month": "1 month",
    }

    for old, new in replacements.items():
        answer = answer.replace(old, new)

    if answer.startswith("for "):
        answer = answer[4:].strip()

    return answer


def extract_escalation_signals(text):
    answer = text.strip().lower()
    signals = []

    breathing_terms = [
        "short of breath",
        "trouble breathing",
        "hard to breathe",
        "can't breathe",
        "cannot breathe",
        "breathing is hard",
    ]

    fainting_terms = [
        "pass out",
        "passed out",
        "faint",
        "fainted",
        "lightheaded",
        "dizzy",
        "felt like i might pass out",
    ]

    worsening_terms = [
        "getting worse",
        "worse",
        "much worse",
        "rapidly worse",
    ]

    for term in breathing_terms:
        if term in answer:
            signals.append("active_breathing_difficulty")
            break

    for term in fainting_terms:
        if term in answer:
            signals.append("syncope_or_presyncope")
            break

    for term in worsening_terms:
        if term in answer:
            signals.append("rapid_worsening")
            break

    return signals


def extract_yes_no_unknown(text):
    answer = text.strip().lower()

    yes_terms = {
        "yes", "y", "yeah", "yep", "true", "it did", "i did", "definitely"
    }
    no_terms = {
        "no", "n", "nope", "false", "not really", "it did not", "i did not"
    }

    if answer in yes_terms:
        return True

    if answer in no_terms:
        return False

    if "yes" in answer:
        return True

    if "no" in answer:
        return False

    return None


def extract_neurologic_symptom_terms(text):
    answer = text.strip().lower()

    term_map = {
        "weakness": ["weak", "weakness"],
        "numbness": ["numb", "numbness", "tingling"],
        "trouble_speaking": ["trouble speaking", "slurred speech", "couldn't talk", "difficulty speaking"],
        "vision_problems": ["vision problems", "blurry vision", "double vision", "vision change", "visual change"],
        "confusion": ["confused", "confusion"],
    }

    negation_starts = [
        "no ",
        "not ",
        "denies ",
        "deny ",
        "without ",
    ]

    findings = []

    for label, phrases in term_map.items():
        positive_found = False
        negated_found = False

        for phrase in phrases:
            if phrase in answer:
                for neg in negation_starts:
                    if neg + phrase in answer:
                        negated_found = True

                for neg in negation_starts:
                    for other_phrases in term_map.values():
                        for other_phrase in other_phrases:
                            coordinated_pattern = f"{neg}{other_phrase} or {phrase}"
                            if coordinated_pattern in answer:
                                negated_found = True

                if not negated_found:
                    positive_found = True

        if positive_found and not negated_found:
            findings.append(label)

    return findings


def answer_is_explicit_neurologic_negation(text):
    answer = text.strip().lower()

    negative_markers = [
        "no weakness",
        "no numbness",
        "no trouble speaking",
        "no confusion",
        "no vision changes",
        "no blurry vision",
        "no double vision",
        "denies weakness",
        "denies numbness",
        "denies trouble speaking",
        "denies confusion",
        "denies vision changes",
        "without weakness",
        "without numbness",
        "without trouble speaking",
        "without confusion",
        "without vision changes",
    ]

    if answer.startswith("no "):
        return True

    if answer.startswith("denies "):
        return True

    if answer.startswith("without "):
        return True

    for marker in negative_markers:
        if marker in answer:
            return True

    return False


def intent_to_target(intent):
    for target, spec in TARGET_SPECS.items():
        if spec.get("intent") == intent:
            return target

    return None


def build_generic_update_from_target_spec(target, answer):
    spec = TARGET_SPECS.get(target)
    if spec is None:
        return None

    state_path = spec.get("state_path")
    parse_mode = spec.get("fallback_parse_mode", "text")
    default_update_mode = spec.get("default_update_mode", "set")
    extra_set_fields = spec.get("extra_set_fields", [])
    extra_append_fields = spec.get("extra_append_fields", [])

    update = {
        "set_fields": {},
        "append_fields": {},
        "flags_to_add": [],
        "missing_clarifications_to_add": [],
    }

    update["set_fields"]["conversation_meta.last_answer_status"] = "answered"
    update["set_fields"]["conversation_meta.early_exit_reason"] = None

    if parse_mode == "yes_no":
        value = extract_yes_no_unknown(answer)

        if default_update_mode == "append":
            update["append_fields"][state_path] = [value]
        else:
            update["set_fields"][state_path] = value

    elif parse_mode == "list_append":
        values = split_free_text_list(answer) or [answer]

        if default_update_mode == "append":
            update["append_fields"][state_path] = values
        else:
            update["set_fields"][state_path] = values

        for extra_field in extra_append_fields:
            update["append_fields"][extra_field] = list(values)

    elif parse_mode == "text":
        value = answer

        if default_update_mode == "append":
            update["append_fields"][state_path] = [value]
        else:
            update["set_fields"][state_path] = value

    elif parse_mode == "special_duration":
        update["set_fields"][state_path] = extract_duration(answer)

    elif parse_mode == "special_severity":
        update["set_fields"][state_path] = extract_severity(answer)

    elif parse_mode == "special_neurologic_symptoms":
        findings = extract_neurologic_symptom_terms(answer)
        yes_no_value = extract_yes_no_unknown(answer)

        update["set_fields"][state_path] = True if findings else yes_no_value

        if "policy_answers.neurologic_symptom_terms" in extra_set_fields:
            update["set_fields"]["policy_answers.neurologic_symptom_terms"] = findings

        if findings:
            for extra_field in extra_append_fields:
                update["append_fields"][extra_field] = list(findings)

    else:
        return None

    return update


def build_update_from_answer(intent, patient_answer):
    answer = patient_answer.strip()

    update = {
        "set_fields": {
            "conversation_meta.last_answer_status": "answered",
            "conversation_meta.early_exit_reason": None,
        },
        "append_fields": {},
        "flags_to_add": [],
        "missing_clarifications_to_add": [],
    }

    if intent == "ask_main_reason_for_visit":
        update["set_fields"]["chief_complaint_primary"] = normalize_chief_complaint(answer)
        return update

    if intent in {"escalate_high_risk_chest_pain", "ask_immediate_safety_check"}:
        signals = extract_escalation_signals(answer)

        if signals:
            update["append_fields"]["conversation_meta.acuity_signal"] = signals
            update["flags_to_add"] = signals

        update["append_fields"]["pertinent_positives"] = [answer]
        return update

    target = intent_to_target(intent)
    generic_update = build_generic_update_from_target_spec(target, answer)

    if generic_update is not None:
        return generic_update

    return update