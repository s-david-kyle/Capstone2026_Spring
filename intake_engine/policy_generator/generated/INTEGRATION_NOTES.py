# ============================================================
# COMPLAINT_POLICIES additions — paste into complaint_policies.py
# after importing all policy variables above
# ============================================================
#
# Step 1: paste each .py file from final_policies/ into complaint_policies.py
#         above the COMPLAINT_POLICIES dict
#
# Step 2: add these entries to the COMPLAINT_POLICIES dict:
#
#     "nausea_vomiting":        NAUSEA_VOMITING_POLICY,
#     "fever":                  FEVER_POLICY,
#     "syncope":                SYNCOPE_POLICY,
#     "palpitations":           PALPITATIONS_POLICY,
#     "leg_pain_swelling":      LEG_PAIN_SWELLING_POLICY,
#     "urinary_symptoms":       URINARY_SYMPTOMS_POLICY,
#     "cough":                  COUGH_POLICY,
#     "rash":                   RASH_POLICY,
#     "altered_mental_status":  ALTERED_MENTAL_STATUS_POLICY,
#     "seizure":                SEIZURE_POLICY,
#     "eye_pain":               EYE_PAIN_POLICY,
#     "ear_pain":               EAR_PAIN_POLICY,
#
# ============================================================
#
# NEW TARGETS needed in target_specs.py before these policies run:
#
# From seizure policy:
#     seizure_history
#     antiepileptic_compliance
#     recent_sleep_deprivation
#     recent_substance_use
#     tongue_or_lip_biting
#     incontinence_during_event
#     postictal_confusion
#     prodrome_witnessed_loss_of_consciousness
#
# From syncope policy:
#     prodrome_witnessed_loss_of_consciousness  (shared with seizure)
#
# From leg pain policy:
#     calf_tenderness_or_warmth
#     unilateral_leg_swelling
#     unilateral_vs_bilateral
#     recent_immobility_or_travel
#     recent_trauma_or_surgery
#
# From urinary policy:
#     flank_pain
#     hematuria
#     urinary_retention
#     suprapubic_pain
#
# From eye pain policy:
#     floaters_or_flashes
#     vision_loss_pattern
#     recent_eye_trauma
#     eye_pain_type
#     eye_discharge
#     redness
#     headache_with_eye_pain
#     contact_lens_use
#
# From ear pain policy:
#     hearing_loss_or_tinnitus
#     ear_drainage_or_bleeding
#
# From fever policy:
#     rash_or_petechiae
#
# ============================================================
