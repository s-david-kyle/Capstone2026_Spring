# Current Questions by Symptom

Generated from the cleaned v1.1.0 package after episode-duration skip updates.

## Abdominal Pain (`abdominal_pain`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did it start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is the pain constant, or does it come and go in episodes? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `episode_duration` | `EVENT-004` | When it comes, how long does each episode last? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PATTERN_NOT_EPISODIC` |
| 4 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `location` | `PAIN-014` | Where exactly is the pain? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `severity` | `PAIN-015` | How severe is it from 0 to 10? | `SCALE_0_10` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `character` | `PAIN-016` | What does the abdominal pain feel like, for example throbbing, sharp, dull, burning, cramping, pressure-like, stabbing, or aching? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `radiation` | `PAIN-017` | Does the pain travel anywhere else, such as the back, groin, chest, shoulder, or leg? If yes, where? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `sudden_onset` | `HEADQ-001` | Did the pain start suddenly, meaning it came on abruptly rather than gradually? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `tearing_pain` | `PAIN-002` | Does the pain feel tearing or ripping, especially toward the back? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|SEVERITY_BELOW_7` |
| 14 | high_priority_followup | `abdominal_pulsation` | `ABD-001` | Does it feel like there is a pulsing or throbbing feeling in your abdomen? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `vomiting` | `GI-002` | Have you been vomiting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `vomiting_frequency` | `GIQ-001` | How often are you vomiting? | `SHORT_TEXT` | `detail` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 17 | high_priority_followup | `dehydration` | `CON-011A` | Have you been very dry, dizzy when standing, or unable to keep fluids down? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `low_urine_output` | `CON-011B` | Have you been passing much less urine than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:low_urine_output` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `blood_in_stool` | `GI-004B` | Have you noticed blood in the stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:blood_in_stool` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `melena` | `GIQ-021` | Has the stool been black or tarry? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:melena` | `FIELD_ALREADY_CAPTURED` |
| 21 | high_priority_followup | `bowel_obstruction_symptom` | `GI-023` | Are you unable to pass stool or gas? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:bowel_obstruction` | `FIELD_ALREADY_CAPTURED` |
| 22 | high_priority_followup | `fainting` | `NEU-002` | Have you fainted or passed out? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 23 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 24 | high_priority_followup | `pregnancy_context` | `GYNHX-001` | Could you be pregnant now, or are you recently postpartum? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 25 | high_priority_followup | `abdominal_distension` | `GI-005` | Has your abdomen become swollen or more bloated than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 26 | high_priority_followup | `recent_trauma` | `CTX-004` | Did this start after an injury, fall, blow, or accident? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `diarrhea` | `GI-003` | Have you had loose stool or diarrhea? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:diarrhea` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `stool_frequency` | `GIQ-008` | How often are you passing stool? | `COUNT_OR_SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 29 | targeted_followup | `stool_content` | `GIQ-014` | What is the stool like? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 30 | targeted_followup | `constipation` | `GI-011` | Have you been constipated or had difficulty passing stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:constipation` | `FIELD_ALREADY_CAPTURED` |
| 31 | targeted_followup | `stool_consistency` | `GIQ-015` | What is the stool like when it comes? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 32 | targeted_followup | `difficulty_passing_stool` | `GIQ-017` | Are you having difficulty passing stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `detail` | `ros:constipation` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 33 | targeted_followup | `loss_of_appetite` | `GI-006` | Has your appetite gone down? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:loss_of_appetite` | `FIELD_ALREADY_CAPTURED` |
| 34 | targeted_followup | `food_exposure` | `CTX-002` | Did this seem to start after any suspicious food or meal? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:food_exposure` | `FIELD_ALREADY_CAPTURED` |
| 35 | targeted_followup | `dysuria` | `GU-001` | Do you have pain or burning when you pass urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:dysuria` | `FIELD_ALREADY_CAPTURED` |
| 36 | targeted_followup | `urinary_frequency` | `GU-002` | Are you passing urine more often than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_frequency` | `FIELD_ALREADY_CAPTURED` |
| 37 | targeted_followup | `urinary_urgency` | `GU-003` | Do you get a sudden strong urge to pass urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_urgency` | `FIELD_ALREADY_CAPTURED` |
| 38 | targeted_followup | `hematuria` | `GU-006` | Have you noticed blood in your urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:hematuria` | `FIELD_ALREADY_CAPTURED` |
| 39 | targeted_followup | `flank_pain` | `GU-007` | Do you have pain in your side or back near the kidney? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:flank_pain` | `FIELD_ALREADY_CAPTURED` |
| 40 | targeted_followup | `prior_stones` | `PMH-023` | Have you had kidney stones before? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 41 | targeted_followup | `lmp` | `GYNHX-002` | When was the first day of your last menstrual period? | `TEMPORAL_OR_SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 42 | targeted_followup | `vaginal_bleeding` | `GYN-001` | Have you had any bleeding from the vagina? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vaginal_bleeding` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 43 | targeted_followup | `menstrual_flow_pads` | `GYNQ-010` | How many pads or tampons do you use on your heaviest day? | `NUMERIC_OR_SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 44 | targeted_followup | `vaginal_discharge` | `GYN-002` | Have you noticed any vaginal discharge? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vaginal_discharge` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 45 | targeted_followup | `discharge_color` | `GYNQ-001` | What color is the discharge? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 46 | targeted_followup | `discharge_consistency` | `GYNQ-002` | What is the discharge like: thin, thick, clumpy, or something else? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 47 | targeted_followup | `discharge_odor` | `GYNQ-003` | Does it have any odor? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 48 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Back pain (`back_pain`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the back pain start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is the pain constant, or does it come and go in episodes? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `location` | `PAIN-014` | Where is the back pain located? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `pain_specific_location` | `PAIN-014B` | Can you point to the exact spot in your back? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `character` | `PAIN-016` | What does the back pain feel like, for example throbbing, sharp, dull, burning, cramping, pressure-like, stabbing, or aching? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `severity` | `PAIN-015` | On a scale of 0 to 10, how severe is it? | `SCALE_0_10` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `radiation` | `PAIN-017` | Does the pain travel anywhere else, such as the back, groin, chest, shoulder, or leg? If yes, where? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `recent_trauma` | `CTX-004` | Did this start after any recent trauma or injury? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `leg_weakness` | `NEURO-007` | Any weakness in one or both legs? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `numbness` | `NEURO-004` | Any numbness in the legs or elsewhere? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:numbness` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `tingling` | `NEURO-005` | Any tingling or pins-and-needles in the legs? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:tingling` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `saddle_anesthesia` | `NEURO-018` | Any numbness around the groin or saddle area? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `bowel_dysfunction` | `SPINE-001A` | Have you had new trouble controlling your bowels or new loss of stool control? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:bowel_dysfunction` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `bladder_dysfunction` | `SPINE-001B` | Have you had new trouble passing urine or controlling your bladder? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:bladder_dysfunction` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `fever` | `CON-001` | Any fever with the back pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `history_of_cancer` | `PMH-014` | Any history of cancer? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 21 | high_priority_followup | `fracture_risk_history` | `PMH-021` | Do you have osteoporosis or long-term steroid use? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:back_pain` | `FIELD_ALREADY_CAPTURED` |
| 22 | high_priority_followup | `weight_loss` | `CON-007` | Any unexplained weight loss? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weight_loss` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `leg_pain` | `MSK-011` | Any pain going into the leg? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `stiffness` | `MSK-010` | Any stiffness in the back? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:stiffness` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `pain_worse_with_movement` | `MSKQ-010` | Is the pain worse with movement? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `recent_heavy_lifting` | `CTX-009` | Did this start after any recent heavy lifting or strain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 27 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Chest Pain (`chest_pain`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the chest pain start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it there all the time, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 3 | core_characterization | `episode_duration` | `EVENT-004` | When it happens, how long does each episode last? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PATTERN_NOT_EPISODIC` |
| 4 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `` |
| 5 | core_characterization | `severity` | `PAIN-015` | How bad is it from 0 to 10? | `SCALE_0_10` | `qualifier` | `` | `` |
| 6 | core_characterization | `location` | `PAIN-014` | Where exactly is the chest pain? | `SHORT_TEXT` | `qualifier` | `ros:location` | `` |
| 7 | core_characterization | `character` | `PAIN-016` | What does the chest pain feel like, for example throbbing, sharp, dull, burning, cramping, pressure-like, stabbing, or aching? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 8 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 9 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 10 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 11 | high_priority_followup | `pain_at_rest` | `CPQ-001` | Does the pain happen even when you are resting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `exertional_trigger` | `EVENT-012` | Does it come on or get worse with physical activity? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `upper_body_radiation` | `CPQ-002` | Does the pain spread to your arm, shoulder, neck, or jaw? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chest_pain` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `diaphoresis` | `CON-002` | Have you broken out into a sweat with it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `nausea` | `GI-007` | Have you felt nauseated? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:nausea` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Have you had any difficulty in breathing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `tearing_pain` | `PAIN-002` | Does the pain feel tearing or ripping? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|SEVERITY_BELOW_7` |
| 18 | high_priority_followup | `radiation` | `PAIN-017` | Does the pain travel anywhere else, such as the back, groin, chest, shoulder, or leg? If yes, where? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `pleuritic_pain` | `RESP-008` | Is it worse when you take a deep breath or cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:pleuritic_pain` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `hemoptysis` | `RESP-004` | Have you coughed up blood? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:hemoptysis` | `FIELD_ALREADY_CAPTURED` |
| 21 | high_priority_followup | `leg_swelling` | `CV-001` | Have you had swelling in one or both legs? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:leg_swelling` | `FIELD_ALREADY_CAPTURED` |
| 22 | high_priority_followup | `palpitations` | `CV-003` | Have you felt your heart racing or beating irregularly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:palpitations` | `FIELD_ALREADY_CAPTURED` |
| 23 | high_priority_followup | `fainting` | `NEU-002` | Have you fainted or passed out? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 24 | high_priority_followup | `dizziness` | `NEU-001` | Have you felt dizzy or lightheaded? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:dizziness` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `cough` | `RESP-005` | Do you have a cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:cough` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `wheeze` | `RESPQ-004` | Do you hear a whistling sound when you breathe? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:wheeze` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `recent_immobility` | `SOC-014` | Have you been stuck in bed, on a long trip, or not moving around much recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_immobility` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `recent_travel` | `SOC-007` | Have you traveled anywhere recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_travel` | `FIELD_ALREADY_CAPTURED` |
| 30 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Constipation (`constipation`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the constipation start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it constant, or does it come and go in episodes? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `last_bowel_movement` | `GI-020` | When was your last bowel movement? If you remember, about how long ago was it? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `ros:constipation` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `stool_hardness` | `GI-021` | Are the stools hard, dry, pellet-like, or difficult to pass? | `SHORT_TEXT` | `qualifier` | `ros:constipation` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `straining` | `GI-022` | Have you been straining to pass stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:constipation` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `change_in_bowel_habit` | `GI-024` | Has there been a change from your usual bowel habit? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:change_in_bowel_habit` | `FIELD_ALREADY_CAPTURED` |
| 8 | high_priority_followup | `bowel_obstruction_symptom` | `GI-023` | Are you unable to pass stool or gas? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:bowel_obstruction` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `abdominal_distension` | `GI-005` | Any abdominal swelling or distension? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `vomiting` | `GI-002` | Have you been vomiting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `vomiting_frequency` | `GIQ-001` | How often are you vomiting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `blood_in_stool` | `GI-004B` | Any blood in the stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:blood_in_stool` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `melena` | `GIQ-021` | Any black tarry stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:melena` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `fever` | `CON-001` | Any fever with the constipation? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `weight_loss` | `CON-007` | Any unexplained weight loss? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weight_loss` | `FIELD_ALREADY_CAPTURED` |
| 16 | targeted_followup | `abdominal_pain` | `GI-008` | Any abdominal pain with the constipation? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `bloating` | `GI-010` | Any bloating with the constipation? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:bloating` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `opioid_use` | `MED-015` | Are you taking any opioid or strong pain medicines? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `prior_abdominal_surgery` | `PMH-024` | Any history of abdominal surgery? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Cough (`cough`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the cough start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it there all the time, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 3 | core_characterization | `episode_duration` | `EVENT-004` | When it comes, how long does each episode last? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PATTERN_NOT_EPISODIC` |
| 4 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `` |
| 5 | core_characterization | `productive_cough` | `RESP-011` | Are you bringing anything up when you cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `cough_character` | `RESPQ-009` | What is the cough like? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `sputum_character` | `RESPQ-010` | What are you bringing up, and what is it like? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 8 | core_characterization | `sputum_colour` | `RESPQ-011` | What colour is it? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 9 | core_characterization | `sputum_amount` | `RESPQ-012` | How much are you bringing up? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 10 | core_characterization | `sputum_consistency` | `RESPQ-013` | Is it thick, thin, sticky, or something else? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 11 | core_characterization | `frothy_sputum` | `RESPQ-014` | Is it frothy or bubbly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 12 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 13 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 14 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 15 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `chills` | `CON-003` | Have you felt cold or shivery without uncontrollable shaking? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:chills` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Have you had any difficulty in breathing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `hemoptysis` | `RESP-004` | Have you coughed up blood? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:hemoptysis` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `chest_pain` | `CV-002` | Do you have chest pain or tightness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chest_pain` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `pleuritic_pain` | `RESP-008` | Is it worse when you take a deep breath or cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:pleuritic_pain` | `FIELD_ALREADY_CAPTURED` |
| 21 | high_priority_followup | `leg_swelling` | `CV-001` | Have you had swelling in one or both legs? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:leg_swelling` | `FIELD_ALREADY_CAPTURED` |
| 22 | high_priority_followup | `recent_immobility` | `SOC-014` | Have you been stuck in bed, on a long trip, or not moving around much recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_immobility` | `FIELD_ALREADY_CAPTURED` |
| 23 | high_priority_followup | `wheeze` | `RESPQ-004` | Do you hear a whistling sound when you breathe? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:wheeze` | `FIELD_ALREADY_CAPTURED` |
| 24 | high_priority_followup | `stridor` | `RESPQ-005` | Is your breathing noisy or harsh? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:stridor` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `runny_nose` | `RESP-010` | Do you have a runny nose? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:runny_nose` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `sore_throat` | `ENT-000` | Do you have a sore throat? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:sore_throat` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `malaise` | `CON-009` | Have you generally felt unwell or weak all over? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:malaise` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `fatigue` | `CON-005` | Have you been unusually tired? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:fatigue` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `recent_antibiotics` | `MED-002` | Have you taken any antibiotics in the last few weeks? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 30 | targeted_followup | `recent_travel` | `SOC-007` | Have you traveled anywhere recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_travel` | `FIELD_ALREADY_CAPTURED` |
| 31 | targeted_followup | `post_tussive_vomiting` | `RESP-013` | Have you vomited after coughing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 32 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Diarrhea (`diarrhea`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the diarrhea start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it happening constantly, or in repeated episodes? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `stool_frequency` | `GIQ-008` | How often are you passing stool? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `stool_consistency` | `GIQ-015` | What is the stool like? Is it watery, loose, formed, or something else? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `stool_content` | `GIQ-014` | What have you noticed in the stool? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `blood_in_stool` | `GI-004B` | Have you seen blood in the stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:blood_in_stool` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `melena` | `GIQ-021` | Has the stool been black or tarry? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `detail` | `ros:melena` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 12 | high_priority_followup | `dehydration` | `CON-011A` | Have you been very dry, dizzy when standing, or unable to keep fluids down? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `low_urine_output` | `CON-011B` | Have you been passing much less urine than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:low_urine_output` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `vomiting_frequency` | `GIQ-001` | How often are you vomiting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `severe_abdominal_pain` | `GI-013` | Do you have severe abdominal pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `abdominal_distension` | `GI-005` | Is your abdomen swollen or distended? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `bowel_obstruction_symptom` | `GI-023` | Are you unable to pass stool or gas? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:bowel_obstruction` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `weakness` | `CON-006` | Have you felt unusually weak? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `abdominal_pain` | `GI-008` | Do you have abdominal pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `vomiting` | `GI-002` | Have you vomited? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `chills` | `CON-003` | Have you felt cold or shivery without uncontrollable shaking? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:chills` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `food_exposure` | `CTX-002` | Did this seem to start after any food exposure or suspicious meal? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:food_exposure` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `recent_travel` | `SOC-007` | Have you traveled anywhere recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_travel` | `FIELD_ALREADY_CAPTURED` |
| 25 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Dizziness (`dizziness`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `dizziness` | `NEU-001` | Have you been feeling dizzy or lightheaded? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:dizziness` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `onset` | `EVENT-001` | When did the dizziness start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has it been going on? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `dizziness_type` | `NEURO-032` | Is it more like spinning, lightheadedness, near-fainting, or imbalance? | `SHORT_TEXT` | `qualifier` | `ros:dizziness` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `pattern` | `EVENT-003` | Is the dizziness constant, or does it come and go in episodes? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `positional_trigger` | `NEURO-033` | Is it triggered by turning in bed, looking up, bending, or changing head position? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `standing_trigger` | `EVENT-013` | Does it happen when you stand up or after standing for a while? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `spinning_sensation` | `NEURO-034` | Does it feel like the room is spinning or moving? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `lightheadedness` | `NEURO-035` | Does it feel more like lightheadedness or near-fainting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:dizziness` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `imbalance` | `NEURO-036` | Do you feel off-balance or unsteady when walking or standing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:gait_or_balance_problem` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `loss_of_consciousness` | `NEURO-001` | Did you actually pass out or lose consciousness with the dizziness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `chest_pain` | `CV-002` | Do you have chest pain with the dizziness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chest_pain` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `palpitations` | `CV-003` | Do you feel racing, pounding, or irregular heartbeats with it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:palpitations` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Are you short of breath with the dizziness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `focal_weakness` | `NEURO-023` | Any weakness on one side, facial droop, or one-sided clumsiness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `headache` | `NEU-005` | Do you have a headache with it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:headache` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `fever` | `CON-001` | Any fever with the dizziness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `pregnancy_context` | `GYNHX-001` | Could you be pregnant? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 19 | targeted_followup | `hearing_change` | `ENT-009` | Have you noticed reduced hearing or hearing changes? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `tinnitus` | `ENT-010` | Do you hear ringing, buzzing, or noise in the ear? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `dehydration_context` | `CTX-022` | Had you been dehydrated, not drinking, vomiting, having diarrhea, or losing fluids before this started? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `recent_illness` | `CTX-015` | Have you had a recent illness before the dizziness started? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `nausea` | `GI-007` | Do you have nausea with the dizziness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:nausea` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `vomiting` | `GI-002` | Have you been vomiting with the dizziness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `vomiting_frequency` | `GIQ-001` | How often are you vomiting? | `SHORT_TEXT` | `detail` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 26 | targeted_followup | `dehydration` | `CON-011A` | Have you been very dry, dizzy when standing, or unable to keep fluids down? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `low_urine_output` | `CON-011B` | Have you been passing much less urine than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:low_urine_output` | `FIELD_ALREADY_CAPTURED` |
| 28 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Dysuria (`dysuria`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the pain or burning when passing urine start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it there every time you pass urine, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `severity` | `PAIN-015` | On a scale of 0 to 10, how bad is it? | `SCALE_0_10` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `dysuria_character` | `GUQ-004` | What does the pain or burning feel like? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `voiding_timing_relation` | `GUQ-005` | Is it before, during, or after passing urine? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `chills` | `CON-003` | Have you felt cold or shivery without uncontrollable shaking? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:chills` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `flank_pain` | `GU-007` | Do you have pain in your side or back near the kidneys? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:flank_pain` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `hematuria` | `GU-006` | Have you noticed blood in the urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:hematuria` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `inability_to_pass_urine` | `GU-022` | Are you unable to pass urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:urinary_retention` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `dehydration` | `CON-011A` | Have you been very dry, dizzy when standing, or unable to keep fluids down? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `low_urine_output` | `CON-011B` | Have you been passing much less urine than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:low_urine_output` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `severe_abdominal_pain` | `GI-013` | Do you have severe lower abdominal or belly pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `urinary_frequency` | `GU-002` | Are you passing urine more often than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_frequency` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `urinary_urgency` | `GU-003` | Do you feel a sudden urge to pass urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_urgency` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `suprapubic_pain` | `GU-008B` | Do you have pain in the lower middle part of your belly just above the pubic bone? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `abdominal_pain` | `GI-008` | Do you have any other abdominal pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `nausea` | `GI-007` | Have you been nauseated? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:nausea` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `vomiting` | `GI-002` | Have you vomited? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `urethral_discharge` | `GU-009B` | Have you noticed any discharge from the urine opening? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `vaginal_discharge` | `GYN-002` | Have you noticed any vaginal discharge? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vaginal_discharge` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `pregnancy_context` | `GYNHX-001` | Could you be pregnant, or is pregnancy a possibility? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 27 | targeted_followup | `recent_sexual_exposure` | `SOC-015` | Have you had a recent sexual exposure that may be relevant? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `prior_stones` | `PMH-023` | Have you had kidney or urine stones before? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `weakness` | `CON-006` | Have you felt unusually weak? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 30 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Fatigue (`fatigue`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | opening | `presenting_complaint_narrative` | `NARR-001` | Please provide information about presenting complaint narrative. | `NARRATIVE_FREE_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `onset` | `EVENT-001` | When did you first notice the fatigue or unusual tiredness? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | Do you have duration? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `severity` | `PAIN-015` | Do you have severity? | `SCALE_0_10` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `functional_impact` | `PAIN-020` | Do you have functional impact? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | high_priority_followup | `breathlessness_at_rest` | `RESPQ-001` | Does it happen even when you are resting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 7 | high_priority_followup | `palpitations` | `CV-003` | Have you felt your heart racing or beating irregularly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:palpitations` | `FIELD_ALREADY_CAPTURED` |
| 8 | high_priority_followup | `loss_of_consciousness` | `NEURO-001` | Have you actually passed out or lost consciousness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `dizziness` | `NEU-001` | Have you felt dizzy, lightheaded, or near-fainting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:dizziness` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `blood_in_stool` | `GI-004B` | Have you noticed blood in your stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:blood_in_stool` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `melena` | `GIQ-021` | Has your stool been black or tarry? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:melena` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `hemoptysis` | `RESP-004` | Have you coughed up blood? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:hemoptysis` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `weight_loss` | `CON-007` | Any unexplained weight loss? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:weight_loss` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `night_sweats` | `CON-004` | Have you had drenching night sweats? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:night_sweats` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `rigors` | `CON-010` | Have you had shaking chills or rigors that made your body shake? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chills` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `lymph_node_swelling` | `HEME-003` | Have you noticed any swollen glands or lymph nodes? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:lymph_node_swelling` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `sleep_quality` | `SLEEP-001` | Are you sleeping well? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `appetite_change` | `GI-006B` | Has your appetite changed? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `associated_symptoms` | `ASSOC-001` | Have any other symptoms come with it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `dysphagia` | `GI-025` | Do you have difficulty swallowing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:dysphagia` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `excessive_thirst` | `ENDO-003` | Have you been unusually thirsty? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:excessive_thirst` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `excessive_urination` | `ENDO-004` | Have you been passing urine much more often or in larger amounts than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:excessive_urination` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `cold_intolerance` | `ENDO-002` | Do you feel unusually cold? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:cold_intolerance` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `low_mood_anhedonia` | `PSY-002` | Have you had low mood or loss of interest in things you usually enjoy? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `nutrition_status` | `NUT-001` | How is your usual diet and nutrition, including any restricted eating, food avoidance, or poor access to food? | `SHORT_TEXT` | `qualifier` | `ros:nutrition_status` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `menstrual_history` | `GYNHX-008` | How heavy are your periods? Any change in cycle? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `prior_anaemia` | `PMH-028` | Have you been told you have anaemia before? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `osa_screen` | `SLEEP-002` | Do you snore loudly or feel excessively sleepy during the day? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|DURATION_BELOW_4_WEEKS` |
| 30 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Fever (`fever`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `temperature_measured` | `FEVERQ-001` | Have you checked your temperature? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `temperature_value` | `FEVERQ-002` | What was the temperature? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 3 | core_characterization | `pattern` | `EVENT-003` | Is the fever there all the time, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `time_of_day_variation` | `FEVERQ-003` | Is it worse at a particular time of day or night? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `duration` | `EVENT-002` | How long has the fever been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `rigors` | `CON-010` | Have you had shaking chills or rigors that made your body shake? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chills` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `response_to_antipyretics` | `FEVERQ-004` | Does it improve with fever medicine like acetaminophen or ibuprofen? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `confusion` | `NEU-004` | Have you been confused, unusually drowsy, or not thinking clearly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:confusion` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `headache` | `NEU-005` | Do you have a headache? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:headache` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `neck_stiffness` | `NEU-012` | Is your neck stiff or painful to bend? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:neck_stiffness` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `photophobia` | `NEU-013` | Is bright light bothering your eyes more than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:photophobia` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Have you had any difficulty in breathing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `rash` | `SKIN-001` | Do you have any rash or new skin spots? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `vomiting` | `GI-002` | Have you been vomiting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `vomiting_frequency` | `GIQ-001` | How often are you vomiting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `dehydration` | `CON-011A` | Have you been very dry, dizzy when standing, or unable to keep fluids down? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `low_urine_output` | `CON-011B` | Have you been passing much less urine than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:low_urine_output` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `severe_abdominal_pain` | `GI-013` | Do you have severe abdominal pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `chills` | `CON-003` | Have you felt cold or shivery without uncontrollable shaking? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:chills` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `malaise` | `CON-009` | Have you generally felt unwell or weak all over? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:malaise` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `fatigue` | `CON-005` | Have you been unusually tired? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:fatigue` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `weakness` | `CON-006` | Have you felt unusually weak? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `recent_travel` | `SOC-007` | Have you traveled anywhere recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_travel` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `cough` | `RESP-005` | Do you have a cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:cough` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `sore_throat` | `ENT-000` | Do you have a sore throat? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:sore_throat` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `runny_nose` | `RESP-010` | Do you have a runny nose? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:runny_nose` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `nausea` | `GI-007` | Have you been nauseated? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:nausea` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `diarrhea` | `GI-003` | Have you had diarrhea or loose stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:diarrhea` | `FIELD_ALREADY_CAPTURED` |
| 30 | targeted_followup | `abdominal_pain` | `GI-008` | Do you have abdominal pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 31 | targeted_followup | `dysuria` | `GU-001` | Do you have pain or burning when passing urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:dysuria` | `FIELD_ALREADY_CAPTURED` |
| 32 | targeted_followup | `urinary_frequency` | `GU-002` | Are you passing urine more often than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_frequency` | `FIELD_ALREADY_CAPTURED` |
| 33 | targeted_followup | `urinary_urgency` | `GU-003` | Do you feel a sudden urge to pass urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_urgency` | `FIELD_ALREADY_CAPTURED` |
| 34 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Headache (`headache`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the headache start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it there all the time, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this headache been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `severity` | `PAIN-015` | On a scale of 0 to 10, how severe is it? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `location` | `PAIN-014` | Where is the headache located? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `radiation` | `PAIN-017` | Does the pain travel anywhere else, such as the back, groin, chest, shoulder, or leg? If yes, where? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `character` | `PAIN-016` | What does the headache feel like, for example throbbing, sharp, dull, burning, cramping, pressure-like, stabbing, or aching? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `sudden_onset` | `HEADQ-001` | Did the headache start suddenly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `maximal_at_onset` | `HEADQ-002` | Was it at its worst right when it started? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `worst_headache_of_life` | `HEADQ-003` | Is this the worst headache you have ever had? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `confusion` | `NEU-004` | Have you been confused or not thinking clearly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:confusion` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `neck_stiffness` | `NEU-012` | Is your neck stiff or painful to bend? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:neck_stiffness` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `photophobia` | `NEU-013` | Is bright light bothering your eyes more than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:photophobia` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `weakness` | `CON-006` | Have you had any weakness in your face, arm, or leg? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `numbness` | `NEURO-004` | Have you had numbness or loss of feeling anywhere? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:numbness` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `speech_difficulty` | `NEU-010` | Have you had trouble speaking or getting your words out? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:speech_difficulty` | `FIELD_ALREADY_CAPTURED` |
| 21 | high_priority_followup | `vision_changes` | `NEU-011` | Have you had any change in your vision? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vision_changes` | `FIELD_ALREADY_CAPTURED` |
| 22 | high_priority_followup | `seizure` | `NEU-008` | Have you had any seizure or shaking episode? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:seizure` | `FIELD_ALREADY_CAPTURED` |
| 23 | high_priority_followup | `recent_head_trauma` | `TRAUMA-001` | Have you had any recent hit or injury to the head? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 24 | high_priority_followup | `anticoagulant_use` | `MED-003` | Are you taking blood thinners? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `nausea` | `GI-007` | Have you been nauseated? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:nausea` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `vomiting` | `GI-002` | Have you vomited? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `dizziness` | `NEU-001` | Have you felt dizzy or lightheaded? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:dizziness` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `fainting` | `NEU-002` | Have you fainted or nearly fainted? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `transient_visual_obscurations` | `HEADQ-006` | Have you had brief episodes where your vision goes dim or blacks out? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 30 | targeted_followup | `jaw_pain_with_chewing` | `HEADQ-007` | Do you get jaw pain when chewing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 31 | targeted_followup | `scalp_tenderness` | `HEADQ-008` | Is your scalp tender to touch? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 32 | targeted_followup | `ocular_redness_pain` | `HEADQ-009` | Do you have eye redness or eye pain with the headache? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:eye_symptoms` | `FIELD_ALREADY_CAPTURED` |
| 33 | targeted_followup | `rash` | `SKIN-001` | Do you have any rash or new skin spots? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 34 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Hematuria (`hematuria`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did you first notice blood in the urine? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it happening every time, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `hematuria` | `GU-006` | Any blood in the urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:hematuria` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `hematuria_visible` | `GU-020` | Can you actually see blood in the urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | high_priority_followup | `inability_to_pass_urine` | `GU-022` | Are you unable to pass urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:urinary_retention` | `FIELD_ALREADY_CAPTURED` |
| 7 | high_priority_followup | `clots_in_urine` | `GU-021` | Any clots in the urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | high_priority_followup | `flank_pain` | `GU-007` | Any pain in the side or flank? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:flank_pain` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `fever` | `CON-001` | Any fever with the blood in the urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `recent_trauma` | `CTX-004` | Did this start after any recent trauma or injury? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `anticoagulant_use` | `MED-003` | Are you taking any blood thinners or anticoagulants? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | targeted_followup | `dysuria` | `GU-001` | Any burning or pain when passing urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:dysuria` | `FIELD_ALREADY_CAPTURED` |
| 13 | targeted_followup | `urinary_frequency` | `GU-002` | Are you passing urine more often than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_frequency` | `FIELD_ALREADY_CAPTURED` |
| 14 | targeted_followup | `urinary_urgency` | `GU-003` | Any urgency to pass urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_urgency` | `FIELD_ALREADY_CAPTURED` |
| 15 | targeted_followup | `suprapubic_pain` | `GU-008B` | Any pain low in the lower abdomen or over the bladder area? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 16 | targeted_followup | `recent_catheter` | `CTX-011` | Any recent catheter or urinary procedure? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `prior_uti` | `PMH-022` | Any history of prior urinary tract infections? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `prior_stones` | `PMH-023` | Any history of kidney or urinary stones? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `history_of_cancer` | `PMH-014` | Any history of cancer? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `family_history_urologic_cancer` | `GUC-003` | Any family history of bladder or kidney cancer? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `context_history` | `context:urologic_cancer_family_history` | `FIELD_ALREADY_CAPTURED` |
| 21 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Joint pain (`joint_pain`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the joint pain start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is the pain constant, or does it come and go in episodes? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `location` | `PAIN-014` | Which joint is affected? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `pain_specific_location` | `PAIN-014B` | Can you point to the exact spot within the joint area? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `character` | `PAIN-016` | What does the joint pain feel like, for example throbbing, sharp, dull, burning, cramping, pressure-like, stabbing, or aching? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `severity` | `PAIN-015` | On a scale of 0 to 10, how severe is it? | `SCALE_0_10` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `recent_trauma` | `CTX-004` | Did this start after any recent trauma or injury? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `fever` | `CON-001` | Any fever with the joint pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `inability_to_bear_weight` | `MSK-007` | Are you unable to bear weight on it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:inability_to_bear_weight` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `swelling` | `MASS-001` | Any swelling of the joint? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:swelling` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `warmth` | `SKIN-011` | Does the joint feel warm? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `redness` | `SKIN-010` | Is there redness around the joint? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `stiffness` | `MSK-010` | Any stiffness in the joint? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:stiffness` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `morning_stiffness` | `MSKQ-011` | Is there stiffness in the morning? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `multiple_joints_involved` | `MSKQ-012` | Is it affecting more than one joint? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `pain_worse_with_movement` | `MSKQ-010` | Is the pain worse with movement? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 21 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Loss of consciousness (`loss_of_consciousness`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `loss_of_consciousness` | `NEURO-001` | Did you lose consciousness or pass out? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `onset` | `EVENT-001` | When did this happen? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | About how long were you out or not fully aware? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `complete_blackout` | `EVENT-010` | Did you completely black out? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `detail` | `ros:fainting` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 5 | core_characterization | `witnessed_collapse` | `EVENT-011` | Did anyone see you suddenly go down or collapse? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 6 | high_priority_followup | `head_injury` | `TRAUMA-002` | Did you hit your head or have a head injury with the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | high_priority_followup | `chest_pain` | `CV-002` | Did you have chest pain before or during the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chest_pain` | `FIELD_ALREADY_CAPTURED` |
| 8 | high_priority_followup | `palpitations` | `CV-003` | Did you feel racing, pounding, or irregular heartbeats before the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:palpitations` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Were you short of breath before or during the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `focal_weakness` | `NEURO-023` | Any weakness on one side afterward? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `seizure` | `NEU-008` | Did anyone think it looked like a seizure or seizure-like event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:seizure` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `pregnancy_context` | `GYNHX-001` | Could you be pregnant? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 13 | high_priority_followup | `fever` | `CON-001` | Any fever before or around the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 14 | targeted_followup | `prodrome` | `NEURO-041` | Was there any warning beforehand, such as dizziness, lightheadedness, nausea, sweating, blurred vision, or palpitations? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 15 | targeted_followup | `return_to_baseline` | `NEURO-029` | Did you return fully to your usual self afterward? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 16 | targeted_followup | `prior_similar_events` | `PMH-027` | Has something like this happened before? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `dehydration_context` | `CTX-022` | Had you been dehydrated, not drinking, vomiting, having diarrhea, or losing fluids before this happened? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `standing_trigger` | `EVENT-013` | Did it happen while standing up or after standing for a while? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `exertional_trigger` | `EVENT-012` | Did it happen during exercise or exertion? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Oedema (`oedema`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | opening | `presenting_complaint_narrative` | `NARR-001` | Please provide information about presenting complaint narrative. | `NARRATIVE_FREE_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `onset` | `EVENT-001` | Do you have onset? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | Do you have duration? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `swelling_location` | `OED-000` | Where is the swelling — feet, ankles, legs, hands, face, abdomen, or all over? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `swelling_distribution` | `OED-001` | Is the swelling on one side, both sides, or generalized all over? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `severity` | `PAIN-015` | Do you have severity? | `SCALE_0_10` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | high_priority_followup | `acute_unilateral_swelling` | `DVT-001` | Did one leg or one area become swollen suddenly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | high_priority_followup | `calf_pain` | `VASC-001` | Is there pain or tenderness in the calf? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `calf_redness` | `VASC-002` | Is the calf or swollen area red? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Have you had any difficulty in breathing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `orthopnea` | `RESPQ-002` | Is your breathing worse when you lie flat? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:orthopnea` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `paroxysmal_nocturnal_dyspnea` | `RESPQ-003` | Do you wake from sleep short of breath or gasping for air? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:paroxysmal_nocturnal_dyspnea` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `facial_swelling` | `SKIN-013` | Have you had facial or lip swelling? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:facial_swelling` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `tongue_swelling` | `ENT-011` | Have you had tongue swelling? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:tongue_swelling` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `chest_pain` | `CV-002` | Do you have any chest pain or tightness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chest_pain` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `recent_change_in_pattern` | `EVENT-020` | Has the pattern changed noticeably in the last few weeks? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|DURATION_BELOW_4_WEEKS` |
| 17 | high_priority_followup | `low_urine_output` | `CON-011B` | Are you passing much less urine than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:low_urine_output` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `rapid_weight_gain` | `CON-012` | Have you gained weight rapidly over the past few days or weeks? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `local_inflammation_over_swelling` | `OED-005` | Is there redness, warmth, tenderness, or skin irritation over the swollen area? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:local_inflammation_over_swelling` | `FIELD_ALREADY_CAPTURED` |
| 21 | high_priority_followup | `abdominal_distension` | `GI-005` | Has your abdomen become swollen or more bloated than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `course` | `EVENT-006` | Do you have course? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `pitting_character` | `OED-002` | If you press on the swollen area, does it leave an indent? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `diurnal_variation` | `OED-003` | Is the swelling worse at the end of the day? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `skin_changes_over_swelling` | `DERM-011` | Any skin changes over the swollen area? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `context_or_qualifier` | `context:swelling_context` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `functional_impact` | `PAIN-020` | Do you have functional impact? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `associated_symptoms` | `ASSOC-001` | Have any other symptoms come with it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `known_heart_failure` | `PMH-030` | Have you ever been told you have heart failure? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `known_kidney_disease` | `PMH-031` | Do you have any known kidney problems? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 30 | targeted_followup | `known_liver_disease` | `PMH-032` | Do you have any liver problems? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 31 | targeted_followup | `swelling_related_medications` | `MED-017` | Are you taking any medicines that can cause swelling, such as amlodipine, steroids, NSAIDs, gabapentin, or pioglitazone? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `context_or_qualifier` | `context:swelling_context` | `FIELD_ALREADY_CAPTURED` |
| 32 | targeted_followup | `prior_clot_history` | `VASC-004` | Have you ever had a blood clot, such as DVT or pulmonary embolism? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:prior_clot_history` | `FIELD_ALREADY_CAPTURED` |
| 33 | targeted_followup | `recent_immobility` | `SOC-014` | Have you been stuck in bed, on a long trip, or not moving around much recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_immobility` | `FIELD_ALREADY_CAPTURED` |
| 34 | targeted_followup | `recent_travel` | `SOC-007` | Have you traveled anywhere recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_travel` | `FIELD_ALREADY_CAPTURED` |
| 35 | targeted_followup | `recent_surgery` | `SURG-001` | Have you had any recent surgery or procedure? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 36 | targeted_followup | `recent_trauma` | `CTX-004` | Did this start after an injury, fall, blow, or accident? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 37 | targeted_followup | `hypothyroid_symptoms` | `ENDO-007` | Have you had symptoms such as cold intolerance, constipation, dry skin, or unexplained weight gain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 38 | targeted_followup | `pregnancy_context` | `GYNHX-001` | Could you be pregnant now, or are you recently postpartum? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 39 | targeted_followup | `jaundice` | `GI-012` | Have you noticed yellowing of your eyes or skin? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:jaundice` | `FIELD_ALREADY_CAPTURED` |
| 40 | targeted_followup | `foamy_urine` | `REN-001` | Is your urine foamy or frothy? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:foamy_urine` | `FIELD_ALREADY_CAPTURED` |
| 41 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Generalized body pain (`pain`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the generalized body pain start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is the pain constant, or does it come and go in episodes? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `widespread_pain` | `PAIN-030` | Is the pain widespread or all over the body? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `body_aches` | `PAIN-031` | Are you having body aches all over? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `character` | `PAIN-016` | What does the pain feel like, for example throbbing, sharp, dull, burning, cramping, pressure-like, stabbing, or aching? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `severity` | `PAIN-015` | On a scale of 0 to 10, how severe is it? | `SCALE_0_10` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `fever` | `CON-001` | Any fever with the body pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `weakness` | `CON-006` | Any unusual weakness with this? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `rash` | `SKIN-001` | Any rash or skin change with this? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `weight_loss` | `CON-007` | Any unexplained weight loss? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weight_loss` | `FIELD_ALREADY_CAPTURED` |
| 15 | targeted_followup | `fatigue` | `CON-005` | Any fatigue with the body pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:fatigue` | `FIELD_ALREADY_CAPTURED` |
| 16 | targeted_followup | `stiffness` | `MSK-010` | Any generalized stiffness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:stiffness` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `recent_illness` | `CTX-015` | Have you been sick recently before this started? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Palpitations (`palpitations`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the palpitations start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it there all the time, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `episode_duration` | `EVENT-004` | When it happens, how long does each episode last? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PATTERN_NOT_EPISODIC` |
| 4 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `frequency` | `EVENT-005` | How often does it happen? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `palpitations_character` | `PALP-001` | What do the palpitations feel like? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `trigger_context` | `CTX-013` | What were you doing when it started? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `chest_pain` | `CV-002` | Do you have chest pain or tightness with the palpitations? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chest_pain` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Do you get short of breath with the palpitations? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `fainting` | `NEU-002` | Have you fainted or nearly fainted with the palpitations? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `dizziness` | `NEU-001` | Do you get dizzy or lightheaded with the palpitations? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:dizziness` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `weakness` | `CON-006` | Have you felt weak during the palpitations? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `confusion` | `NEU-004` | Have you felt confused or not thinking clearly during the palpitations? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:confusion` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `palpitations_at_rest` | `PALPQ-003` | Do they happen while you are resting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `palpitations_with_exertion` | `PALPQ-004` | Do they happen or get worse with exertion? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `prior_cardiac_history` | `CVHX-001` | Have you ever been told you have a heart condition? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `family_history_sudden_death` | `CVHX-002` | Has anyone in your family died suddenly from a heart problem or unexpectedly at a young age? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `nausea` | `GI-007` | Have you been nauseated with the palpitations? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:nausea` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `caffeine_trigger` | `PALPQ-005` | Do they seem triggered by coffee, tea, cola, or caffeine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `energy_drink_trigger` | `PALPQ-006` | Do they seem triggered by energy drinks? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `decongestant_trigger` | `PALPQ-007` | Do they seem triggered by cold medicines or decongestants? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 25 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Rash (`rash`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `rash` | `SKIN-001` | Have you noticed a rash? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `onset` | `EVENT-001` | When did the rash start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has it been there? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `rash_site` | `DERM-001` | Where is the rash located? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `rash_specific_location` | `DERM-002` | Can you point to the exact area? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `spread_pattern` | `DERM-003` | Has the rash spread or changed area? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `itching` | `SKIN-002` | Is it itchy? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:itching` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `painful_rash` | `DERM-005` | Is the rash painful? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `fever` | `CON-001` | Any fever with the rash? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `blistering` | `SKIN-012` | Are there blisters? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `skin_peeling` | `SKIN-005` | Is the skin peeling? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `mouth_involvement` | `SKIN-006B` | Are there sores or rash in the mouth? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `eye_involvement` | `SKIN-008` | Are the eyes involved or irritated? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Are you short of breath or having trouble breathing with the rash? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `facial_swelling` | `SKIN-013` | Is there swelling of the face, lips, or tongue? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:facial_swelling` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `recent_medication_exposure` | `MED-010` | Did the rash start after a new medicine or treatment? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `redness` | `SKIN-010` | Is the rash red? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `warmth` | `SKIN-011` | Does it feel warm? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `discharge` | `SKIN-009` | Any discharge or pus from it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `recent_illness` | `CTX-015` | Have you had a recent illness before the rash started? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `contact_exposure` | `CTX-020` | Was there recent contact with a new soap, cream, plant, chemical, fabric, or other exposure? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:contact_exposure` | `FIELD_ALREADY_CAPTURED` |
| 22 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Seizure (`seizure`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the seizure happen? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `duration` | `EVENT-002` | About how long did it last? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `seizure` | `NEU-008` | Did you have a seizure or seizure-like event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:seizure` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `witnessed_seizure_activity` | `NEURO-019` | Did anyone witness seizure-like activity? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | high_priority_followup | `loss_of_consciousness` | `NEURO-001` | Did you lose consciousness during the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 6 | high_priority_followup | `head_injury` | `TRAUMA-002` | Did you hit your head or have a head injury with the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | high_priority_followup | `fever` | `CON-001` | Any fever with or before the seizure? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 8 | high_priority_followup | `focal_weakness` | `NEURO-023` | Any weakness on one side afterward? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `pregnancy_context` | `GYNHX-001` | Could you be pregnant? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 10 | high_priority_followup | `known_epilepsy` | `PMH-025` | Do you have a known seizure disorder or epilepsy? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `prior_seizure_history` | `PMH-026` | Has this happened before? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | targeted_followup | `postictal_confusion` | `NEURO-020` | Were you confused afterward? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 13 | targeted_followup | `tongue_biting` | `NEURO-021` | Any tongue biting during the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 14 | targeted_followup | `urinary_incontinence` | `NEURO-022` | Any loss of bladder control during the event? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 15 | targeted_followup | `medication_nonadherence` | `MED-016` | Have you missed seizure or other important medicines recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 16 | targeted_followup | `substance_withdrawal_context` | `CTX-012` | Has there been recent alcohol or substance withdrawal? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `aura` | `NEURO-027` | Was there any warning before the event, like a strange feeling, smell, or sensation? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `seizure_type` | `NEURO-028` | What was the seizure like — shaking, staring, one-sided movements, or something else? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `trigger_context` | `CTX-013` | Was there anything that seemed to trigger it, such as missed sleep, missed medicines, alcohol withdrawal, flashing lights, or illness? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `return_to_baseline` | `NEURO-029` | Did you return fully to your usual self afterward? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `recurrent_events` | `NEURO-030` | Have there been repeated similar events? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `clustered_events` | `NEURO-031` | Did more than one event happen close together? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 23 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Shortness of Breath (`shortness_of_breath`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the breathing problem start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it there all the time, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 3 | core_characterization | `episode_duration` | `EVENT-004` | When it happens, how long does each episode last? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PATTERN_NOT_EPISODIC` |
| 4 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `` |
| 5 | core_characterization | `severity` | `PAIN-015` | How bad is it from 0 to 10? | `SCALE_0_10` | `qualifier` | `` | `` |
| 6 | core_characterization | `exertional_trigger` | `EVENT-012` | Does it come on or get worse with physical activity? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `` |
| 7 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `` |
| 8 | high_priority_followup | `breathlessness_at_rest` | `RESPQ-001` | Does it happen even when you are resting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `unable_to_speak_full_sentences` | `RESP-002` | Is your breathing so bad that you cannot speak in full sentences? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `cyanosis` | `RESP-003` | Have your lips, face, or fingertips looked bluish? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `confusion` | `NEU-004` | Have you felt confused or not like yourself? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:confusion` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `stridor` | `RESPQ-005` | Is your breathing noisy or harsh? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:stridor` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `chest_pain` | `CV-002` | Do you have any chest pain or tightness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:chest_pain` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `hemoptysis` | `RESP-004` | Have you coughed up blood? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:hemoptysis` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `pleuritic_pain` | `RESP-008` | Is it worse when you take a deep breath or cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:pleuritic_pain` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `leg_swelling` | `CV-001` | Have you had swelling in one or both legs? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:leg_swelling` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `recent_immobility` | `SOC-014` | Have you been stuck in bed, on a long trip, or not moving around much recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_immobility` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `orthopnea` | `RESPQ-002` | Is it worse when you lie flat? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:orthopnea` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `paroxysmal_nocturnal_dyspnea` | `RESPQ-003` | Do you wake from sleep short of breath? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:paroxysmal_nocturnal_dyspnea` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `fainting` | `NEU-002` | Have you fainted or passed out? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fainting` | `FIELD_ALREADY_CAPTURED` |
| 21 | high_priority_followup | `dizziness` | `NEU-001` | Have you felt dizzy or lightheaded? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:dizziness` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `wheeze` | `RESPQ-004` | Do you hear a whistling sound when you breathe? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:wheeze` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `positional_component` | `RESPQ-008` | Is it affected by your position, such as lying down or sitting up? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `cough` | `RESP-005` | Do you have a cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:cough` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `cough_character` | `RESPQ-009` | What is the cough like? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 26 | targeted_followup | `sputum_character` | `RESPQ-010` | Are you bringing anything up, and what is it like? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 27 | targeted_followup | `asthma_history` | `PMH-002` | Do you have asthma? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `copd_history` | `PMH-003` | Do you have COPD or chronic obstructive lung disease? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `palpitations` | `CV-003` | Have you felt your heart racing or beating irregularly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:palpitations` | `FIELD_ALREADY_CAPTURED` |
| 30 | targeted_followup | `recent_travel` | `SOC-007` | Have you traveled anywhere recently? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_travel` | `FIELD_ALREADY_CAPTURED` |
| 31 | targeted_followup | `recent_antibiotics` | `MED-002` | Have you taken any antibiotics in the last few weeks? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 32 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Sore throat (`sore_throat`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `sore_throat` | `ENT-000` | Do you have a sore throat? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:sore_throat` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `onset` | `EVENT-001` | When did the sore throat start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has it been going on? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `pain_with_swallowing` | `ENT-001` | Does it hurt when you swallow? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:sore_throat` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `voice_change` | `ENT-003` | Has your voice changed? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:sore_throat` | `FIELD_ALREADY_CAPTURED` |
| 6 | high_priority_followup | `drooling` | `ENT-005` | Are you drooling or unable to handle your saliva? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | high_priority_followup | `shortness_of_breath` | `RESP-001` | Are you short of breath or having trouble breathing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 8 | high_priority_followup | `fever` | `CON-001` | Any fever with the sore throat? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `neck_swelling` | `ENT-006` | Is there swelling in the neck or throat area? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:neck_swelling` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `dysphagia` | `GI-025` | Are you having trouble swallowing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:dysphagia` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `muffled_voice` | `ENT-004` | Does your voice sound muffled or like a hot-potato voice? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:sore_throat` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `rash` | `SKIN-001` | Do you have a rash anywhere on the body? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `mouth_involvement` | `SKIN-006B` | Are there sores, ulcers, or other changes in the mouth? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:rash` | `FIELD_ALREADY_CAPTURED` |
| 14 | targeted_followup | `cough` | `RESP-005` | Do you also have a cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:cough` | `FIELD_ALREADY_CAPTURED` |
| 15 | targeted_followup | `runny_nose` | `RESP-010` | Do you also have a runny or blocked nose? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:runny_nose` | `FIELD_ALREADY_CAPTURED` |
| 16 | targeted_followup | `tonsillar_exudate` | `ENT-008` | Have you noticed white patches, pus, or exudate on the tonsils? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `sick_contact` | `CTX-019` | Have you been around anyone who was sick with a sore throat, cold, or similar illness? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:sick_contact` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `throat_irritant_exposure` | `CTX-021` | Was there a recent exposure to smoke, dust, chemicals, allergens, or another throat irritant? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:allergy_or_irritant_exposure` | `FIELD_ALREADY_CAPTURED` |
| 19 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Swelling or lump (`swelling_or_lump`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did you first notice the swelling or lump? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `duration` | `EVENT-002` | How long has it been there? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `lump_swelling` | `MASS-000` | Have you noticed a swelling or lump? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:swelling` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `lump_site` | `MASS-002` | Where is the swelling or lump located? | `SHORT_TEXT` | `qualifier` | `ros:swelling` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `lump_specific_location` | `MASS-003` | Can you point to the exact spot of the swelling or lump? | `SHORT_TEXT` | `qualifier` | `ros:location` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `growth_pattern` | `MASS-004` | Has it been growing or changing in size? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `painful_lump` | `MASS-005` | Is the swelling or lump painful? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `multiple_lumps` | `MASS-006` | Is there more than one swelling or lump? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `rapid_enlargement` | `MASS-007` | Has it enlarged quickly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | high_priority_followup | `redness` | `SKIN-010` | Is there redness around it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `warmth` | `SKIN-011` | Does it feel warm? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `fever` | `CON-001` | Any fever with it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `discharge` | `SKIN-009` | Any discharge or pus from it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `weight_loss` | `CON-007` | Any unexplained weight loss? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weight_loss` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `night_sweats` | `CON-004` | Any night sweats? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:night_sweats` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `recent_trauma` | `CTX-004` | Did this start after any recent trauma or injury? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | targeted_followup | `tenderness` | `MASS-009` | Is it tender to touch? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `mobility` | `MASS-008` | Does it move under the skin or feel fixed? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `recent_insect_bite` | `CTX-014` | Was there a recent insect bite there? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `recent_infection` | `CTX-016` | Have you had a recent infection nearby or elsewhere? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:recent_infection` | `FIELD_ALREADY_CAPTURED` |
| 21 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Vaginal discharge (`vaginal_discharge`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the discharge start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it there all the time, or does it come and go? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `severity` | `PAIN-015` | On a scale of 0 to 10, how severe is it? | `SCALE_0_10` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `discharge_amount` | `GYNQ-004` | How much discharge are you having? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `discharge_color` | `GYNQ-001` | What colour is the discharge? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `discharge_consistency` | `GYNQ-002` | What is the discharge like in consistency? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `discharge_odor` | `GYNQ-003` | Does the discharge have an odor? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `aggravating_factors` | `PAIN-018` | What makes it worse, such as movement, coughing, eating, urinating, passing stool, touching it, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as rest, lying still, medicines, food, passing urine or stool, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `abdominal_pain` | `GI-008` | Do you have lower abdominal or pelvic pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `severe_abdominal_pain` | `GI-013` | Do you have severe abdominal or pelvic pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `pregnancy_context` | `GYNHX-001` | Could you be pregnant, or is pregnancy a possibility? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 16 | high_priority_followup | `lmp` | `GYNHX-002` | When was your last menstrual period? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 17 | high_priority_followup | `abnormal_vaginal_bleeding` | `GYN-003` | Have you had heavy or unusual vaginal bleeding? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vaginal_bleeding` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `weakness` | `CON-006` | Have you felt unusually weak? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `vulvovaginal_irritation` | `GYN-004` | Do you have vulvovaginal itching, burning, or irritation? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vaginal_discharge` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `dysuria` | `GU-001` | Do you have pain or burning when passing urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:dysuria` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `urinary_frequency` | `GU-002` | Are you passing urine more often than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_frequency` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `urinary_urgency` | `GU-003` | Do you feel a sudden urge to pass urine? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:urinary_urgency` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `recent_sexual_exposure` | `SOC-015` | Have you had a recent sexual exposure that may be relevant? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 24 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Vomiting (`vomiting`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | core_characterization | `onset` | `EVENT-001` | When did the vomiting start? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `pattern` | `EVENT-003` | Is it constant, or does it come in episodes? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `duration` | `EVENT-002` | How long has this been going on altogether? | `TEMPORAL_WITH_UNIT_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `vomiting_frequency` | `GIQ-001` | How often are you vomiting? | `SHORT_TEXT` | `qualifier` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `vomit_content` | `GIQ-016` | What does the vomit contain—food, bile, blood, coffee-ground material, stool-like material, mucus, or something else? | `SHORT_TEXT` | `qualifier` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 6 | core_characterization | `vomit_amount` | `GIQ-018` | About how much do you bring up each time—small amounts, moderate amounts, or large amounts? | `SHORT_TEXT` | `qualifier` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 7 | core_characterization | `projectile_vomiting` | `GIQ-019` | Is the vomiting forceful or projectile, meaning it shoots out suddenly? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 8 | core_characterization | `aggravating_factors` | `PAIN-018` | What seems to trigger or worsen the vomiting, such as food, drink, movement, smells, coughing, pain, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 9 | core_characterization | `relieving_factors` | `PAIN-019` | What makes it better, such as resting, stopping food, medicines, sitting still, or nothing? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 10 | core_characterization | `functional_impact` | `PAIN-020` | How is it affecting what you can do, such as walking, standing, eating, sleeping, breathing, or daily activities? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `vomiting` | `GI-002` | Have you been vomiting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `dehydration` | `CON-011A` | Have you been very dry, dizzy when standing, or unable to keep fluids down? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `low_urine_output` | `CON-011B` | Have you been passing much less urine than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:low_urine_output` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `hematemesis` | `GI-009B` | Have you seen blood in the vomit? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `coffee_ground_vomit` | `GI-010B` | Has the vomit looked dark like coffee grounds? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `severe_abdominal_pain` | `GI-013` | Do you have severe abdominal pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `abdominal_distension` | `GI-005` | Is your abdomen swollen or distended? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 18 | high_priority_followup | `bowel_obstruction_symptom` | `GI-023` | Are you unable to pass stool or gas? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:bowel_obstruction` | `FIELD_ALREADY_CAPTURED` |
| 19 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 20 | high_priority_followup | `weakness` | `CON-006` | Have you felt unusually weak? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `abdominal_pain` | `GI-008` | Do you have abdominal pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `diarrhea` | `GI-003` | Have you had diarrhea or loose stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:diarrhea` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `headache` | `NEU-005` | Do you have a headache? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:headache` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `food_exposure` | `CTX-002` | Did this seem to start after any food exposure or suspicious meal? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:food_exposure` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `chills` | `CON-003` | Have you felt cold or shivery without uncontrollable shaking? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:chills` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `pregnancy_context` | `GYNHX-001` | Could you be pregnant, or is pregnancy a possibility? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 27 | targeted_followup | `lmp` | `GYNHX-002` | When was your last menstrual period? | `SHORT_TEXT` | `detail` | `` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE\|PATIENT_ELDERLY_SKIP_PREGNANCY` |
| 28 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

## Weight Loss (`weight_loss`)

| # | Phase | Field | Code | Question | Response type | Role | Dedup family | Skip if |
|---:|---|---|---|---|---|---|---|---|
| 1 | opening | `presenting_complaint_narrative` | `NARR-001` | Please provide information about presenting complaint narrative. | `NARRATIVE_FREE_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 2 | core_characterization | `amount_lost` | `WL-001` | How much weight have you lost? | `NUMERIC_OR_SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 3 | core_characterization | `weight_loss_timeframe` | `WL-002` | Over what period of time did you lose that weight? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 4 | core_characterization | `weight_loss_intentionality` | `WL-003` | Were you trying to lose weight, or did it happen without trying? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 5 | core_characterization | `appetite_change` | `GI-006B` | Has your appetite changed? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:loss_of_appetite` | `FIELD_ALREADY_CAPTURED` |
| 6 | high_priority_followup | `rapid_loss` | `WL-004` | Did the weight come off quickly over days to weeks? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 7 | high_priority_followup | `dysphagia` | `GI-025` | Have you had trouble swallowing? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:dysphagia` | `FIELD_ALREADY_CAPTURED` |
| 8 | high_priority_followup | `vomiting` | `GI-002` | Have you been vomiting? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED` |
| 9 | high_priority_followup | `vomiting_frequency` | `GIQ-001` | How often are you vomiting? | `SHORT_TEXT` | `detail` | `ros:vomiting` | `FIELD_ALREADY_CAPTURED\|PARENT_NEGATIVE` |
| 10 | high_priority_followup | `blood_in_stool` | `GI-004B` | Have you noticed blood in your stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:blood_in_stool` | `FIELD_ALREADY_CAPTURED` |
| 11 | high_priority_followup | `melena` | `GIQ-021` | Has your stool been black or tarry? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:melena` | `FIELD_ALREADY_CAPTURED` |
| 12 | high_priority_followup | `hemoptysis` | `RESP-004` | Have you coughed up blood? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:hemoptysis` | `FIELD_ALREADY_CAPTURED` |
| 13 | high_priority_followup | `night_sweats` | `CON-004` | Have you had drenching night sweats? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:night_sweats` | `FIELD_ALREADY_CAPTURED` |
| 14 | high_priority_followup | `fever` | `CON-001` | Have you had a fever? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:fever` | `FIELD_ALREADY_CAPTURED` |
| 15 | high_priority_followup | `severe_weakness` | `CON-006S` | Have you felt severely weak or unable to do normal activities? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:weakness` | `FIELD_ALREADY_CAPTURED` |
| 16 | high_priority_followup | `dehydration` | `CON-011A` | Have you felt very dry, very thirsty, or unable to stay hydrated? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 17 | high_priority_followup | `low_urine_output` | `CON-011B` | Are you passing much less urine than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `red_flag_subtype` | `ros:low_urine_output` | `FIELD_ALREADY_CAPTURED` |
| 18 | targeted_followup | `functional_impact` | `PAIN-020` | Do you have functional impact? | `SHORT_TEXT` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 19 | targeted_followup | `associated_symptoms` | `ASSOC-001` | Have any other symptoms come with it? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 20 | targeted_followup | `diarrhea` | `GI-003` | Have you had diarrhea or loose stool? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:diarrhea` | `FIELD_ALREADY_CAPTURED` |
| 21 | targeted_followup | `abdominal_pain` | `GI-008` | Have you had abdominal pain? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:abdominal_pain` | `FIELD_ALREADY_CAPTURED` |
| 22 | targeted_followup | `change_in_bowel_habit` | `GI-024` | Have you noticed a lasting change in your bowel habits? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:change_in_bowel_habit` | `FIELD_ALREADY_CAPTURED` |
| 23 | targeted_followup | `cough` | `RESP-005` | Have you had a cough? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:cough` | `FIELD_ALREADY_CAPTURED` |
| 24 | targeted_followup | `shortness_of_breath` | `RESP-001` | Have you had shortness of breath? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `parent_symptom` | `ros:shortness_of_breath` | `FIELD_ALREADY_CAPTURED` |
| 25 | targeted_followup | `excessive_thirst` | `ENDO-003` | Have you been unusually thirsty? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:excessive_thirst` | `FIELD_ALREADY_CAPTURED` |
| 26 | targeted_followup | `excessive_urination` | `ENDO-004` | Are you passing urine more often or in larger amounts than usual? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:excessive_urination` | `FIELD_ALREADY_CAPTURED` |
| 27 | targeted_followup | `low_mood_anhedonia` | `PSY-002` | Have you felt low, lost interest, or stopped enjoying things? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 28 | targeted_followup | `nutrition_status` | `NUT-001` | How is your usual diet and nutrition, including restricted eating, food avoidance, or poor access to food? | `SHORT_TEXT` | `qualifier` | `ros:nutrition_status` | `FIELD_ALREADY_CAPTURED` |
| 29 | targeted_followup | `lymph_node_swelling` | `HEME-003` | Have you noticed swollen glands or lumps in the neck, armpit, or groin? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `ros:lymph_node_swelling` | `FIELD_ALREADY_CAPTURED` |
| 30 | targeted_followup | `hyperthyroid_symptoms` | `ENDO-006` | Have you had heat intolerance, tremor, sweating, anxiety, or a racing heartbeat? | `BOOLEAN_WITH_OPTIONAL_DETAILS` | `qualifier` | `` | `FIELD_ALREADY_CAPTURED` |
| 31 | final_closeout | `final_closeout_question` | `CLOSE-001` | Is there anything else you want to mention that we have not asked about yet? | `SHORT_TEXT` | `qualifier` | `` | `` |

