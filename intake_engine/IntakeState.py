from copy import deepcopy

from intake_engine.state.routing import determine_next_step
from intake_engine.state.rule_based_parser import (
    answer_is_explicit_neurologic_negation,
    build_update_from_answer,
    extract_escalation_signals,
    extract_neurologic_symptom_terms,
    extract_yes_no_unknown,
    intent_to_target,
)
from intake_engine.state.templates import FACET_ORDER, INTAKE_TEMPLATE, make_empty_intake


class IntakeState:
    facet_order = FACET_ORDER
    intake_template = INTAKE_TEMPLATE

    def __init__(self, data = None):
        self.data = deepcopy(data) if data is not None else make_empty_intake()

    def reset(self):
        self.data = make_empty_intake()
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

        associated_symptoms_status = (
            self.data["conversation_meta"]["question_status"].get("associated_symptoms")
        )
        associated_symptoms_asked = associated_symptoms_status in {
            "asked_answered", "asked_answered_empty", "asked_declined", "asked_unknown"
        }
        if not hpi["associated_symptoms"] and not associated_symptoms_asked:
            missing.append("associated symptoms")

        return missing

    def refresh_missing_clarifications(self):
        self.data["missing_clarifications"] = self.collect_missing_clarifications()
        return self

    def detect_basic_flags(self):
        chief_complaint_raw = self.data["chief_complaint_primary"] or ""

        if isinstance(chief_complaint_raw, list):
            chief_complaint = " ".join(str(x) for x in chief_complaint_raw).lower()
        else:
            chief_complaint = str(chief_complaint_raw).lower()
            
        severity = (self.data["hpi"]["severity"] or "").lower()
        associated_symptoms = [
            symptom.lower() for symptom in self.data["hpi"]["associated_symptoms"]
        ]
        policy_answers = self.data["policy_answers"]
        flags = []

        if "chest pain" in chief_complaint:
            # Check associated_symptoms list OR policy_answers.shortness_of_breath
            sob_in_symptoms = "shortness of breath" in associated_symptoms
            sob_in_policy = policy_answers.get("shortness_of_breath") is True
            if sob_in_symptoms or sob_in_policy:
                flags.append("chest_pain_with_shortness_of_breath")

            if "sweating" in associated_symptoms or policy_answers.get("diaphoresis") is True:
                flags.append("chest_pain_with_diaphoresis")

        if severity in {"8/10", "9/10", "10/10"}:
            if not self.data["conversation_meta"].get("safety_check_done", False):
                flags.append("severe_symptom_intensity")

        return flags

    def refresh_flags(self):
        detected_flags = self.detect_basic_flags()

        # severe_symptom_intensity is transient — remove it before recomputing
        # so it only persists while severity is still 8-10/10, not forever
        persistent_flags = [
            f for f in self.data["flags"]
            if f != "severe_symptom_intensity"
        ]
        self.data["flags"] = persistent_flags

        self._append_unique(self.data["flags"], detected_flags)
        return self

    def determine_next_step(self):
        return determine_next_step(self.data, self.to_dict)

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
            return "Could you tell me what's been bothering you today?"

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

    def _classify_special_answer_status(self, text):
        answer = text.strip().lower()

        stop_phrases = [
            "i want to stop",
            "i want to end this",
            "i'm done",
            "im done",
            "no more questions",
            "end this",
            "stop this",
        ]

        # Match bare single words only as exact answers
        stop_words = {"stop", "quit", "end"}

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

        if answer in stop_words or any(phrase in answer for phrase in stop_phrases):
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
        yes_no_value = extract_yes_no_unknown(patient_answer)

        target = self._intent_to_target(intent)

        if target is not None:
            from intake_engine.policies.target_specs import TARGET_SPECS

            spec = TARGET_SPECS.get(target, {})
            state_path = spec.get("state_path")
            fallback_parse_mode = spec.get("fallback_parse_mode")
            default_update_mode = spec.get("default_update_mode", "set")

            if (
                yes_no_value is not None
                and fallback_parse_mode == "yes_no"
                and state_path is not None
            ):
                applied_update.setdefault("set_fields", {})
                applied_update.setdefault("append_fields", {})

                if default_update_mode == "append":
                    applied_update["append_fields"][state_path] = [yes_no_value]
                else:
                    applied_update["set_fields"][state_path] = yes_no_value

        if intent == "ask_neurologic_symptoms":
            if yes_no_value is False:
                applied_update.setdefault("set_fields", {})
                applied_update["set_fields"]["policy_answers.neurologic_symptoms"] = False
                applied_update["set_fields"]["policy_answers.neurologic_symptom_terms"] = []

                applied_update.setdefault("append_fields", {})
                if "pertinent_positives" in applied_update["append_fields"]:
                    applied_update["append_fields"]["pertinent_positives"] = []

                return applied_update

            if answer_is_explicit_neurologic_negation(patient_answer):
                applied_update.setdefault("set_fields", {})
                applied_update["set_fields"]["policy_answers.neurologic_symptoms"] = False
                applied_update["set_fields"]["policy_answers.neurologic_symptom_terms"] = []

                applied_update.setdefault("append_fields", {})
                if "pertinent_positives" in applied_update["append_fields"]:
                    applied_update["append_fields"]["pertinent_positives"] = []

        return applied_update

    def _intent_to_target(self, intent):
        return intent_to_target(intent)

    def _answer_status_to_question_status(self, answer_status):
        mapping = {
            "answered": "asked_answered",
            "unknown": "asked_unknown",
            "declined": "asked_declined",
            "answered_empty": "asked_answered_empty",
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

    def build_update_from_answer(self, intent, patient_answer):
        return build_update_from_answer(intent, patient_answer)

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

        # After safety check is answered, clear the transient flag so the
        # override rule does not loop indefinitely
        if current_intent == "ask_immediate_safety_check":
            self.data["flags"] = [
                f for f in self.data["flags"]
                if f != "severe_symptom_intensity"
            ]
            self.data["conversation_meta"]["safety_check_done"] = True

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

        if self._is_deterministic_intent(current_intent):
            applied_update = self.build_update_from_answer(
                current_intent,
                patient_answer,
            )

            return self._finalize_patient_turn(
                current_intent = current_intent,
                patient_answer = patient_answer,
                applied_update = applied_update,
                parser_name = "rule_based_deterministic",
                question_generator = question_generator,
            )

        special_status = self._classify_special_answer_status(patient_answer)
        target = self._intent_to_target(current_intent)
        answer_text = patient_answer.strip().lower()

        from intake_engine.policies.target_specs import TARGET_SPECS
        spec = TARGET_SPECS.get(target, {}) if target is not None else {}

        is_list_target = (
            spec.get("default_update_mode") == "append"
            or spec.get("fallback_parse_mode") == "list_append"
        )

        if special_status is not None:
            applied_update = self._build_special_answer_update(special_status)
        elif is_list_target and answer_text in {"no", "nope", "nothing", "none", "next"}:
            applied_update = {
                "set_fields": {
                    "conversation_meta.last_answer_status": "answered_empty",
                    "conversation_meta.early_exit_reason": None,
                },
                "append_fields": {},
                "flags_to_add": [],
                "missing_clarifications_to_add": [],
            }
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

        if self._is_deterministic_intent(current_intent):
            applied_update = self.build_update_from_answer(
                current_intent,
                patient_answer,
            )

            return self._finalize_patient_turn(
                current_intent = current_intent,
                patient_answer = patient_answer,
                applied_update = applied_update,
                parser_name = "rule_based_deterministic",
                question_generator = question_generator,
            )

        special_status = self._classify_special_answer_status(patient_answer)
        target = self._intent_to_target(current_intent)
        answer_text = patient_answer.strip().lower()

        from intake_engine.policies.target_specs import TARGET_SPECS
        spec = TARGET_SPECS.get(target, {}) if target is not None else {}

        is_list_target = (
            spec.get("default_update_mode") == "append"
            or spec.get("fallback_parse_mode") == "list_append"
        )

        if special_status is not None:
            applied_update = self._build_special_answer_update(special_status)
            parser_name = "special_answer"

        elif is_list_target and answer_text in {"no", "nope", "nothing", "none", "next"}:
            applied_update = {
                "set_fields": {
                    "conversation_meta.last_answer_status": "answered_empty",
                    "conversation_meta.early_exit_reason": None,
                },
                "append_fields": {},
                "flags_to_add": [],
                "missing_clarifications_to_add": [],
            }
            parser_name = "empty_list_answer"

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
            # yes/no safety targets
            "sudden_severe_onset",
            "visual_changes",
            "fever_or_neck_stiffness",
            "head_trauma",
            "pregnancy_or_postpartum_context",
            "shortness_of_breath",
            "syncope_or_presyncope",
            "rapid_worsening",
            # HPI characterization
            "onset",
            "duration",
            "severity",
            "timing",
            "course",
            "location",
            "character",
            # list fields — rule-based is reliable enough and avoids LLM JSON issues
            "aggravating_factors",
            "relieving_factors",
            "associated_symptoms",
            "medications",
            "allergies",
            "radiation",
            "aura_features",
            "urinary_symptoms",
            # Tier 1 new yes/no targets
            "prodrome_witnessed_loss_of_consciousness",
            "hemoptysis",
            "rash_or_petechiae",
            "calf_tenderness_or_warmth",
            "unilateral_leg_swelling",
            "recent_immobility_or_travel",
            "recent_trauma_or_surgery",
            "flank_pain",
            "hematuria",
            "urinary_retention",
            "suprapubic_pain",
            "floaters_or_flashes",
            "recent_eye_trauma",
            "eye_discharge",
            "redness",
            "headache_with_eye_pain",
            "contact_lens_use",
            "hearing_loss_or_tinnitus",
            "ear_drainage_or_bleeding",
            "seizure_history",
            "antiepileptic_compliance",
            "recent_sleep_deprivation",
            "recent_substance_use",
            "tongue_or_lip_biting",
            "incontinence_during_event",
            "postictal_confusion",
        }

        if target in always_rule_based_targets:
            return True

        if parse_mode in {
            "special_duration",
            "special_severity",
        }:
            return True

        return False