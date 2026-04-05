from copy import deepcopy

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


class IntakeState:
    facet_order = [
        "chief_complaint_primary",
        "other_concerns",
        "hpi",
        "pertinent_positives",
        "pertinent_negatives",
        "pmh_psh",
        "medications",
        "allergies",
        "social_factors",
        "missing_clarifications",
        "flags",
    ]

    intake_template = {
        "chief_complaint_primary": None,
        "other_concerns": [],
        "hpi": {
            "summary": None,
            "onset": None,
            "location": None,
            "duration": None,
            "timing": None,
            "course": None,
            "character": None,
            "severity": None,
            "aggravating_factors": [],
            "relieving_factors": [],
            "associated_symptoms": [],
            "context": None,
        },
        "pertinent_positives": [],
        "pertinent_negatives": [],
        "pmh_psh": {
            "past_medical_history": [],
            "past_surgical_history": [],
        },
        "medications": [],
        "allergies": [],
        "social_factors": [],
        "missing_clarifications": [],
        "flags": [],
        "policy_answers": {
            "sudden_severe_onset": None,
            "neurologic_symptoms": None,
            "neurologic_symptom_terms": [],
            "visual_changes": None,
            "confusion_or_ams": None,
            "fever_or_neck_stiffness": None,
            "head_trauma": None,
            "pregnancy_or_postpartum_context": None,
            "photophobia": None,
            "phonophobia": None,
            "nausea_or_vomiting": None,
            "aura_features": [],
            "exertional_trigger": None,
            "positional_component": None,
            "new_or_progressive_pattern": None,
            "medication_overuse_context": None,
            "shortness_of_breath": None,
            "syncope_or_presyncope": None,
            "rapid_worsening": None,
            "radiation": [],
            "nausea": None,
            "diaphoresis": None,
            "exertional_component": None,
        },
        "conversation_meta": {
            "visit_id": None,
            "turn_count": 0,
            "language": "en",
            "acuity_signal": [],
            "intake_complete": False,
            "last_question_intent": None,
            "last_question_target": None,
            "last_question_text": None,
            "last_answer_status": None,
            "user_requested_stop": False,
            "early_exit_reason": None,
            "natural_completion_ready": False,
            "question_status": {},
            "transcript": [],
        },
        "derived_outputs": {
            "patient_friendly_summary": None,
            "clinical_handoff_summary": None,
        },
        "future_context": {
            "ehr_data": None,
            "prior_encounters": None,
            "problem_list": None,
            "recent_labs": None,
            "recent_imaging": None,
            "external_documents": None,
        },
    }

    def __init__(self, data = None):
        self.data = deepcopy(data) if data is not None else deepcopy(self.intake_template)

    def reset(self):
        self.data = deepcopy(self.intake_template)
        return self

    def to_dict(self):
        return deepcopy(self.data)

    def log_turn(self, speaker, text, intent = None, metadata = None):
        entry = {
            "turn_index": len(self.data["conversation_meta"]["transcript"]) + 1,
            "speaker": speaker,
            "text": text,
            "intent": intent,
            "metadata": metadata or {},
        }
        self.data["conversation_meta"]["transcript"].append(entry)
        return self

    def _get_nested_parent_and_key(self, dotted_path):
        keys = dotted_path.split(".")
        parent = self.data

        for key in keys[:-1]:
            if key not in parent:
                raise KeyError(f"Invalid path segment '{key}' in '{dotted_path}'")

            parent = parent[key]

            if not isinstance(parent, dict):
                raise TypeError(
                    f"Path '{dotted_path}' does not resolve through dictionaries cleanly"
                )

        return parent, keys[-1]

    def _append_unique(self, target_list, values):
        if not isinstance(target_list, list):
            raise TypeError("target_list must be a list")

        if not isinstance(values, list):
            values = [values]

        for value in values:
            if value not in target_list:
                target_list.append(value)

    def _is_deterministic_intent(self, intent):
        return intent in {
            "recommend_immediate_attention",
            "escalate_high_risk_chest_pain",
            "ask_immediate_safety_check",
            "ask_main_reason_for_visit",
            "summarize_and_check_for_anything_else",
            "end_intake_early",
            "end_intake_naturally",
        }

    def apply_update(self, update):
        set_fields = update.get("set_fields", {})
        append_fields = update.get("append_fields", {})
        flags_to_add = update.get("flags_to_add", [])
        missing_to_add = update.get("missing_clarifications_to_add", [])

        for dotted_path, value in set_fields.items():
            parent, key = self._get_nested_parent_and_key(dotted_path)

            if key not in parent:
                raise KeyError(f"Invalid final key '{key}' in '{dotted_path}'")

            parent[key] = value

        for dotted_path, values in append_fields.items():
            parent, key = self._get_nested_parent_and_key(dotted_path)

            if key not in parent:
                raise KeyError(f"Invalid final key '{key}' in '{dotted_path}'")

            if not isinstance(parent[key], list):
                raise TypeError(
                    f"Field '{dotted_path}' is not a list and cannot be appended to"
                )

            self._append_unique(parent[key], values)

        self._append_unique(self.data["flags"], flags_to_add)
        self._append_unique(self.data["missing_clarifications"], missing_to_add)

        self.data["conversation_meta"]["turn_count"] += 1
        return self

    def collect_missing_clarifications(self):
        missing = []

        chief_complaint = self.data["chief_complaint_primary"]
        hpi = self.data["hpi"]

        if not chief_complaint:
            missing.append("main reason for visit")
            return missing

        if not hpi["onset"]:
            missing.append("when it started")

        if not hpi["location"]:
            missing.append("where the symptom is located")

        if not hpi["duration"]:
            missing.append("how long it has been going on")

        if not hpi["severity"]:
            missing.append("how severe it is")

        if not hpi["associated_symptoms"]:
            missing.append("associated symptoms")

        return missing

    def refresh_missing_clarifications(self):
        self.data["missing_clarifications"] = self.collect_missing_clarifications()
        return self

    def detect_basic_flags(self):
        chief_complaint = (self.data["chief_complaint_primary"] or "").lower()
        severity = (self.data["hpi"]["severity"] or "").lower()
        associated_symptoms = [
            symptom.lower() for symptom in self.data["hpi"]["associated_symptoms"]
        ]

        flags = []

        if "chest pain" in chief_complaint:
            if "shortness of breath" in associated_symptoms:
                flags.append("chest_pain_with_shortness_of_breath")

            if "sweating" in associated_symptoms:
                flags.append("chest_pain_with_diaphoresis")

        if severity in {"8/10", "9/10", "10/10"}:
            flags.append("severe_symptom_intensity")

        return flags

    def refresh_flags(self):
        detected_flags = self.detect_basic_flags()
        self._append_unique(self.data["flags"], detected_flags)
        return self

    def _override_rule_matches(self, rule):
        chief_complaint = self.data["chief_complaint_primary"]
        flags = set(self.data["flags"])
        acuity_signals = set(self.data["conversation_meta"]["acuity_signal"])

        required_flags = set(rule.get("requires_any_flags", []))
        required_acuity_signals = set(rule.get("requires_any_acuity_signals", []))

        if rule.get("requires_user_requested_stop"):
            if not self.data["conversation_meta"].get("user_requested_stop", False):
                return False

        if rule.get("requires_natural_completion"):
            if not self.data["conversation_meta"].get("natural_completion_ready", False):
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

    def _choose_global_override_step(self):
        for rule in OVERRIDE_RULES:
            if self._override_rule_matches(rule):
                return {
                    "intent": rule["intent"],
                    "target": rule.get("target"),
                    "source": rule.get("source", "global_override"),
                    "rule_name": rule["name"],
                }

        return None

    def _choose_policy_step(self):
        chief_complaint = self.data["chief_complaint_primary"]

        if not chief_complaint:
            return None

        policy = get_policy_for_complaint(chief_complaint)
        target = policy.choose_next_target(self.to_dict())
        intent = policy.target_to_intent(target)

        return {
            "intent": intent,
            "target": target,
            "policy_name": getattr(policy, "policy_name", None),
        }

    def determine_next_step(self):
        override_step = self._choose_global_override_step()

        if override_step is not None:
            return {
                "intent": override_step["intent"],
                "target": override_step["target"],
                "source": override_step["source"],
            }

        policy_step = self._choose_policy_step()

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

    def update_completion_status(self):
        next_step = self.determine_next_step()

        if next_step["intent"] in {
            "recommend_immediate_attention",
            "end_intake_early",
            "end_intake_naturally",
        }:
            self.data["conversation_meta"]["intake_complete"] = True

        return self

    def choose_next_question_intent(self):
        return self.determine_next_step()["intent"]

    def render_question_for_intent(self, intent):
        """
        Deterministic fallback rendering for urgent, entry, and generic prompts.
        Normal intake questions should usually come from the LLM question generator.
        """
        if intent == "recommend_immediate_attention":
            return (
                "Your answers suggest this may need immediate medical attention. "
                "Please alert nearby medical staff right away or seek emergency help now."
            )

        if intent == "escalate_high_risk_chest_pain":
            return (
                "Your symptoms may need urgent attention. "
                "Are you having trouble breathing right now or feeling like you might pass out?"
            )

        if intent == "ask_immediate_safety_check":
            return (
                "Are your symptoms getting worse right now, "
                "or do you feel like you need immediate help?"
            )

        if intent == "ask_main_reason_for_visit":
            return "Could you tell me what’s been bothering you today?"

        if intent == "end_intake_early":
            return (
                "Okay. We can stop here. "
                "If you need help right now or your symptoms are getting worse, "
                "please seek medical attention immediately."
            )

        if intent == "end_intake_naturally":
            return "Thank you. I have what I need for now."

        if intent == "summarize_and_check_for_anything_else":
            return "Is there anything else important you want to make sure I know?"

        return "Is there anything else important you want to make sure I know?"

    def get_next_question(self, question_generator = None):
        next_step = self.determine_next_step()
        intent = next_step["intent"]
        target = next_step["target"]

        if self._is_deterministic_intent(intent):
            question = self.render_question_for_intent(intent)
        elif question_generator is not None:
            try:
                question = question_generator.generate_question(
                    intake_state = self.to_dict(),
                    target = target,
                    intent = intent,
                )
            except Exception as e:
                print("QUESTION GENERATION ERROR:", type(e).__name__, str(e))
                question = self.render_question_for_intent(intent)
        else:
            question = self.render_question_for_intent(intent)

        self.data["conversation_meta"]["last_question_intent"] = intent
        self.data["conversation_meta"]["last_question_target"] = target
        self.data["conversation_meta"]["last_question_text"] = question

        self.log_turn(
            speaker = "system",
            text = question,
            intent = intent,
            metadata = {
                "target": target,
                "step_source": next_step["source"],
            } if target is not None else {
                "step_source": next_step["source"],
            },
        )

        return {
            "intent": intent,
            "target": target,
            "question": question,
        }

    def _normalize_chief_complaint(self, text):
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

    def _split_free_text_list(self, text):
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

    def _extract_severity(self, text):
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

    def _extract_duration(self, text):
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

    def _extract_escalation_signals(self, text):
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

    def _extract_yes_no_unknown(self, text):
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

    def _extract_neurologic_symptom_terms(self, text):
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

    def _answer_is_explicit_neurologic_negation(self, text):
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

    def _classify_special_answer_status(self, text):
        answer = text.strip().lower()

        stop_phrases = [
            "stop",
            "quit",
            "end",
            "end this",
            "stop this",
            "i want to stop",
            "i want to end this",
            "i'm done",
            "im done",
            "no more questions",
        ]

        decline_phrases = [
            "prefer not to answer",
            "don't want to answer",
            "do not want to answer",
            "rather not say",
            "prefer not to say",
            "skip",
            "pass",
        ]

        unknown_phrases = [
            "don't know",
            "do not know",
            "not sure",
            "unsure",
            "i'm not sure",
            "unknown",
            "can't remember",
            "cannot remember",
            "i dont know",
            "idk",
        ]

        if any(phrase in answer for phrase in stop_phrases):
            return "stop"

        if any(phrase in answer for phrase in decline_phrases):
            return "declined"

        if any(phrase in answer for phrase in unknown_phrases):
            return "unknown"

        return None

    def _build_special_answer_update(self, status):
        update = {
            "set_fields": {},
            "append_fields": {},
            "flags_to_add": [],
            "missing_clarifications_to_add": [],
        }

        update["set_fields"]["conversation_meta.last_answer_status"] = status

        if status == "stop":
            update["set_fields"]["conversation_meta.user_requested_stop"] = True
            update["set_fields"]["conversation_meta.early_exit_reason"] = "user_requested_stop"

        return update

    def _is_negative_wrap_up_answer(self, text):
        answer = text.strip().lower()

        negative_terms = {
            "no",
            "nope",
            "nothing else",
            "that's all",
            "thats all",
            "no thank you",
            "no thanks",
        }

        if answer in negative_terms:
            return True

        if answer.startswith("no "):
            return True

        return False

    def _build_wrap_up_update(self, patient_answer):
        update = {
            "set_fields": {
                "conversation_meta.last_answer_status": "answered",
                "conversation_meta.early_exit_reason": None,
            },
            "append_fields": {},
            "flags_to_add": [],
            "missing_clarifications_to_add": [],
        }

        if self._is_negative_wrap_up_answer(patient_answer):
            update["set_fields"]["conversation_meta.natural_completion_ready"] = True
        else:
            update["append_fields"]["other_concerns"] = [patient_answer]

        return update

    def _postprocess_llm_update_for_intent(self, intent, patient_answer, applied_update):
        yes_no_value = self._extract_yes_no_unknown(patient_answer)

        semantic_yes_no_targets = {
            "ask_neurologic_symptoms": "policy_answers.neurologic_symptoms",
            "ask_visual_changes": "policy_answers.visual_changes",
            "ask_confusion_or_ams": "policy_answers.confusion_or_ams",
            "ask_fever_or_neck_stiffness": "policy_answers.fever_or_neck_stiffness",
            "ask_head_trauma": "policy_answers.head_trauma",
            "ask_pregnancy_or_postpartum_context": "policy_answers.pregnancy_or_postpartum_context",
            "ask_shortness_of_breath": "policy_answers.shortness_of_breath",
            "ask_syncope_or_presyncope": "policy_answers.syncope_or_presyncope",
            "ask_rapid_worsening": "policy_answers.rapid_worsening",
        }

        if intent in semantic_yes_no_targets and yes_no_value is not None:
            applied_update.setdefault("set_fields", {})
            applied_update["set_fields"][semantic_yes_no_targets[intent]] = yes_no_value

            if intent == "ask_neurologic_symptoms" and yes_no_value is False:
                applied_update["set_fields"]["policy_answers.neurologic_symptom_terms"] = []

                applied_update.setdefault("append_fields", {})
                if "pertinent_positives" in applied_update["append_fields"]:
                    applied_update["append_fields"]["pertinent_positives"] = []

            return applied_update

        if intent == "ask_neurologic_symptoms":
            if self._answer_is_explicit_neurologic_negation(patient_answer):
                applied_update.setdefault("set_fields", {})
                applied_update["set_fields"]["policy_answers.neurologic_symptoms"] = False
                applied_update["set_fields"]["policy_answers.neurologic_symptom_terms"] = []

                applied_update.setdefault("append_fields", {})
                if "pertinent_positives" in applied_update["append_fields"]:
                    applied_update["append_fields"]["pertinent_positives"] = []

        return applied_update

    def _intent_to_target(self, intent):
        from intake_engine.policies.target_specs import TARGET_SPECS

        for target, spec in TARGET_SPECS.items():
            if spec.get("intent") == intent:
                return target

        return None

    def _answer_status_to_question_status(self, answer_status):
        mapping = {
            "answered": "asked_answered",
            "unknown": "asked_unknown",
            "declined": "asked_declined",
        }
        return mapping.get(answer_status)

    def _record_question_status(self, intent):
        target = self._intent_to_target(intent)

        if target is None:
            return

        answer_status = self.data["conversation_meta"].get("last_answer_status")
        question_status = self._answer_status_to_question_status(answer_status)

        if question_status is None:
            return

        self.data["conversation_meta"]["question_status"][target] = question_status

    def _build_generic_update_from_target_spec(self, target, answer):
        from intake_engine.policies.target_specs import TARGET_SPECS

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
            value = self._extract_yes_no_unknown(answer)

            if default_update_mode == "append":
                update["append_fields"][state_path] = [value]
            else:
                update["set_fields"][state_path] = value

        elif parse_mode == "list_append":
            values = self._split_free_text_list(answer) or [answer]

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
            update["set_fields"][state_path] = self._extract_duration(answer)

        elif parse_mode == "special_severity":
            update["set_fields"][state_path] = self._extract_severity(answer)

        elif parse_mode == "special_neurologic_symptoms":
            findings = self._extract_neurologic_symptom_terms(answer)
            yes_no_value = self._extract_yes_no_unknown(answer)

            update["set_fields"][state_path] = True if findings else yes_no_value

            if "policy_answers.neurologic_symptom_terms" in extra_set_fields:
                update["set_fields"]["policy_answers.neurologic_symptom_terms"] = findings

            if findings:
                for extra_field in extra_append_fields:
                    update["append_fields"][extra_field] = list(findings)

        else:
            return None

        return update

    def build_update_from_answer(self, intent, patient_answer):
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
            update["set_fields"]["chief_complaint_primary"] = self._normalize_chief_complaint(answer)
            return update

        if intent in {"escalate_high_risk_chest_pain", "ask_immediate_safety_check"}:
            signals = self._extract_escalation_signals(answer)

            if signals:
                update["append_fields"]["conversation_meta.acuity_signal"] = signals
                update["flags_to_add"] = signals

            update["append_fields"]["pertinent_positives"] = [answer]
            return update

        target = self._intent_to_target(intent)
        generic_update = self._build_generic_update_from_target_spec(target, answer)

        if generic_update is not None:
            return generic_update

        return update

    def _finalize_patient_turn(
        self,
        current_intent,
        patient_answer,
        applied_update,
        parser_name,
        question_generator = None,
    ):
        self.apply_update(applied_update)
        self._record_question_status(current_intent)
        self.refresh_missing_clarifications()
        self.refresh_flags()
        self.update_completion_status()

        self.log_turn(
            speaker = "patient",
            text = patient_answer,
            intent = current_intent,
            metadata = {
                "applied_update": deepcopy(applied_update),
                "current_flags": deepcopy(self.data["flags"]),
                "current_missing_clarifications": deepcopy(
                    self.data["missing_clarifications"]
                ),
                "parser": parser_name,
            },
        )

        next_question_info = self.get_next_question(
            question_generator = question_generator
        )

        return {
            "current_intent": current_intent,
            "applied_update": applied_update,
            "missing_clarifications": self.data["missing_clarifications"],
            "next_intent": next_question_info["intent"],
            "next_target": next_question_info["target"],
            "next_question": next_question_info["question"],
        }

    def process_answer(self, patient_answer, question_generator = None):
        current_intent = self.data["conversation_meta"]["last_question_intent"]

        if current_intent is None:
            current_intent = self.choose_next_question_intent()

        if current_intent == "summarize_and_check_for_anything_else":
            applied_update = self._build_wrap_up_update(patient_answer)

            return self._finalize_patient_turn(
                current_intent = current_intent,
                patient_answer = patient_answer,
                applied_update = applied_update,
                parser_name = "wrap_up_handler",
                question_generator = question_generator,
            )

        special_status = self._classify_special_answer_status(patient_answer)

        if special_status is not None:
            applied_update = self._build_special_answer_update(special_status)
        else:
            applied_update = self.build_update_from_answer(current_intent, patient_answer)

        return self._finalize_patient_turn(
            current_intent = current_intent,
            patient_answer = patient_answer,
            applied_update = applied_update,
            parser_name = "rule_based",
            question_generator = question_generator,
        )

    def process_answer_with_llm(
        self,
        patient_answer,
        extractor,
        normalizer,
        question_generator = None,
    ):
        current_intent = self.data["conversation_meta"]["last_question_intent"]

        if current_intent is None:
            current_intent = self.choose_next_question_intent()

        if current_intent == "summarize_and_check_for_anything_else":
            applied_update = self._build_wrap_up_update(patient_answer)

            return self._finalize_patient_turn(
                current_intent = current_intent,
                patient_answer = patient_answer,
                applied_update = applied_update,
                parser_name = "wrap_up_handler",
                question_generator = question_generator,
            )

        special_status = self._classify_special_answer_status(patient_answer)

        if special_status is not None:
            applied_update = self._build_special_answer_update(special_status)
            parser_name = "special_answer"

        elif self._should_use_rule_based_first(current_intent):
            applied_update = self.build_update_from_answer(
                current_intent,
                patient_answer,
            )
            parser_name = "rule_based_primary"

        else:
            try:
                applied_update = extractor.extract_update(
                    intent = current_intent,
                    patient_answer = patient_answer,
                    intake_state = self.to_dict(),
                )

                applied_update = normalizer.normalize_update(applied_update)

                applied_update = self._postprocess_llm_update_for_intent(
                    intent = current_intent,
                    patient_answer = patient_answer,
                    applied_update = applied_update,
                )

                applied_update = normalizer.normalize_update(applied_update)

                applied_update.setdefault("set_fields", {})
                applied_update["set_fields"].setdefault(
                    "conversation_meta.last_answer_status",
                    "answered",
                )
                applied_update["set_fields"].setdefault(
                    "conversation_meta.early_exit_reason",
                    None,
                )

                parser_name = "bounded_llm"

            except Exception as e:
                print("EXTRACTOR FALLBACK:", type(e).__name__, str(e))

                applied_update = self.build_update_from_answer(
                    current_intent,
                    patient_answer,
                )

                parser_name = "rule_based_fallback"

        return self._finalize_patient_turn(
            current_intent = current_intent,
            patient_answer = patient_answer,
            applied_update = applied_update,
            parser_name = parser_name,
            question_generator = question_generator,
        )

    def choose_next_target(self):
        return self.determine_next_step()["target"]

    def _should_use_rule_based_first(self, intent):
        target = self._intent_to_target(intent)

        if target is None:
            return False

        from intake_engine.policies.target_specs import TARGET_SPECS

        spec = TARGET_SPECS.get(target, {})
        parse_mode = spec.get("fallback_parse_mode")

        always_rule_based_targets = {
            "sudden_severe_onset",
            "visual_changes",
            "fever_or_neck_stiffness",
            "head_trauma",
            "pregnancy_or_postpartum_context",
            "shortness_of_breath",
            "syncope_or_presyncope",
            "rapid_worsening",
            "onset",
            "duration",
            "severity",
            "timing",
            "course",
            "location",
            "character",
        }

        if target in always_rule_based_targets:
            return True

        if parse_mode in {
            "special_duration",
            "special_severity",
        }:
            return True

        return False