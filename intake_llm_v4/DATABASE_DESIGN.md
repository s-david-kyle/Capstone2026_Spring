# Database Design

## Overview

The system uses a local SQLite database for persistent storage of encounters, turns, summaries, and metrics. SQLite was chosen because:

- Zero configuration – no separate database server.
- Single file – easy to back up, move, or delete.
- ACID compliant – safe for concurrent access by the API.
- No ORM – direct SQL gives full control over performance and schema.

## Schema

### Table `encounters`

| Column                  | Type                | Description                                       |
| ----------------------- | ------------------- | ------------------------------------------------- |
| `id`                  | INTEGER PRIMARY KEY | Auto‑incrementing session ID                     |
| `session_name`        | TEXT UNIQUE         | Human‑readable name (timestamp + complaint)      |
| `created_at`          | TIMESTAMP           | Session start time                                |
| `ended_at`            | TIMESTAMP           | Completion time                                   |
| `primary_complaint`   | TEXT                | Complaint ID (e.g.,`abdominal_pain`)            |
| `secondary_complaint` | TEXT                | JSON array of secondary complaints (unused in v1) |
| `pertinent_positive`  | TEXT                | JSON array of positive findings (from summary)    |
| `pertinent_negative`  | TEXT                | JSON array of negative findings                   |
| `model_version`       | TEXT                | Version of the engine                             |
| `status`              | TEXT                | `active`, `completed`, `reviewed`           |
| `modified_at`         | TIMESTAMP           | Last update time                                  |
| `patient_age`         | INTEGER             | Age at encounter                                  |
| `patient_sex`         | TEXT                | `male` or `female`                            |
| `escalation_level`    | TEXT                | From `shared_v2.json` escalation tiers          |
| `extracted_state`     | TEXT                | JSON object of all captured field‑value pairs    |

**Indexes:** `status`, `created_at`

### Table `turns`

| Column              | Type                | Description                          |
| ------------------- | ------------------- | ------------------------------------ |
| `turn_id`         | INTEGER PRIMARY KEY | Auto‑increment                      |
| `session_id`      | INTEGER             | Foreign key to `encounters.id`     |
| `time_of_message` | TIMESTAMP           | When the turn occurred               |
| `speaker`         | TEXT                | `system` or `patient`            |
| `message`         | TEXT                | The question text or patient answer  |
| `question_id`     | TEXT                | The field name (e.g.,`onset`)      |
| `phase`           | TEXT                | Which phase the question belonged to |

**Indexes:** `session_id`, `question_id`

### Table `summaries`

| Column           | Type                | Description                      |
| ---------------- | ------------------- | -------------------------------- |
| `session_id`   | INTEGER PRIMARY KEY | Foreign key to `encounters.id` |
| `pre_summary`  | TEXT                | Template summary (structured)    |
| `ai_summary`   | TEXT                | LLM‑generated HPI paragraph     |
| `post_summary` | TEXT                | Clinician‑edited final summary  |
| `reviewed_at`  | TIMESTAMP           | When the clinician saved         |

### Table `session_metrics`

| Column                       | Type                | Description                                                             |
| ---------------------------- | ------------------- | ----------------------------------------------------------------------- |
| `session_id`               | INTEGER PRIMARY KEY | Foreign key to `encounters.id`                                        |
| `patient_turn_count`       | INTEGER             | Number of patient answers                                               |
| `system_turn_count`        | INTEGER             | Number of system questions                                              |
| `required_fields_total`    | INTEGER             | Total questions in required phases                                      |
| `required_fields_filled`   | INTEGER             | How many of those were answered                                         |
| `completion_rate`          | REAL                | `filled / total`                                                      |
| `missing_fields_count`     | INTEGER             | Count of unanswered required questions                                  |
| `missing_fields`           | TEXT                | JSON array of missing field names                                       |
| `summary_length`           | INTEGER             | Length of `pre_summary` in characters                                 |
| `similarity_ratio`         | REAL                | Reserved for future (similarity between pre and post)                   |
| `major_edit_flag`          | INTEGER             | Whether clinician made substantial edits                                |
| `clinician_acceptance`     | INTEGER             | 0 = not accepted, 1 = accepted without changes, 2 = accepted with edits |
| `hallucination_flag_count` | INTEGER             | Number of possible AI hallucinations (Phase 3)                          |
| `hallucination_notes`      | TEXT                | JSON array of hallucination descriptions                                |

## Rationale for design choices

- **No ORM** – Keeps dependencies minimal and avoids SQLAlchemy’s complexity. All queries are parameterised raw SQL.
- **JSON fields** – `extracted_state`, `missing_fields`, `hallucination_notes` are stored as JSON for flexibility. They can be queried using SQLite’s `json_extract` if needed.
- **Separate metrics table** – Avoids cluttering the main `encounters` table with analytical fields that are not needed for daily operation.
- **`session_name` unique** – Allows easy lookup by human‑readable identifier.

## Backup and restore

The entire database is a single file (`data/clinical_intake.db`). To back up:

```bash
cp data/clinical_intake.db backups/clinical_intake_$(date +%Y%m%d).db
```
