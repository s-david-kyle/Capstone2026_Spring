# Architecture — v1.1.0

## Overview

The Clinical Intake Runtime v1.1.0 is a deterministic clerking application with an optional AI summary layer. The system collects structured patient answers, prevents repeated questions through shared dedup logic, batches ROS by body system, evaluates escalation rules from accumulated state, and renders both template and AI summaries.

## Main components

| Component | Path | Purpose |
|---|---|---|
| Streamlit UI | `app/ui/streamlit_app.py` | Patient-facing/test interface, question rendering, ROS batch answer entry, summaries, and extracted-state display. |
| FastAPI backend | `app/api/main.py` | Session lifecycle, answer submission, ROS/module orchestration, completion, and summary endpoints. |
| Complaint engine | `app/engine/intake_engine.py` | Deterministic complaint question scheduling, skip logic, dedup tracking, and escalation evaluation. |
| ROS runner | `app/engine/ros_runner.py` | Selects ROS questions by complaint system priority and returns one body-system batch at a time. |
| Module runner | `app/engine/module_runner.py` | Runs PMH/PSH, drug/allergy, social/family, gynecologic, and immunization modules. |
| Summary engine | `app/engine/summary_engine.py` | Builds deterministic template summary and optionally calls Anthropic or Ollama for AI HPI. |
| Database layer | `app/db/db_manager.py` | Raw SQLite persistence for encounters, turns, summaries, metrics, and schema version. |
| Shared contracts | `complaints_modules/shared_v2.json` | Canonical codes, aliases, predicates, escalation rules, and guardrails. |
| ROS bank | `complaints_modules/ros_question_bank.json` | ROS questions, display systems, and ROS-owned dedup families. |

## Runtime flow

1. User starts a session with primary complaint, age, sex, and optional secondary complaint.
2. The backend loads shared, index, complaint, and module configuration.
3. The complaint engine asks core, danger, targeted, and closeout questions according to `question_phase_map`.
4. Secondary complaint logic uses field/code dedup first and suppresses only repeated parent-symptom families.
5. ROS runs after complaint/module phases and suppresses any ROS family already covered by complaint or module questions.
6. Escalation rules evaluate after complaint, ROS, and module answers.
7. Completion writes extracted state and summary artifacts to SQLite.
8. The UI displays the template summary, AI summary, and clinician-editable summary.

## Dedup model

- `field` prevents exact duplicate data capture.
- `code` prevents duplicate canonical questions across files.
- `dedup_family` is ROS-owned and prevents repeated generic ROS review.
- `question_role` controls whether a complaint/secondary question is a parent symptom, qualifier, red flag, or context question.

## Escalation model

Escalation rules are defined in `shared_v2.json` as condition trees over accumulated session state. Rules can be complaint-specific or global. Escalation only upgrades acuity; it never downgrades.

## Summary providers

The deterministic template summary is always available. The AI summary attempts Anthropic first when `ANTHROPIC_API_KEY` is set, then local Ollama, then falls back to the template HPI.
