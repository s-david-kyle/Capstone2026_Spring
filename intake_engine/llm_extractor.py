import json
import re

from intake_engine.policies.target_specs import TARGET_SPECS


SPECIAL_ALLOWED_BY_INTENT = {
    "ask_main_reason_for_visit": {
        "set_fields": {"chief_complaint_primary"},
        "append_fields": set(),
    },
    "ask_immediate_safety_check": {
        "set_fields": set(),
        "append_fields": {
            "hpi.associated_symptoms",
            "pertinent_positives",
            "conversation_meta.acuity_signal",
        },
    },
    "escalate_high_risk_chest_pain": {
        "set_fields": set(),
        "append_fields": {
            "pertinent_positives",
            "conversation_meta.acuity_signal",
        },
    },
    "recommend_immediate_attention": {
        "set_fields": set(),
        "append_fields": set(),
    },
    "summarize_and_check_for_anything_else": {
        "set_fields": set(),
        "append_fields": set(),
    },
}


class BoundedLLMExtractor:
    def __init__(self, llm_callable):
        self.llm_callable = llm_callable

    def _intent_to_target(self, intent):
        for target, spec in TARGET_SPECS.items():
            if spec.get("intent") == intent:
                return target
        return None

    def _build_allowed_from_target_spec(self, target):
        spec = TARGET_SPECS.get(target)

        if spec is None:
            return {
                "set_fields": set(),
                "append_fields": set(),
            }

        state_path = spec.get("state_path")
        default_update_mode = spec.get("default_update_mode", "set")
        extra_set_fields = set(spec.get("extra_set_fields", []))
        extra_append_fields = set(spec.get("extra_append_fields", []))

        allowed_set_fields = set()
        allowed_append_fields = set()

        if state_path:
            if default_update_mode == "append":
                allowed_append_fields.add(state_path)
            else:
                allowed_set_fields.add(state_path)

        allowed_set_fields.update(extra_set_fields)
        allowed_append_fields.update(extra_append_fields)

        return {
            "set_fields": allowed_set_fields,
            "append_fields": allowed_append_fields,
        }

    def _allowed_updates_for_intent(self, intent):
        target = self._intent_to_target(intent)

        if target is not None:
            return self._build_allowed_from_target_spec(target)

        return SPECIAL_ALLOWED_BY_INTENT.get(
            intent,
            {"set_fields": set(), "append_fields": set()},
        )

    def _trim_intake_state_for_extraction(self, intake_state):
        return {
            "chief_complaint_primary": intake_state.get("chief_complaint_primary"),
            "other_concerns": intake_state.get("other_concerns", []),
            "hpi": intake_state.get("hpi", {}),
            "pertinent_positives": intake_state.get("pertinent_positives", []),
            "pertinent_negatives": intake_state.get("pertinent_negatives", []),
            "pmh_psh": intake_state.get("pmh_psh", {}),
            "medications": intake_state.get("medications", []),
            "allergies": intake_state.get("allergies", []),
            "social_factors": intake_state.get("social_factors", []),
            "policy_answers": intake_state.get("policy_answers", {}),
            "missing_clarifications": intake_state.get("missing_clarifications", []),
            "flags": intake_state.get("flags", []),
        }

    def build_prompt(self, intent, patient_answer, intake_state):
        intent_specific_rules = []

        target = self._intent_to_target(intent)
        spec = TARGET_SPECS.get(target) if target is not None else None

        if spec is not None:
            intent_specific_rules.append(spec["extraction_instruction"])
        else:
            if intent == "ask_main_reason_for_visit":
                intent_specific_rules.append(
                    'Extract the main complaint into set_fields under "chief_complaint_primary".'
                )

            if intent == "ask_immediate_safety_check":
                intent_specific_rules.append(
                    'If immediate danger phrases like trouble breathing, feeling faint, or worsening quickly are present, add them to append_fields under "conversation_meta.acuity_signal" and also include relevant free-text positives under "pertinent_positives".'
                )

            if intent == "escalate_high_risk_chest_pain":
                intent_specific_rules.append(
                    'If immediate danger phrases like trouble breathing, feeling faint, or worsening quickly are present, add them to append_fields under "conversation_meta.acuity_signal" and also include relevant free-text positives under "pertinent_positives".'
                )

        if intent in {
            "ask_aggravating_factors",
            "ask_relieving_factors",
            "ask_associated_symptoms",
        }:
            intent_specific_rules.append(
                'If the patient answer clearly fits another existing field better than the literal current target, use that better field instead of forcing it into the wrong field.'
            )
            intent_specific_rules.append(
                'Symptom-like information may belong in append_fields under "hpi.associated_symptoms" and "pertinent_positives".'
            )
            intent_specific_rules.append(
                'Things that make the symptom worse belong in append_fields under "hpi.aggravating_factors".'
            )
            intent_specific_rules.append(
                'Things that make the symptom better belong in append_fields under "hpi.relieving_factors".'
            )
            intent_specific_rules.append(
                'Examples: "nausea", "blurry vision", "sleepy", and "sensitivity to light" are symptom-style answers.'
            )
            intent_specific_rules.append(
                'Examples: "bright light makes it worse" is an aggravating factor.'
            )
            intent_specific_rules.append(
                'Examples: "rest helps a little" is a relieving factor.'
            )

        rules_block = "\n".join(intent_specific_rules)
        compact_state = self._trim_intake_state_for_extraction(intake_state)

        return f"""
    You are a medical intake information extraction assistant.

    Your job is NOT to diagnose.
    Your job is NOT to choose the next question.
    Your only job is to convert the patient's answer into a structured update.

    Current intent:
    {intent}

    Patient answer:
    {patient_answer}

    Compact intake state:
    {json.dumps(compact_state, indent = 2)}

    Return ONLY valid JSON with this exact structure:
    {{
    "set_fields": {{}},
    "append_fields": {{}},
    "flags_to_add": [],
    "missing_clarifications_to_add": []
    }}

    Rules:
    - Prefer to answer the current intent directly.
    - If the patient answer clearly fits another existing field better than the literal current target, use that better field.
    - Only use fields that already exist in the schema.
    - Use dotted paths for nested fields.
    - Do not invent facts not stated by the patient.
    - If the answer does not clearly support a field, leave it out.
    - For list fields, use arrays of strings.
    - If the answer contains immediate danger phrases like trouble breathing, feeling faint, or worsening quickly, add appropriate flags.
    - Leave missing_clarifications_to_add empty. Missing fields are computed by the intake engine.
    - Return JSON only. Do not include explanations or markdown.
    {rules_block}

    Return JSON only.
    """.strip()

    def _strip_json_fences(self, text):
        cleaned = text.strip()

        fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if fenced_match:
            return fenced_match.group(1).strip()

        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return cleaned[first_brace:last_brace + 1].strip()

        return cleaned

    def _merge_dict_list(self, value):
        merged = {}

        for item in value:
            if not isinstance(item, dict):
                continue

            for key, item_value in item.items():
                if key not in merged:
                    merged[key] = item_value
                    continue

                existing = merged[key]

                if isinstance(existing, list) and isinstance(item_value, list):
                    merged[key] = existing + item_value
                elif isinstance(existing, list):
                    merged[key] = existing + [item_value]
                elif isinstance(item_value, list):
                    merged[key] = [existing] + item_value
                else:
                    merged[key] = item_value

        return merged

    def _coerce_mapping_field(self, value):
        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        if value == []:
            return {}

        if isinstance(value, list):
            dict_items = [item for item in value if isinstance(item, dict)]
            if dict_items:
                return self._merge_dict_list(dict_items)
            return {}

        return {}

    def _coerce_list_field(self, value):
        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            return []

        return [value]

    def _coerce_common_container_mistakes(self, parsed):
        repaired = dict(parsed)

        repaired["set_fields"] = self._coerce_mapping_field(repaired.get("set_fields"))
        repaired["append_fields"] = self._coerce_mapping_field(repaired.get("append_fields"))
        repaired["flags_to_add"] = self._coerce_list_field(repaired.get("flags_to_add"))
        repaired["missing_clarifications_to_add"] = self._coerce_list_field(
            repaired.get("missing_clarifications_to_add")
        )

        return repaired

    def _append_unique(self, container, field, values):
        if not values:
            return

        if field not in container:
            container[field] = []

        existing = container[field]
        for value in values:
            if value not in existing:
                existing.append(value)

    def _extract_symptom_terms_from_answer(self, patient_answer):
        text = patient_answer.strip().lower()
        terms = []

        if "nausea" in text or "nauseated" in text:
            terms.append("nausea")

        if "vomit" in text or "vomiting" in text:
            terms.append("vomiting")

        if "light sensitivity" in text or "sensitivity to light" in text:
            terms.append("sensitivity to light")

        if "blurry vision" in text or text == "blurry":
            terms.append("blurry vision")

        if "double vision" in text:
            terms.append("double vision")

        if "sleepy" in text or "unusually sleepy" in text:
            terms.append("sleepy")

        return terms

    def _postprocess_aggravating_factors(self, validated, patient_answer):
        text = patient_answer.strip().lower()

        aggravating_values = list(
            validated["append_fields"].get("hpi.aggravating_factors", [])
        )

        validated["append_fields"].pop("hpi.aggravating_factors", None)

        symptom_terms = []
        relieving_terms = []
        aggravating_terms = []

        if "rest helps" in text or "better with rest" in text or "helps a little" in text:
            relieving_terms.append(patient_answer.strip())

        if "nausea" in text or "nauseated" in text:
            symptom_terms.append("nausea")
            validated["set_fields"]["policy_answers.nausea_or_vomiting"] = True

        if "light sensitivity" in text or "sensitivity to light" in text:
            symptom_terms.append("sensitivity to light")
            validated["set_fields"]["policy_answers.photophobia"] = True

        if "bright light makes it worse" in text or "light makes it worse" in text:
            aggravating_terms.append("bright light")

        for value in aggravating_values:
            lower_value = str(value).strip().lower()

            if (
                "nausea" in lower_value
                or "nauseated" in lower_value
                or "light sensitivity" in lower_value
                or "sensitivity to light" in lower_value
            ):
                symptom_terms.append(lower_value)
                continue

            if "rest helps" in lower_value or "helps a little" in lower_value:
                relieving_terms.append(str(value).strip())
                continue

            if lower_value == "rest":
                continue

            aggravating_terms.append(str(value).strip())

        if symptom_terms:
            self._append_unique(
                validated["append_fields"],
                "hpi.associated_symptoms",
                symptom_terms,
            )
            self._append_unique(
                validated["append_fields"],
                "pertinent_positives",
                symptom_terms,
            )

        if relieving_terms:
            self._append_unique(
                validated["append_fields"],
                "hpi.relieving_factors",
                relieving_terms,
            )

        if aggravating_terms:
            self._append_unique(
                validated["append_fields"],
                "hpi.aggravating_factors",
                aggravating_terms,
            )

    def validate_update_for_intent(self, intent, parsed_update, patient_answer = ""):
        allowed = self._allowed_updates_for_intent(intent)

        validated = {
            "set_fields": {},
            "append_fields": {},
            "flags_to_add": parsed_update.get("flags_to_add", []),
            "missing_clarifications_to_add": [],
        }

        for field, value in parsed_update.get("set_fields", {}).items():
            if field in allowed["set_fields"]:
                validated["set_fields"][field] = value

        for field, value in parsed_update.get("append_fields", {}).items():
            if field in allowed["append_fields"]:
                validated["append_fields"][field] = value

        if intent == "ask_associated_symptoms":
            symptoms = validated["append_fields"].get("hpi.associated_symptoms")
            if symptoms and "pertinent_positives" not in validated["append_fields"]:
                validated["append_fields"]["pertinent_positives"] = list(symptoms)

        if intent == "ask_neurologic_symptoms":
            terms = validated["set_fields"].get("policy_answers.neurologic_symptom_terms")
            if terms and "pertinent_positives" not in validated["append_fields"]:
                validated["append_fields"]["pertinent_positives"] = list(terms)

        if intent == "ask_aggravating_factors":
            self._postprocess_aggravating_factors(validated, patient_answer)

        return validated

    def extract_update(self, intent, patient_answer, intake_state):
        prompt = self.build_prompt(
            intent = intent,
            patient_answer = patient_answer,
            intake_state = intake_state,
        )

        raw_response = self.llm_callable(prompt)
        cleaned_response = self._strip_json_fences(raw_response)

        try:
            parsed = json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM did not return valid JSON: {raw_response}") from exc

        parsed = self._coerce_common_container_mistakes(parsed)

        required_keys = {
            "set_fields",
            "append_fields",
            "flags_to_add",
            "missing_clarifications_to_add",
        }

        if set(parsed.keys()) != required_keys:
            raise ValueError(f"LLM response keys invalid: {parsed.keys()}")

        if not isinstance(parsed["set_fields"], dict):
            raise ValueError("set_fields must be a dictionary")

        if not isinstance(parsed["append_fields"], dict):
            raise ValueError("append_fields must be a dictionary")

        if not isinstance(parsed["flags_to_add"], list):
            raise ValueError("flags_to_add must be a list")

        if not isinstance(parsed["missing_clarifications_to_add"], list):
            raise ValueError("missing_clarifications_to_add must be a list")

        return self.validate_update_for_intent(
            intent = intent,
            parsed_update = parsed,
            patient_answer = patient_answer,
        )