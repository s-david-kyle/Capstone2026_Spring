# Architecture — v1.0.0

## Design goals

1. **Deterministic question selection.** Given the same patient state, the engine always picks the same next question. No LLM in the control loop — LLMs are used only for narrative extraction and summary generation.
2. **One canonical name per clinical concept.** Prevents re-asking the same finding under different labels across complaint phase, ROS phase, and history modules.
3. **Data-first.** Clinical logic lives in JSON files authored by clinicians. Runtime code is a small deterministic interpreter.
4. **Auditable dedup.** No opaque alias-collapse behaviour. If `state[field]` is set, the question is skipped. That's the entire rule.

## Data model

### Atomic symptom

```json
{
  "field": "fever",
  "phase": "early_danger_screen",
  "text": "Any fever?",
  "response_type": "BOOLEAN_WITH_OPTIONAL_DETAILS",
  "options": ["yes", "no"],
  "detail_field": "fever_details",
  "capture_detail_if_positive": true,
  "if_positive_ask": ["fever_details"],
  "canonical_question_key": "fever",
  "canonical_concept": "fever",
  "clinical_priority": "high"
}
```

The rule: **`field == canonical_concept`**, always. The detail row for `fever_details` has `parent_field: "fever"` and `canonical_concept: "fever"` (detail inherits parent's concept).

### Linker atomic (qualifier)

A linker is a full clinical finding on its own that depends on a root atomic being positive:

```json
{
  "field": "pleuritic_chest_pain",
  "text": "Any sharp chest pain that is worse when you breathe in or cough?",
  "ask_if": {
    "op": "field_equals",
    "field_ref": "$state.chest_pain",
    "value": "yes"
  }
}
```

**Engine behaviour on positive linker answer:** the engine inspects `ask_if`. If the gate is a simple `field_equals` on `$state.<parent>` with `value: "yes"`, then on a positive answer to the linker, the engine also sets `state[parent] = "yes"`. This guarantees that a later generic ROS screen for the parent will be suppressed.

### Red-flag pattern

```json
"meningitis_pattern": ["fever", "headache", "neck_stiffness"]
```

A list of atomic field names. Pattern fires (escalation triggered) when ALL listed fields have positive answers in state. No compound shortcuts — each condition is independently captured.

### Question schedule

Per complaint, organised by profile and phase:

```json
"question_schedule": {
  "enforced_phase_order": [
    "opening", "core_characterize", "early_danger_screen",
    "extended_characterize", "critical_followup",
    "high_priority_followup", "context_and_history"
  ],
  "default_profile": {
    "opening": ["presenting_complaint_narrative"],
    "core_characterize": ["onset", "duration", "character"],
    "early_danger_screen": ["fever", "rigors", "severe_constant_pain"]
  }
}
```

Schedules are lists of field IDs. The engine walks them in order, resolves each to the full question via `questions_by_id[fid]`, and applies skip rules.

### Skip pipeline

For each candidate question, the engine evaluates in order:

1. `FIELD_ALREADY_CAPTURED` — if `state[field]` is set (and not empty or `not_assessed`), skip. This is the v1.0.0 dedup rule.
2. `skip_if` rules — declarative conditions from the question or from `skip_if_registry`.
3. `ask_if` gate — if present, must evaluate true. Used for sex gating, age gating, and linker parent-positive gating.

## Runtime components

### `intake_engine.IntakeEngine`

Drives the complaint phase. Owns `self.state`, `self.questions`, `self.turns`. Key methods:

- `get_next_question()` — advances through the schedule, applying the skip pipeline.
- `record_answer(qid, field, answer, phase)` — writes to state, checks red flags, runs linker auto-set, queues detail follow-up.
- `_parent_from_ask_if(ask_if)` — extracts the linker parent from a simple `ask_if` gate. Returns `None` for sex/age gates or complex `any/all` conditions.

### `ros_runner.ROSRunner`

Reads `targeted_ros_plan.high_yield_systems` from the complaint, partitions the ROS bank by system, sorts by `display_system` order + `clinical_priority`. Iterates priority pool first, then cross-system pool. Dedup is the trivial `if state[field] set, skip`.

### `module_runner.ModuleRunner`

Runs one of the five history modules. Reads `activation_rules` to decide whether the module applies (e.g., gynecologic is `SEX_FEMALE` only). Obeys `session_cap_questions` and `load_once_per_session`.

### `summary_engine.SummaryEngine`

Assembles the clerking note from `state`. Uses a hardcoded ordered field list that covers the canonical atomic names plus module fields. Outputs HPI, past medical, medications, allergies, social, family, LMP (if set), and ROS sections.

### `utils.evaluate_condition`

Evaluates `ask_if` / `skip_if` condition objects. Supports ops: `field_equals`, `field_not_equals`, `field_contains`, `field_text_contains_any`, `field_exists_and_not_null`, `field_exists_and_below`, `field_above`, `field_below`, `any`, `all`, plus registered composite conditions from `shared_v2.ask_if_registry` / `skip_if_registry`.

## Why the atomic model

The v2.x model used compound fields like `fever_or_rigors`, `fever_or_meningism`, `hematemesis_or_melena` to save schedule slots. The failure mode: the same patient was asked about fever four different ways across the complaint phase and ROS, because each compound was a different `field` and state didn't recognise the overlap. The v2 rescue was an alias-map + cluster-map that made "fever_or_rigors positive" count as "fever covered" — fragile, hard to reason about, and the source of the bad session transcripts.

v1.0.0 fixes this at the data level: split every compound into atomics, let schedule phases ask each atomic once, let dedup be a field lookup. The alias map still exists (for future extraction-time synonyms like "pins and needles" → `tingling`) but is not used for dedup.

## Extension points

- **Patient-clinician lexicon** (planned): a `patient_clinician_lexicon.json` file mapping lay terms to canonical atomics for the extraction layer. Not needed for the runtime; extraction can ship synonyms independently of the atomic registry.
- **New complaints**: add `<name>_v2.json` following the existing schema. `validator.py` will catch invariant violations.
- **New modules**: add `<name>_module.json` with `activation_rules` if conditional. `ModuleRunner` handles the rest.
- **New ROS atomics**: add to `ros_question_bank.json` with the correct `system` / `display_system` / `clinical_priority`. Any complaint whose `targeted_ros_plan.high_yield_systems` matches will pick them up.
