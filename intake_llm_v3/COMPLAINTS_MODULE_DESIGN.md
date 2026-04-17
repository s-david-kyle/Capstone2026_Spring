```

# Complaints & Module Design Document

## Overview

The clinical intake system is entirely driven by JSON rule files. This design allows non‑programmers to define complaint‑specific question flows, red‑flag patterns, escalation logic, and history modules. The engine is deterministic and auditable.

## File Types

### 1. Complaint files (`complaints/*_v2.json`)

Each complaint defines:

- **`question_budget`** – min, target, max questions for primary and secondary modes.
- **`question_schedule`** – phases (`opening`, `core_characterize`, `early_danger_screen`, …) and which questions belong to each phase. Multiple profiles (e.g., `default_profile`, `chronic_low_severity_profile`) allow different flows based on patient answers.
- **`profile_switch_rules`** – conditions (e.g., duration ≥4 weeks AND severity <6) to switch profiles.
- **`questions_by_id`** – the actual questions with their text, response type, skip_if, ask_if, and canonical concepts.
- **`derived_red_flag_patterns`** – combinations of answers that trigger clinical red flags and escalation.
- **`summary_contract`** – defines which phases contribute to “missing clarifications”.

### 2. Module files (`modules/*.json`)

Modules are reusable history blocks. Each module contains:

- **`questions`** – list of questions with their text, response type, and skip/ask rules.
- **`field_order`** – the order to ask questions.
- **`session_cap_questions`** – per‑module question limit.
- **`activation_rules`** – for conditional modules (e.g., gynecologic module only if female and complaint is gynaecological).

Modules are executed after the primary complaint in the order defined in `MODULE_ORDER`.

### 3. Shared configuration (`shared_v2.json`)

Contains:

- **`concept_dedup_map`** – maps multiple field names to a single canonical concept (e.g., `fever`, `fever_or_rigors` → `fever_present`). The engine skips a question if its canonical concept was already answered.
- **`ask_if_registry`** – reusable conditions (e.g., `SEX_FEMALE_REPRODUCTIVE_AGE`).
- **`skip_if_registry`** – reusable skip rules (e.g., `DURATION_BELOW_4_WEEKS`).
- **`escalation_tiers`** – defines escalation levels and their priorities.
- **`authoritative_module_order`** – the sequence of module execution.
- **`session_guardrails`** – global session question cap (55).

### 4. ROS bank (`ros_question_bank.json`)

A central repository of Review of Systems questions, each tagged with a clinical priority (high/medium/low) and a system. The engine uses the complaint’s `targeted_ros_plan` to select appropriate ROS questions after the complaint.

### 5. Index file (`index_v2.json`)

Lists all active complaints and which conditional modules they may trigger (e.g., `abdominal_pain` may trigger `gynecologic_history_module`).

## Engine Behaviour

### Question Selection

1. The engine starts with the `default_profile` and follows the `enforced_phase_order`.
2. For each phase, it iterates through the listed question IDs.
3. Before asking a question, it evaluates:
   - `skip_if` rules (including `FIELD_ALREADY_CAPTURED`, `DURATION_BELOW_4_WEEKS`, etc.)
   - `ask_if` conditions (e.g., only ask pregnancy questions if female and age 12‑55)
   - Concept deduplication – if the question’s `canonical_concept` was already answered in any earlier question (including other complaints or modules), it is skipped.
4. After each answer, it re‑evaluates `profile_switch_rules` and may change the current profile.
5. When the complaint schedule is exhausted, it hands over to the `ModuleRunner`.

### Module Runner

- Loads modules in the order defined by `MODULE_ORDER`.
- For conditional modules, it checks whether the complaint’s `conditional_session_modules` (from `index_v2.json`) includes the module.
- Each module has its own question cap (`session_cap_questions`).
- After all modules, it asks the `final_closeout_question` from `shared_v2.json`.

### Escalation

- Whenever a question answer matches a `derived_red_flag_pattern`, the engine adds the flag and updates the `escalation_level` based on keyword matching (e.g., “haemodynamic” → `immediate_alert`).
- The escalation level is stored in the database and displayed in the UI.

## Summary Generation

- **Template summary** – uses the complaint’s `summary_contract` to determine which phases contribute to “missing clarifications”. It lists all captured answers, red flags, and escalation.
- **AI summary** – sends the extracted state, pertinent positives/negatives, and red flags to Ollama (`llama3.1`) and returns a fluent HPI paragraph. Falls back to the template HPI if Ollama is unavailable.

## Database Schema

See `app/db/schema.sql`. Key tables:

- `encounters` – session metadata, extracted state, escalation level.
- `turns` – question‑answer pairs with speaker and phase.
- `summaries` – pre‑summary, AI summary, post‑summary (doctor edit).
- `session_metrics` – for analytics (completion rate, missing fields, etc.).

All database operations use raw SQLite3 – no ORM.

## Extending the System

- **Add a new complaint** – create a `complaints/new_complaint_v2.json` following the schema. Add it to `index_v2.json`.
- **Add a new module** – create a `modules/new_module.json` and include it in `MODULE_ORDER` (in code) if it should run for all complaints, or add it to `conditional_session_modules` for specific complaints.
- **Change escalation rules** – modify `derived_red_flag_patterns` in the complaint or edit `_update_escalation` in `intake_engine.py`.
- **Add a new operator** – extend `evaluate_condition` in `utils.py`.

The system is designed to be **clinician‑maintainable** without requiring code changes for routine content updates.
```
