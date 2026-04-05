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

        rules_block = "\n".join(intent_specific_rules)

        return f"""
You are a medical intake information extraction assistant.

Your job is NOT to diagnose.
Your job is NOT to choose the next question.
Your only job is to convert the patient's answer into a structured update.

Current intent:
{intent}

Patient answer:
{patient_answer}

Current intake state:
{json.dumps(intake_state, indent = 2)}

Return ONLY valid JSON with this exact structure:
{{
  "set_fields": {{}},
  "append_fields": {{}},
  "flags_to_add": [],
  "missing_clarifications_to_add": []
}}

Rules:
- Only update fields that are relevant to the current intent.
- Use dotted paths for nested fields.
- Do not invent facts not stated by the patient.
- If the answer does not clearly fill a field, leave it out.
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

    def _coerce_common_container_mistakes(self, parsed):
        repaired = dict(parsed)

        if repaired.get("set_fields") == []:
            repaired["set_fields"] = {}

        if repaired.get("append_fields") == []:
            repaired["append_fields"] = {}

        if repaired.get("flags_to_add") == {}:
            repaired["flags_to_add"] = []

        if repaired.get("missing_clarifications_to_add") == {}:
            repaired["missing_clarifications_to_add"] = []

        return repaired

    def validate_update_for_intent(self, intent, parsed_update):
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
        )