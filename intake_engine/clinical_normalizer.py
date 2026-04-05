SYMPTOM_NORMALIZATION = {
    "sob": "shortness of breath",
    "short of breath": "shortness of breath",
    "difficulty breathing": "shortness of breath",
    "breathing trouble": "shortness of breath",
    "lightheaded": "lightheadedness",
    "dizzy": "dizziness",
    "chest pressure": "chest pain",
    "chest tightness": "chest pain",
    "nauseated": "nausea",
}

ACUITY_SIGNAL_NORMALIZATION = {
    "short of breath": "active_breathing_difficulty",
    "shortness of breath": "active_breathing_difficulty",
    "trouble breathing": "active_breathing_difficulty",
    "difficulty breathing": "active_breathing_difficulty",
    "hard to breathe": "active_breathing_difficulty",
    "breathing trouble": "active_breathing_difficulty",
    "cannot breathe": "active_breathing_difficulty",
    "can't breathe": "active_breathing_difficulty",
    "breathing is hard": "active_breathing_difficulty",

    "feeling faint": "syncope_or_presyncope",
    "felt faint": "syncope_or_presyncope",
    "feel faint": "syncope_or_presyncope",
    "might pass out": "syncope_or_presyncope",
    "may pass out": "syncope_or_presyncope",
    "going to pass out": "syncope_or_presyncope",
    "pass out": "syncope_or_presyncope",
    "passed out": "syncope_or_presyncope",
    "faint": "syncope_or_presyncope",
    "fainted": "syncope_or_presyncope",
    "lightheaded": "syncope_or_presyncope",
    "lightheadedness": "syncope_or_presyncope",
    "dizzy": "syncope_or_presyncope",
    "dizziness": "syncope_or_presyncope",
    "syncope": "syncope_or_presyncope",
    "presyncope": "syncope_or_presyncope",

    "worsening": "rapid_worsening",
    "getting worse": "rapid_worsening",
    "worse": "rapid_worsening",
    "much worse": "rapid_worsening",
    "rapidly worse": "rapid_worsening",
    "rapid worsening": "rapid_worsening",
    "getting worse quickly": "rapid_worsening",
}


class ClinicalNormalizer:
    def __init__(self, symptom_map = None, acuity_signal_map = None):
        self.symptom_map = symptom_map or SYMPTOM_NORMALIZATION
        self.acuity_signal_map = acuity_signal_map or ACUITY_SIGNAL_NORMALIZATION

    def normalize_term(self, term):
        cleaned = term.strip().lower()
        return self.symptom_map.get(cleaned, cleaned)

    def normalize_acuity_signal(self, signal):
        cleaned = signal.strip().lower()
        return self.acuity_signal_map.get(cleaned, cleaned)

    def _normalize_string_list(self, values, normalizer_fn):
        normalized_values = []

        for value in values:
            if isinstance(value, str):
                normalized_value = normalizer_fn(value)
            else:
                normalized_value = value

            if normalized_value not in normalized_values:
                normalized_values.append(normalized_value)

        return normalized_values

    def normalize_update(self, update):
        normalized = {
            "set_fields": dict(update.get("set_fields", {})),
            "append_fields": {},
            "flags_to_add": list(update.get("flags_to_add", [])),
            "missing_clarifications_to_add": [],
        }

        for field, value in update.get("append_fields", {}).items():
            if field == "conversation_meta.acuity_signal" and isinstance(value, list):
                normalized["append_fields"][field] = self._normalize_string_list(
                    value,
                    self.normalize_acuity_signal,
                )
            elif isinstance(value, list):
                normalized["append_fields"][field] = [
                    self.normalize_term(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                normalized["append_fields"][field] = value

        for field, value in update.get("set_fields", {}).items():
            if isinstance(value, str) and field in {
                "chief_complaint_primary",
                "hpi.location",
                "hpi.character",
            }:
                normalized["set_fields"][field] = self.normalize_term(value)

        normalized["flags_to_add"] = self._normalize_string_list(
            normalized["flags_to_add"],
            self.normalize_acuity_signal,
        )

        return normalized