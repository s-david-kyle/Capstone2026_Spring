# A Human-Centered AI System for Structured Symptom Collection and Diagnosis Support

A clinical triage and intake system for high-stress, resource-constrained care settings — built to help patients in underserved communities describe their symptoms clearly and completely, while giving clinicians structured information for faster, more confident review.

Developed as a graduate capstone for the Master of Data Science program at the University of Arizona, in collaboration with the [CoDiRA initiative](https://news.arizona.edu/news/healthcare-powered-ai-guided-human-and-community-insight) (Convergent Digital Health for Remote Access), a University of Arizona Big Idea Challenge–funded research program building AI-powered medical access for underserved and rural communities.

---

## The Problem

Emergency and urgent care settings place extreme demands on clinicians: high patient volume, short time per encounter, and growing documentation requirements. The clinical history — the single most important diagnostic instrument a clinician has — is routinely rushed or fragmented under these conditions.

Existing tools offer single-turn diagnostic responses. Real clinical encounters require multi-turn, conversational structure: a system that knows what to ask next based on what was just answered, catches dangerous symptom combinations across the full session, and leaves the clinician a structured, reviewable record rather than a freeform transcript.

---

## Two Complementary Approaches

This project explored two distinct pathways to the same goal. Both produce a structured clinical picture without replacing clinical judgment. Their key takeaway: **clinician-written logic improves safety and consistency, while the knowledge graph adds adaptive exploration and transparent reasoning. The next step is integrating both into one workflow.**

---

### Approach 1: Dynamic Knowledge Graph + LLM

A patient-facing conversational system that lets the patient's own words build a structured clinical picture turn by turn. As the patient responds, the system extracts clinical keywords using a local LLM, maps them to validated UMLS medical vocabulary, and builds a dynamic knowledge graph that ranks symptoms by biological system and relationship type. A symptom or system must rank at the top across three consecutive turns before it commits — preventing premature narrowing.

The clinician-facing interface displays a structured summary of the conversation alongside the knowledge graph, allowing drill-down into the reasoning path that connected the patient's history to the surfaced symptom candidates. At each turn, ranked symptom candidates are persisted to a local SQLite database so the full diagnostic trajectory is recoverable for review.

**Stack:** Streamlit · local LLM (Gemma 3) · UMLS API · NetworkX · yFiles · SQLite

---

### Approach 2: Clinician-Driven Intake Engine

A deterministic, schema-driven intake engine in which every question, skip condition, gating predicate, and escalation rule is defined explicitly in versioned configuration files authored by clinicians — no learned dialogue policy, no prompt-dependent behavior. The engine evaluates red-flag combinations across accumulated session state after every answer and escalates monotonically: once a danger level is triggered, it cannot be lowered within a session.

An optional LLM summarization layer accepts the structured record as input and produces a readable clinical narrative paragraph. The LLM is downstream of structured capture — it refines readability, it does not determine what was captured. The deterministic record is always the source of truth.

The design pivot from a fully generative patient-facing engine to a deterministic one was driven by three observed failure modes during prototyping: inconsistent question selection across runs of the same case, occasional sex- or age-inappropriate questions even when demographic context was present, and repeated concepts captured under different field names — making downstream summarization noisy. Moving question logic into explicit, reviewable configuration addresses all three at the architectural level rather than the prompt-engineering level.

**Stack:** Streamlit · FastAPI · Python · SQLite · Anthropic Claude API · Ollama (local fallback)

| Component | Purpose |
|---|---|
| Streamlit interface | Patient-facing intake UI; demographics, complaint selection, responses |
| FastAPI backend | Session management, question flow control, answer storage |
| Deterministic intake engine | Complaint-specific question delivery, skip logic, gating, escalation |
| Complaint JSON files | Versioned configuration defining questions, codes, phases, escalation rules |
| Shared clinical registry | Canonical field names, codes, deduplication families, gating predicates |
| ROS runner | Review-of-systems questioning in body-system batches after HPI |
| Module runner | PMH/PSH, medications, social/family history, gynecologic history |
| SQLite store | Encounters, turns, summaries, extracted state, session metrics |
| Summary engine | Deterministic template summary + optional AI-refined HPI via Claude or Ollama |

The summarization layer supports both remote (Anthropic API) and local (Ollama) inference, so institutions whose data governance policies preclude sending clinical content to external services can use the local path without losing the summarization capability.

---

## Team

Brandon Knox · David Kyle · Kennedy Erele Okhawere · Sree Paada Reddy Pallikila · Partha Vemuri

**Faculty Advisor:** Dr. Rozhin Yasaei, University of Arizona College of Information Science

**Academic Program:** Master of Data Science, University of Arizona, Capstone 2025–2026

**Research Context:** [CoDiRA — Convergent Digital Health for Remote Access](https://news.arizona.edu/news/healthcare-powered-ai-guided-human-and-community-insight), University of Arizona Big Idea Challenge
