# Policy: Ear Pain
# Add EAR_PAIN_POLICY to COMPLAINT_POLICIES in complaint_policies.py

EAR_PAIN_POLICY = {
    "policy_name": "ear_pain",
    "display_name": "Ear Pain",
    "aliases": [
        "ear pain",
        "ear ache",
        "earache",
        "my ear hurts",
        "ear infection",
        "ear drainage",
        "can't hear",
        "hearing loss",
        "ringing in ears",
        "tinnitus",
        "ear is ringing",
    ],
    "critical_followups": [
        "fever_or_neck_stiffness",
        "neurologic_symptoms",
        "head_trauma",
        "hearing_loss_or_tinnitus",
        "ear_drainage_or_bleeding",
    ],
    "must_characterize": [
        "onset",
        "duration",
        "severity",
        "location",
        "character",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "sick_contacts",
    ],
    "red_flags": [
        "fever_with_ear_pain_suggesting_mastoiditis",
        "neurologic_deficit_with_ear_pain",
        "post_traumatic_ear_pain_with_hearing_loss",
        "ear_drainage_or_bleeding",
        "sudden_sensorineural_hearing_loss",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "location",
            "character",
            "aggravating_factors",
            "relieving_factors",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 6,
    },
}
