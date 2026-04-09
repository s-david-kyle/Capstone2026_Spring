"""
generate_policy.py — Clinical intake policy generator
Outputs Python dicts ready to paste into complaint_policies.py.
Also drafts new target_specs entries for clinical review.

Usage:
    python generate_policy.py                        # interactive mode
    python generate_policy.py "Seizure"              # single complaint
    python generate_policy.py --batch                # all 12 Tier 1 complaints
    python generate_policy.py --provider openai "Fever"
"""

import re
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from intake_engine.config import API_KEYS

OUTPUT_DIR = Path(__file__).parent / "generated"

TIER1_COMPLAINTS = [
    "Nausea / Vomiting",
    "Fever",
    "Syncope / Fainting",
    "Palpitations",
    "Leg pain / swelling",
    "Urinary symptoms",
    "Cough",
    "Rash",
    "Altered mental status",
    "Seizure",
    "Eye pain / vision change",
    "Ear pain",
]

KNOWN_TARGETS = [
    "onset", "location", "duration", "severity", "timing", "course",
    "character", "aggravating_factors", "relieving_factors", "associated_symptoms",
    "medications", "allergies",
    "neurologic_symptoms", "visual_changes", "confusion_or_ams",
    "numbness_or_tingling", "head_trauma",
    "shortness_of_breath", "syncope_or_presyncope", "rapid_worsening",
    "chest_pain", "palpitations", "radiation", "nausea", "diaphoresis",
    "exertional_component", "leg_swelling", "orthopnea", "wheezing", "cough",
    "vomiting", "nausea_or_vomiting", "bloody_stool_or_melena",
    "diarrhea", "constipation", "last_oral_intake",
    "urinary_symptoms",
    "trouble_swallowing", "drooling", "voice_change", "sick_contacts",
    "sudden_severe_onset", "fever_or_neck_stiffness", "photophobia",
    "phonophobia", "aura_features", "exertional_trigger",
    "positional_component", "new_or_progressive_pattern",
    "medication_overuse_context",
    "bowel_or_bladder_changes", "recent_heavy_lifting",
    "pregnancy_or_postpartum_context",
    "fever",
]

SYSTEM_PROMPT = f"""You are a clinical informaticist and emergency medicine expert designing an AI intake system.

The system maps complaint policies to a registry of pre-defined targets (target_specs).
Each target defines a question, parse mode, and state path already implemented in code.

KNOWN TARGETS — use these exact names wherever clinically appropriate:
{json.dumps(KNOWN_TARGETS, indent=2)}

RULES:
1. Always prefer a known target over inventing a new one.
2. Only invent a new target if NO known target fits the clinical need.
3. For every new target invented, provide a full draft spec in "new_target_specs".
4. must_characterize MUST always include: onset, severity, duration, aggravating_factors, relieving_factors, associated_symptoms
5. Use snake_case for all target names.
6. Be medically accurate — red flags must reflect real emergency medicine triage criteria.
7. aliases should be natural phrases a patient might say to describe this complaint.
8. red_flags are human-readable escalation outcome labels, NOT target names.
9. min_required_characterization_count should be between 4 and 6 depending on complexity.

Existing policies for consistency:
- Headache: critical=[sudden_severe_onset, neurologic_symptoms, fever_or_neck_stiffness]
- Chest Pain: critical=[shortness_of_breath, syncope_or_presyncope, rapid_worsening]
- Abdominal Pain: critical=[vomiting, fever, bloody_stool_or_melena, pregnancy_or_postpartum_context]
- Shortness of Breath: critical=[chest_pain, rapid_worsening, syncope_or_presyncope]
- Dizziness: critical=[syncope_or_presyncope, neurologic_symptoms, chest_pain]
- Sore Throat: critical=[trouble_swallowing, drooling, voice_change]
- Back Pain: critical=[neurologic_symptoms, bowel_or_bladder_changes, fever]

DO NOT put these in critical_followups — they belong in high_priority_followups:
- medications, allergies, last_oral_intake, sick_contacts, recent_heavy_lifting
- Any musculoskeletal history or background context targets

DO NOT include the presenting complaint itself as a followup target.
DO NOT include duplicate or semantically redundant targets in the same section.

Target spec format for new targets:
{{
  "intent": "ask_<target_name>",
  "state_path": "policy_answers.<target_name>",
  "fallback_parse_mode": "yes_no",
  "question_mode": "deterministic",
  "question_text": "Plain English question to ask the patient.",
  "question_instruction": "Instruction for the LLM question generator.",
  "extraction_instruction": "Extract a boolean into set_fields under \\"policy_answers.<target_name>\\"."
}}

Return ONLY valid JSON. No markdown fences, no explanation."""

POLICY_PROMPT = """Generate a medically accurate clinical intake policy for: "{complaint}"

Return ONLY this JSON (no markdown fences):
{{
  "policy_name": "<snake_case_name>",
  "display_name": "{complaint}",
  "aliases": ["natural phrases a patient might say", "..."],
  "critical_followups": ["known targets only — red flag screening"],
  "must_characterize": ["onset", "severity", "duration", "aggravating_factors", "relieving_factors", "associated_symptoms"],
  "high_priority_followups": ["medications", "allergies"],
  "red_flags": ["human_readable_escalation_label", "..."],
  "wrap_up_rule": {{
    "type": "characterization_threshold",
    "require_all_critical": true,
    "required_characterization_targets": ["onset", "duration", "severity", "aggravating_factors", "relieving_factors", "associated_symptoms"],
    "min_required_characterization_count": 4
  }},
  "new_target_specs": {{}}
}}"""


def strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def generate_with_claude(complaint: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=API_KEYS["anthropic"])
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": POLICY_PROMPT.format(complaint=complaint)}]
    )
    text = strip_fences(response.content[0].text)
    if not text:
        raise ValueError("Empty response from API")
    return json.loads(text)


def generate_with_openai(complaint: str) -> dict:
    import openai
    client = openai.OpenAI(api_key=API_KEYS["openai"])
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": POLICY_PROMPT.format(complaint=complaint)}
        ]
    )
    text = strip_fences(response.choices[0].message.content)
    return json.loads(text)


def generate(complaint: str, provider: str = "anthropic") -> dict:
    print(f"  Generating '{complaint}' via {provider}...", end=" ", flush=True)
    policy = generate_with_claude(complaint) if provider == "anthropic" else generate_with_openai(complaint)
    print("done.")
    return policy


def policy_to_python(policy: dict) -> str:
    """Render a policy dict as a Python variable definition."""
    name = policy["policy_name"].upper() + "_POLICY"
    clean = {k: v for k, v in policy.items() if k != "new_target_specs"}

    lines = [f"{name} = {{"]
    for key, value in clean.items():
        if isinstance(value, list):
            if not value:
                lines.append(f'    "{key}": [],')
            else:
                lines.append(f'    "{key}": [')
                for item in value:
                    lines.append(f'        "{item}",')
                lines.append("    ],")
        elif isinstance(value, dict):
            lines.append(f'    "{key}": {{')
            for k, v in value.items():
                if isinstance(v, list):
                    if not v:
                        lines.append(f'        "{k}": [],')
                    else:
                        lines.append(f'        "{k}": [')
                        for item in v:
                            lines.append(f'            "{item}",')
                        lines.append("        ],")
                elif isinstance(v, bool):
                    lines.append(f'        "{k}": {str(v)},')
                elif isinstance(v, int):
                    lines.append(f'        "{k}": {v},')
                else:
                    lines.append(f'        "{k}": "{v}",')
            lines.append("    },")
        else:
            lines.append(f'    "{key}": "{value}",')
    lines.append("}")
    return "\n".join(lines)


def save_policy(policy: dict) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = policy["policy_name"]
    path = OUTPUT_DIR / f"{slug}.py"
    content = "\n".join([
        f'# Policy: {policy["display_name"]}',
        f'# Add {policy["policy_name"].upper()}_POLICY to COMPLAINT_POLICIES in complaint_policies.py',
        "",
        policy_to_python(policy),
    ])
    path.write_text(content)
    return path


def save_new_target_specs(all_new_specs: dict) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "new_target_specs_REVIEW.py"
    lines = [
        '"""',
        "DRAFT new target specs — review for medical accuracy before adding to:",
        "    intake_engine/policies/target_specs.py",
        '"""',
        "",
        "NEW_TARGET_SPECS = {",
    ]
    for target_name, spec in all_new_specs.items():
        lines.append(f'    "{target_name}": {{')
        for k, v in spec.items():
            escaped = str(v).replace('"', '\\"')
            lines.append(f'        "{k}": "{escaped}",')
        lines.append("    },")
    lines.append("}")
    path.write_text("\n".join(lines))
    return path


def report(policy: dict):
    new_specs = policy.get("new_target_specs", {})
    if new_specs:
        print(f"\n  *** {len(new_specs)} new target(s) needed ***")
        for name in new_specs:
            print(f"      - {name}")
    else:
        print(f"  No new targets needed.")


def main():
    args = sys.argv[1:]
    provider = "anthropic"
    batch = False
    complaint = None

    if "--provider" in args:
        idx = args.index("--provider")
        provider = args[idx + 1]
        args.pop(idx); args.pop(idx)

    if "--batch" in args:
        batch = True
        args.remove("--batch")

    if args:
        complaint = args[0]

    if provider == "openai" and not API_KEYS.get("openai"):
        print("ERROR: No OpenAI key set in intake_engine/config.py")
        sys.exit(1)

    if batch:
        print(f"\nBatch generating {len(TIER1_COMPLAINTS)} Tier 1 policies via {provider}...\n")
        all_new_specs = {}
        for c in TIER1_COMPLAINTS:
            try:
                policy = generate(c, provider)
                path = save_policy(policy)
                new_specs = policy.get("new_target_specs", {})
                all_new_specs.update(new_specs)
                n = len(new_specs)
                suffix = f" (+{n} new targets)" if n else ""
                print(f"  Saved -> {path}{suffix}")
            except Exception as e:
                print(f"  FAILED: {e}")

        print("\n--- Summary ---")
        if all_new_specs:
            specs_path = save_new_target_specs(all_new_specs)
            print(f"  {len(all_new_specs)} new target(s) drafted -> {specs_path}")
            print(f"  Review before adding to target_specs.py\n")
            for name in all_new_specs:
                print(f"    - {name}")
        else:
            print("  All policies used existing targets only.")
        print("\nDone.")

    elif complaint:
        try:
            policy = generate(complaint, provider)
            path = save_policy(policy)
            new_specs = policy.get("new_target_specs", {})
            print(f"\nSaved -> {path}")
            report(policy)
            if new_specs:
                specs_path = save_new_target_specs(new_specs)
                print(f"  Draft specs -> {specs_path}")
            print()
            print(policy_to_python(policy))
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    else:
        print("\nClinical Policy Generator")
        print("-------------------------")
        print(f"Provider: {provider}  (use --provider openai to switch)\n")
        print("Tier 1 complaints:")
        for i, c in enumerate(TIER1_COMPLAINTS, 1):
            print(f"  {i:2}. {c}")
        print("   0. Enter a custom complaint\n")

        choice = input("Select a number (or 0 for custom): ").strip()
        if choice == "0":
            complaint = input("Enter complaint name: ").strip()
        elif choice.isdigit() and 1 <= int(choice) <= len(TIER1_COMPLAINTS):
            complaint = TIER1_COMPLAINTS[int(choice) - 1]
        else:
            print("Invalid choice.")
            sys.exit(1)

        try:
            policy = generate(complaint, provider)
            path = save_policy(policy)
            new_specs = policy.get("new_target_specs", {})
            print(f"\nSaved -> {path}")
            report(policy)
            if new_specs:
                specs_path = save_new_target_specs(new_specs)
                print(f"  Draft specs -> {specs_path}")
            print()
            print(policy_to_python(policy))
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
