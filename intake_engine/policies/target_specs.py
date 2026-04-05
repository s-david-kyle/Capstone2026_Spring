TARGET_SPECS = {
    "sudden_severe_onset": {
        "intent": "ask_sudden_severe_onset",
        "state_path": "policy_answers.sudden_severe_onset",
        "fallback_parse_mode": "yes_no",
        "question_mode": "yes_no_template",
        "question_aux": "Did",
        "question_subject": "the headache",
        "question_predicate": "start suddenly and become very severe right away",
        "question_instruction": (
            "Ask whether the headache started suddenly and became severe right away."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.sudden_severe_onset".'
        ),
    },
    "neurologic_symptoms": {
        "intent": "ask_neurologic_symptoms",
        "state_path": "policy_answers.neurologic_symptoms",
        "fallback_parse_mode": "special_neurologic_symptoms",
        "question_mode": "deterministic",
        "question_text": "Have you had weakness, numbness, trouble speaking, confusion, or vision changes?",
        "extra_set_fields": ["policy_answers.neurologic_symptom_terms"],
        "extra_append_fields": ["pertinent_positives"],
        "question_instruction": (
            "Ask about neurologic warning symptoms such as weakness, numbness, trouble speaking, confusion, or vision problems."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.neurologic_symptoms". '
            'If specific neurologic symptom terms are mentioned, also extract them into set_fields under "policy_answers.neurologic_symptom_terms". '
            'If specific neurologic symptom terms are extracted, also copy them into append_fields under "pertinent_positives".'
        ),
    },
    "visual_changes": {
        "intent": "ask_visual_changes",
        "state_path": "policy_answers.visual_changes",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you had blurry vision, double vision, or other vision changes?",
        "question_instruction": (
            "Ask whether there have been blurry vision, double vision, or other vision changes."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.visual_changes".'
        ),
    },
    "confusion_or_ams": {
        "intent": "ask_confusion_or_ams",
        "state_path": "policy_answers.confusion_or_ams",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you felt confused, unusually sleepy, or not like yourself?",
        "question_instruction": (
            "Ask whether the patient has felt confused, unusually sleepy, disoriented, or not like themselves."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.confusion_or_ams".'
        ),
    },
    "fever_or_neck_stiffness": {
        "intent": "ask_fever_or_neck_stiffness",
        "state_path": "policy_answers.fever_or_neck_stiffness",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you had a fever or a stiff neck with the headache?",
        "question_instruction": (
            "Ask whether the patient has fever or a stiff neck with the headache."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.fever_or_neck_stiffness".'
        ),
    },
    "head_trauma": {
        "intent": "ask_head_trauma",
        "state_path": "policy_answers.head_trauma",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you hit your head recently or had any head injury?",
        "question_instruction": (
            "Ask whether the patient has hit their head recently or had any head injury."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.head_trauma".'
        ),
    },
    "pregnancy_or_postpartum_context": {
        "intent": "ask_pregnancy_or_postpartum_context",
        "state_path": "policy_answers.pregnancy_or_postpartum_context",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Are you pregnant or have you recently given birth?",
        "question_instruction": (
            "Ask whether the patient is pregnant or has recently given birth."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.pregnancy_or_postpartum_context".'
        ),
    },
    "onset": {
        "intent": "ask_onset",
        "state_path": "hpi.onset",
        "fallback_parse_mode": "text",
        "question_instruction": (
            "Ask when the main complaint started."
        ),
        "extraction_instruction": (
            'Extract the onset description into set_fields under "hpi.onset".'
        ),
    },
    "location": {
        "intent": "ask_location",
        "state_path": "hpi.location",
        "fallback_parse_mode": "text",
        "question_instruction": (
            "Ask where the symptom is located."
        ),
        "extraction_instruction": (
            'Extract the location description into set_fields under "hpi.location".'
        ),
    },
    "duration": {
        "intent": "ask_duration",
        "state_path": "hpi.duration",
        "fallback_parse_mode": "special_duration",
        "question_instruction": (
            "Ask how long the symptom has been going on."
        ),
        "extraction_instruction": (
            'Extract the duration into set_fields under "hpi.duration".'
        ),
    },
    "severity": {
        "intent": "ask_severity",
        "state_path": "hpi.severity",
        "fallback_parse_mode": "special_severity",
        "question_instruction": (
            "Ask how severe the symptom is right now."
        ),
        "extraction_instruction": (
            'Extract severity into set_fields under "hpi.severity". '
            'If a 0 to 10 rating is given, normalize to forms like "7/10".'
        ),
    },
    "timing": {
        "intent": "ask_timing",
        "state_path": "hpi.timing",
        "fallback_parse_mode": "text",
        "question_instruction": (
            "Ask whether the symptom is constant or comes and goes."
        ),
        "extraction_instruction": (
            'Extract the timing description into set_fields under "hpi.timing".'
        ),
    },
    "course": {
        "intent": "ask_course",
        "state_path": "hpi.course",
        "fallback_parse_mode": "text",
        "question_instruction": (
            "Ask how the symptom has changed over time."
        ),
        "extraction_instruction": (
            'Extract the course description into set_fields under "hpi.course".'
        ),
    },
    "character": {
        "intent": "ask_character",
        "state_path": "hpi.character",
        "fallback_parse_mode": "text",
        "question_instruction": (
            "Ask how the symptom feels, for example sharp, dull, pressure, or throbbing."
        ),
        "extraction_instruction": (
            'Extract the symptom character into set_fields under "hpi.character".'
        ),
    },
    "aggravating_factors": {
        "intent": "ask_aggravating_factors",
        "state_path": "hpi.aggravating_factors",
        "default_update_mode": "append",
        "fallback_parse_mode": "list_append",
        "question_instruction": (
            "Ask what makes the symptom worse."
        ),
        "extraction_instruction": (
            'Extract aggravating factors into append_fields under "hpi.aggravating_factors".'
        ),
    },
    "relieving_factors": {
        "intent": "ask_relieving_factors",
        "state_path": "hpi.relieving_factors",
        "default_update_mode": "append",
        "fallback_parse_mode": "list_append",
        "question_instruction": (
            "Ask what makes the symptom better."
        ),
        "extraction_instruction": (
            'Extract relieving factors into append_fields under "hpi.relieving_factors".'
        ),
    },
    "associated_symptoms": {
        "intent": "ask_associated_symptoms",
        "state_path": "hpi.associated_symptoms",
        "default_update_mode": "append",
        "fallback_parse_mode": "list_append",
        "extra_append_fields": ["pertinent_positives"],
        "question_instruction": (
            "Ask what other symptoms are happening along with the main complaint."
        ),
        "extraction_instruction": (
            'Extract symptom phrases into append_fields under "hpi.associated_symptoms". '
            'Also copy the same symptom phrases into append_fields under "pertinent_positives".'
        ),
    },
    "medications": {
        "intent": "ask_medications",
        "state_path": "medications",
        "default_update_mode": "append",
        "fallback_parse_mode": "list_append",
        "question_instruction": (
            "Ask what medications the patient is currently taking."
        ),
        "extraction_instruction": (
            'Extract medication names into append_fields under "medications".'
        ),
    },
    "allergies": {
        "intent": "ask_allergies",
        "state_path": "allergies",
        "default_update_mode": "append",
        "fallback_parse_mode": "list_append",
        "question_instruction": (
            "Ask whether the patient has any medication allergies or other allergies."
        ),
        "extraction_instruction": (
            'Extract allergy terms into append_fields under "allergies".'
        ),
    },
    "photophobia": {
        "intent": "ask_photophobia",
        "state_path": "policy_answers.photophobia",
        "fallback_parse_mode": "yes_no",
        "question_mode": "yes_no_template",
        "question_aux": "Does",
        "question_subject": "light",
        "question_predicate": "make the headache worse",
        "question_instruction": (
            "Ask whether light makes the headache worse or whether the patient is sensitive to light."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.photophobia".'
        ),
    },
    "phonophobia": {
        "intent": "ask_phonophobia",
        "state_path": "policy_answers.phonophobia",
        "fallback_parse_mode": "yes_no",
        "question_mode": "yes_no_template",
        "question_aux": "Does",
        "question_subject": "sound",
        "question_predicate": "make the headache worse",
        "question_instruction": (
            "Ask whether sound makes the headache worse or whether the patient is sensitive to noise."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.phonophobia".'
        ),
    },
    "nausea_or_vomiting": {
        "intent": "ask_nausea_or_vomiting",
        "state_path": "policy_answers.nausea_or_vomiting",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you had nausea or vomiting with the headache?",
        "question_instruction": (
            "Ask whether there has been nausea or vomiting with the headache."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.nausea_or_vomiting".'
        ),
    },
    "aura_features": {
        "intent": "ask_aura_features",
        "state_path": "policy_answers.aura_features",
        "default_update_mode": "append",
        "fallback_parse_mode": "list_append",
        "question_instruction": (
            "Ask whether there were warning symptoms before the headache, such as visual changes, tingling, or trouble speaking."
        ),
        "extraction_instruction": (
            'Extract aura symptom terms into append_fields under "policy_answers.aura_features".'
        ),
    },
    "exertional_trigger": {
        "intent": "ask_exertional_trigger",
        "state_path": "policy_answers.exertional_trigger",
        "fallback_parse_mode": "yes_no",
        "question_mode": "yes_no_template",
        "question_aux": "Did",
        "question_subject": "exercise, coughing, straining, or exertion",
        "question_predicate": "trigger the headache",
        "question_instruction": (
            "Ask whether exercise, coughing, straining, or exertion triggered the headache."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.exertional_trigger".'
        ),
    },
    "positional_component": {
        "intent": "ask_positional_component",
        "state_path": "policy_answers.positional_component",
        "fallback_parse_mode": "yes_no",
        "question_mode": "yes_no_template",
        "question_aux": "Does",
        "question_subject": "the headache",
        "question_predicate": "change when you lie down, sit up, or stand",
        "question_instruction": (
            "Ask whether the headache changes with lying down, sitting up, or standing."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.positional_component".'
        ),
    },
    "new_or_progressive_pattern": {
        "intent": "ask_new_or_progressive_pattern",
        "state_path": "policy_answers.new_or_progressive_pattern",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Is this a new kind of headache or has it been getting worse over time?",
        "question_instruction": (
            "Ask whether this is a new kind of headache or whether it has been getting worse over time."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.new_or_progressive_pattern".'
        ),
    },
    "medication_overuse_context": {
        "intent": "ask_medication_overuse_context",
        "state_path": "policy_answers.medication_overuse_context",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you been using pain medicine frequently for this headache?",
        "question_instruction": (
            "Ask whether the patient has been using pain medicine frequently for this headache."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.medication_overuse_context".'
        ),
    },
    "shortness_of_breath": {
        "intent": "ask_shortness_of_breath",
        "state_path": "policy_answers.shortness_of_breath",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Do you have shortness of breath or trouble breathing with the chest pain?",
        "question_instruction": (
            "Ask whether there is shortness of breath or trouble breathing with the chest pain."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.shortness_of_breath".'
        ),
    },
    "syncope_or_presyncope": {
        "intent": "ask_syncope_or_presyncope",
        "state_path": "policy_answers.syncope_or_presyncope",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you fainted or felt like you might faint?",
        "question_instruction": (
            "Ask whether the patient fainted or felt like they might faint."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.syncope_or_presyncope".'
        ),
    },
    "rapid_worsening": {
        "intent": "ask_rapid_worsening",
        "state_path": "policy_answers.rapid_worsening",
        "fallback_parse_mode": "yes_no",
        "question_mode": "yes_no_template",
        "question_aux": "Is",
        "question_subject": "the chest pain",
        "question_predicate": "getting worse quickly right now",
        "question_instruction": (
            "Ask whether the chest pain is getting worse quickly right now."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.rapid_worsening".'
        ),
    },
    "radiation": {
        "intent": "ask_radiation",
        "state_path": "policy_answers.radiation",
        "default_update_mode": "append",
        "fallback_parse_mode": "list_append",
        "question_instruction": (
            "Ask whether the chest pain moves anywhere else, such as the arm, jaw, neck, shoulder, or back."
        ),
        "extraction_instruction": (
            'Extract radiation locations into append_fields under "policy_answers.radiation".'
        ),
    },
    "nausea": {
        "intent": "ask_nausea",
        "state_path": "policy_answers.nausea",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you had nausea with the chest pain?",
        "question_instruction": (
            "Ask whether there has been nausea with the chest pain."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.nausea".'
        ),
    },
    "diaphoresis": {
        "intent": "ask_diaphoresis",
        "state_path": "policy_answers.diaphoresis",
        "fallback_parse_mode": "yes_no",
        "question_mode": "deterministic",
        "question_text": "Have you had sweating or clamminess with the chest pain?",
        "question_instruction": (
            "Ask whether there has been sweating or clamminess with the chest pain."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.diaphoresis".'
        ),
    },
    "exertional_component": {
        "intent": "ask_exertional_component",
        "state_path": "policy_answers.exertional_component",
        "fallback_parse_mode": "yes_no",
        "question_mode": "yes_no_template",
        "question_aux": "Does",
        "question_subject": "the chest pain",
        "question_predicate": "come on or get worse with physical activity",
        "question_instruction": (
            "Ask whether the chest pain comes on or gets worse with physical activity."
        ),
        "extraction_instruction": (
            'Extract a boolean into set_fields under "policy_answers.exertional_component".'
        ),
    },
}