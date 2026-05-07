# Clerkship Dialogue Database Codebook v1.1.0

# Clerkship Dialogue — Database Codebook & Summary Template

Version 1.1.0 · reflects the current SQLite schema, summary engine, ROS batch selection, ROS-owned dedup families, shared escalation rules, and optional Anthropic/Ollama AI summary flow.

This codebook describes the persistent data model for the clinical intake runtime, how the clinical summary is assembled, how ROS questions are selected, and how escalation rules are evaluated. It is kept in lock-step with `app/db/db_manager.py`, `app/engine/summary_engine.py`, `app/engine/ros_runner.py`, `complaints_modules/ros_question_bank.json`, `complaints_modules/shared_v2.json`, and the active complaint files.

## What changed in v1.1.0

1. Package, contract, complaint, module, and ROS version values were standardized to 1.1.0.
2. Setup documentation now includes `ANTHROPIC_API_KEY` usage and Ollama fallback behavior.
3. The summary engine uses a deterministic template summary first, then optionally calls Anthropic, then Ollama, then falls back to the template HPI.
4. ROS dedup is now driven by ROS-owned `dedup_family` metadata rather than only raw field names.
5. Secondary complaint dedup uses exact field/code matching first and suppresses only repeated parent-symptom families.
6. Escalation rules are shared condition trees evaluated against accumulated session state after complaint, ROS, and module answers.
7. The episode-duration question is skipped when the pattern answer indicates a constant/continuous symptom.
8. Streamlit no longer uses GIF avatars; status is shown through a lightweight text panel.

## Tables — Summary

| Table (logical name) | SQL table name | Purpose |
|---|---|---|
| Session | `encounters` | One row per intake encounter. Stores metadata, patient demographics, escalation level, and final extracted state. |
| Turn | `turns` | Every system and patient message in order. Includes `question_id` and `phase`. |
| Summary | `summaries` | Template pre-summary, AI summary, and clinician-edited post-summary. |
| SessionMetric | `session_metrics` | Per-session quality and dashboard metrics. |
| SchemaVersion | `schema_version` | Applied schema version records for DB compatibility checks. |

## Table — Session (SQL: encounters)

| Column | Type | Meaning | Allowed values / notes | Example |
|---|---|---|---|---|
| `id` | INTEGER PK | Unique encounter id | Auto-increment | `1` |
| `session_name` | TEXT UNIQUE | Human-readable session identifier | Generated as `sess_<UTC>_<complaint_id>` | `sess_20260419_083000_abdominal_pain` |
| `created_at` | DATETIME | Encounter start time | Defaults to `CURRENT_TIMESTAMP` | `2026-04-19 08:30:00` |
| `ended_at` | DATETIME | Encounter end time | NULL until completion | `2026-04-19 08:38:12` |
| `primary_complaint` | TEXT | Primary complaint id | Matches complaint filename | `abdominal_pain` |
| `secondary_complaint` | TEXT JSON | Additional concern(s) | JSON string; `[]` if none | `["dizziness"]` |
| `pertinent_positive` | TEXT JSON | Positive findings | Populated at completion | `["onset: 3 days"]` |
| `pertinent_negative` | TEXT JSON | Denied findings | Populated at completion | `["fever"]` |
| `model_version` | TEXT | Intake pipeline/schema version | Defaults to `v1.1.0` | `v1.1.0` |
| `status` | TEXT | Lifecycle state | `active`, `completed`, `reviewed` | `completed` |
| `modified_at` | DATETIME | Last modification time | Updated on state/status writes | `2026-04-19 08:38:12` |
| `patient_age` | INTEGER | Patient age in years | Required at session start | `35` |
| `patient_sex` | TEXT | Patient sex | Used by sex-gated questions | `female` |
| `escalation_level` | TEXT | Highest acuity raised | `none`, `same_day_clinician_review`, `priority_clinician_review`, `urgent_escalation`, `immediate_alert` | `urgent_escalation` |
| `extracted_state` | TEXT JSON | Snapshot of captured fields | Written throughout/completion | `{"onset":"3 days"}` |

## Table — Turn (SQL: turns)

| Column | Type | Meaning | Allowed values / notes | Example |
|---|---|---|---|---|
| `turn_id` | INTEGER PK | Auto-incrementing row id | Unique DB-wide | `42` |
| `session_id` | INTEGER FK | Links to `encounters.id` | ON DELETE CASCADE | `1` |
| `time_of_message` | DATETIME | Time turn was recorded | Defaults to `CURRENT_TIMESTAMP` | `2026-04-19 08:31:15` |
| `speaker` | TEXT | Message speaker | `system` or `patient` | `system` |
| `message` | TEXT | Raw message text | Question text or answer text | `When did it start?` |
| `question_id` | TEXT | Question id that drove turn | NULL only for free text | `onset` |
| `phase` | TEXT | Intake phase | `opening`, `core_characterization`, `high_priority_followup`, `ros`, `context_and_history`, etc. | `core_characterization` |

## Table — Summary (SQL: summaries)

| Column | Type | Meaning | Allowed values / notes | Example |
|---|---|---|---|---|
| `session_id` | INTEGER PK/FK | Links to `encounters.id` | One summary per session | `1` |
| `pre_summary` | TEXT | Deterministic template summary | Generated from extracted state | `Chief Complaint...` |
| `ai_summary` | TEXT | AI-drafted HPI paragraph | Anthropic, Ollama, or fallback | `The patient presents...` |
| `post_summary` | TEXT | Clinician-edited final | NULL until review | `Patient is...` |
| `reviewed_at` | DATETIME | Clinician review time | NULL until reviewed | `2026-04-19 09:15:00` |

## Table — SessionMetric (SQL: session_metrics)

| Column | Type | Meaning | Computed? | Example |
|---|---|---|---|---|
| `session_id` | INTEGER PK/FK | Links to encounter | Yes | `1` |
| `patient_turn_count` | INTEGER | Number of patient turns | Yes | `9` |
| `system_turn_count` | INTEGER | Number of system turns | Yes | `9` |
| `required_fields_total` | INTEGER | Required fields in active profile | Yes | `22` |
| `required_fields_filled` | INTEGER | Required fields with meaningful values | Yes | `19` |
| `completion_rate` | REAL | Filled/total | Yes | `0.864` |
| `missing_fields_count` | INTEGER | Missing clarification count | Yes | `3` |
| `missing_fields` | TEXT JSON | Missing field names | Yes | `["radiation"]` |
| `summary_length` | INTEGER | Pre-summary character count | Yes | `1280` |
| `similarity_ratio` | REAL | AI-vs-post summary similarity | Stub until clinician review loop | `0.0` |
| `major_edit_flag` | INTEGER | 1 if post-summary differs substantially | Stub | `0` |
| `clinician_acceptance` | INTEGER | 1 if post_summary exists | Stub | `0` |
| `hallucination_flag_count` | INTEGER | AI-introduced ungrounded content count | Stub | `0` |
| `hallucination_notes` | TEXT JSON | Hallucination notes | Stub | `[]` |

## Table — SchemaVersion (SQL: schema_version)

| Column | Type | Meaning | Example |
|---|---|---|---|
| `version` | TEXT PK | Applied schema version | `v1.1.0` |
| `applied_at` | DATETIME | Time bootstrapped | `2026-04-19 08:29:50` |

## Prototype Summary Template

The template-rendered pre-summary is assembled by `summary_engine.format_summary_text()` from the structured output of `generate_template_summary()`. It never invents information.

### Sections, in order

1. Patient demographics.
2. Chief Complaint (Primary).
3. Other Concerns.
4. HPI.
5. Review of Systems (ROS).
6. Pertinent Positives.
7. Pertinent Negatives.
8. PMH / PSH.
9. Medications.
10. Allergies.
11. Social Factors.
12. Family History.
13. Gynecologic History when captured.
14. Immunization History when captured.
15. Missing Clarifications.
16. Flags.
17. Escalation Level.

## AI Summary Flow

The AI HPI is optional. The app always produces the template summary first.

1. If `ANTHROPIC_API_KEY` is present, `summary_engine.ai_summarize()` calls Anthropic Messages API.
2. If Anthropic is unavailable, it calls local Ollama using `OLLAMA_URL` and `OLLAMA_MODEL`.
3. If both fail, it returns the template HPI.

Environment variable example:

```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

## ROS Display Systems

| Display system | High-yield examples |
|---|---|
| Constitutional | fever, chills, night sweats, fatigue, weight loss |
| Cardiovascular | chest pain, palpitations, orthopnea, leg swelling |
| Respiratory | shortness of breath, cough, hemoptysis, wheeze |
| Gastrointestinal | abdominal pain, nausea, vomiting, diarrhea, constipation, blood in stool |
| Genitourinary | dysuria, frequency, hematuria, flank pain, vaginal symptoms |
| Neurological | headache, dizziness, weakness, numbness, seizure, confusion |
| Musculoskeletal | joint pain, muscle pain, back pain, swelling, stiffness |
| Skin | rash, itching, lesions, bruising, blistering |
| Endocrine | heat intolerance, cold intolerance, excessive thirst/urination/hunger |
| Hematologic or Lymphatic | easy bruising, easy bleeding, lymph node swelling |
| Psychiatric | anxiety, depression, mood changes, sleep disturbance |

## How ROS is Conducted

The runtime does not use UMLS expansion. ROS is deterministic and selected from `ros_question_bank.json`.

### ROS selection pipeline

1. Resolve priority systems from `targeted_ros_plan` when present.
2. Fall back to `question_budget.ros_mode.pathological_system`, `primary_system`, and `related_systems`.
3. Partition ROS bank into priority and secondary systems.
4. Order by display system, clinical priority, and stable question id.
5. Return one body-system batch at a time.
6. Apply field/code/dedup-family skip logic before asking.
7. Continue to the next system block if ROS budget remains.

## Concept Dedup

ROS owns universal `dedup_family` values such as `ros:vomiting`, `ros:shortness_of_breath`, and `ros:fever`. Complaint and module questions map to these families when they cover the same review-of-systems concept.

Secondary complaint dedup uses exact `field` and `code` first, then suppresses repeated parent symptoms by dedup family. ROS uses stricter dedup because it runs after complaints and modules.

## Escalation Rules

Escalation rules are shared condition trees in `shared_v2.json`. They evaluate against accumulated session state after every complaint, ROS, or module answer.

Example:

```json
{
  "meningitis_screen": {
    "escalation_level": "immediate_alert",
    "condition": {
      "op": "all",
      "conditions": [
        {"field_ref": "$state.fever", "op": "field_equals", "value": "yes"},
        {"op": "any", "conditions": [
          {"field_ref": "$state.neck_stiffness", "op": "field_equals", "value": "yes"},
          {"field_ref": "$state.photophobia", "op": "field_equals", "value": "yes"},
          {"field_ref": "$state.confusion", "op": "field_equals", "value": "yes"}
        ]}
      ]
    }
  }
}
```

Escalation only upgrades along: `none` → `same_day_clinician_review` → `priority_clinician_review` → `urgent_escalation` → `immediate_alert`.

## Keeping This Codebook in Sync

Update this document when:

1. The `SCHEMA` constant in `db_manager.py` changes.
2. `summary_engine.generate_template_summary()` or `format_summary_text()` changes output sections.
3. `ros_question_bank.json` changes display systems or dedup families.
4. `shared_v2.json` changes escalation rules, ask/skip predicates, or guardrails.
5. The summary provider order changes.
