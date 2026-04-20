# Clinical Intake Runtime — v1.0.0

Deterministic symptom-elicitation engine for ED/acute clinical intake. Takes a patient through a structured complaint-driven dialogue (HPI → early danger screen → characterization → red-flag followup → context/history → ROS → history modules) and produces a clerking-ready summary.

## Release

**Version 1.0.0** — Atomic symptom model. Every clinical finding has exactly one canonical field name used identically across complaint files, the ROS bank, red-flag patterns, history modules, and the summary engine. `field == canonical_concept` everywhere. See `CHANGELOG.md` for the full migration story.

## Directory layout

```
complaints_modules/
├── shared_v2.json              # Global contract: ask_if_registry, skip_if_registry, tone rules
├── ros_question_bank.json      # Review-of-systems atomic questions, by system
├── index_v2.json               # Complaint index + routing metadata
├── <complaint>_v2.json         # 26 complaint files (abdominal_pain, back_pain, ...)
├── modules/                    # Optional subdirectory for history modules in packaged deployments
│   ├── pmh_psh_module.json     # Past medical/surgical history module
│   ├── drug_history_module.json# Medications + allergies module
│   ├── social_family_history_module.json
│   ├── gynecologic_history_module.json
│   └── immunization_history_module.json
└── (or place those module JSON files directly under complaints_modules/ in flat deployments)

app/engine/
├── intake_engine.py            # Complaint-phase runner (HPI → danger → followup → history)
├── ros_runner.py               # Review-of-systems runner
├── module_runner.py            # History-module runner
├── summary_engine.py           # Builds the AI clerking summary
├── utils.py                    # Condition evaluator, state helpers
├── validator.py                # Invariant checker
├── db_manager.py               # SQLite persistence
├── main.py                     # FastAPI entrypoints
└── streamlit_app.py            # Streamlit UI for demo/testing
```

## Architecture principle

**One concept, one field name, everywhere.** A patient is never asked about the same clinical finding twice in a session. Dedup is a one-liner: `if state.get(q.field) is set, skip`.

This means:

- No `concept_alias_map` traversal at dedup time.
- No `clinical_cluster_map` to collapse overlapping compounds.
- No `covered_concepts` list to track which ideas have been screened.

All of that complexity existed to paper over compound questions. Compound questions are gone.

## Core abstractions

### Atomic symptom

A single clinical finding (`fever`, `chest_pain`, `hematuria`). Has a canonical field name that IS its canonical concept. Asked with a self-contained BOOLEAN-with-optional-details question.

### Linker atomic

A qualifier variant of a root atomic that carries clinical meaning in its own right. Example: `pleuritic_chest_pain` is a distinct clinical finding, not "chest_pain + pleuritic qualifier". Linkers have `ask_if` gating on the root atomic being positive. When a linker is answered positive, the engine **auto-sets the root atomic to positive** too, preserving dedup correctness across phases.

### Red-flag pattern

A list of atomic field names that must ALL be positive for the pattern to fire. Example: `meningitis_pattern: [fever, headache, neck_stiffness]`. No compound shortcuts.

### Schedule phases (per complaint)

`opening → core_characterize → early_danger_screen → extended_characterize → critical_followup → high_priority_followup → context_and_history`. Each phase is an ordered list of field IDs; the engine walks them, skipping anything already in state.

### History modules (run after complaint phase)

PMH/PSH, drugs + allergies, social/family, gynecologic (conditional), immunization (conditional). Each is an independent schedule with its own `field_order`. Module questions use uniform canonical field names: `past_medical_history`, `past_surgical_history`, `current_medications`, `allergies`, `family_history`, `lmp`, `smoking_current`, `alcohol_current`, etc.

## Session flow

```
1. Patient narrative (opening)
2. Complaint runner walks schedule phases in order
   — skip any field already in state
   — on positive answer: check red-flag patterns, queue detail follow-up, run linker auto-set
3. ROS runner reads targeted_ros_plan when present; otherwise it derives the ROS plan from primary_system + related_systems, then picks N atomic screens from the bank and skips any field already in state
4. Module runner runs PMH/PSH, drugs, social, gyn (if SEX_FEMALE), immunization (if indicated)
5. Summary engine assembles the clerking note from state
```

## Key invariants (validated at build time)

1. Every field in every schedule phase resolves in that complaint's `questions_by_id`.
2. Every field in every red-flag pattern resolves in `questions_by_id`.
3. No compound field name (containing `_or_`, `_and_`, compound BOOLEAN text screening 2+ concepts) appears anywhere.
4. Every `questions_by_id` entry has `canonical_concept == field` (detail rows have `canonical_concept == parent_field`).
5. Every `parent_field` reference resolves to an atomic.
6. No routine-flow safeguarding question fires — all gated by specific clinical context.
7. LMP uses canonical phrasing gated by `SEX_FEMALE_REPRODUCTIVE_AGE`.
8. All 41 JSON files declare `version: "1.0.0"`.

Run `python -m app.engine.validator` to verify.

## Safeguarding policy

Safeguarding questions are **gated, not routine**. Current gating:

- `trauma_v2.json`: fires when `mechanism=assault`, assault-related text detected, or patient age ≤ 17.
- `loss_of_consciousness_v2.json`: fires when drug-facilitated LOC is suspected or patient age ≤ 17.
- Removed entirely from `vaginal_discharge_v2.json` routine flow.

When it fires, the phrasing is sensitive and explicitly framed as an opening the patient can decline.

## Social history

- `smoking_current` always asked → detail captures quantity in patient-friendly language (no pack-year math).
- `smoking_past` asked only if current = no.
- `alcohol_current` always asked → detail captures amount in a usual week.
- `recreational_drug_use` gated behind specific clinical red flags (cardiac/neuro/seizure contexts); sensitively phrased.
- `cocaine_or_stimulant_use` — removed as routine.

## Running the system

```bash
# Install deps
pip install -r requirements.txt

# Validate data integrity
python -m app.engine.validator

# Run the Streamlit demo UI
streamlit run app/ui/streamlit_app.py

# Run the FastAPI backend (main.py)
uvicorn app.engine.main:app --reload --port 8000

# Run tests
pytest tests/
```

## File of record

- `CHANGELOG.md` — release history, migration notes, retired field names
- `ARCHITECTURE.md` — detailed architecture and design decisions
- `migration_map.json` — compound → atomic field mapping (historical reference)
- `audit_v1_0_0.json` / `phase2_audit.json` / `phase3_audit.json` — per-file migration audit trails
