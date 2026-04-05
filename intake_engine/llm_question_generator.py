from intake_engine.policies.target_specs import TARGET_SPECS


class LLMQuestionGenerator:
    def __init__(self, llm_backend):
        """
        llm_backend can be:
        - an object with a generate(prompt) method
        - or a plain callable(prompt) -> str
        """
        self.llm_backend = llm_backend

    def _target_spec(self, target):
        if target is None:
            return None
        return TARGET_SPECS.get(target)

    def _render_yes_no_template_question(self, spec):
        aux = spec.get("question_aux", "").strip()
        subject = spec.get("question_subject", "").strip()
        predicate = spec.get("question_predicate", "").strip()

        if not (aux and subject and predicate):
            return None

        return f"{aux} {subject} {predicate}?"

    def _deterministic_question_for_target(self, target):
        spec = self._target_spec(target)

        if spec is None:
            return None

        question_mode = spec.get("question_mode")

        if question_mode == "deterministic":
            return spec.get("question_text")

        if question_mode == "yes_no_template":
            return self._render_yes_no_template_question(spec)

        return None

    def build_prompt(self, intake_state, target = None, intent = None):
        complaint = intake_state.get("chief_complaint_primary")
        hpi = intake_state.get("hpi", {})
        policy_answers = intake_state.get("policy_answers", {})

        if target is not None:
            spec = TARGET_SPECS.get(target)
            guidance = (
                spec["question_instruction"]
                if spec is not None
                else "Ask clearly and directly about the given target."
            )
            mode = "target"
            action_name = target
        else:
            mode = "intent"
            action_name = intent
            guidance = (
                "Phrase the next patient-facing intake turn for the given intent. "
                "If the intent is urgent, make it brief and direct. "
                "If the intent is a question, ask exactly one short question."
            )

        return f"""
You are a medical intake question generator.

Write exactly one short patient-facing intake turn.

You are not diagnosing.
You are not choosing the next target or intent.
You are only phrasing the next turn.

Mode:
{mode}

Action:
{action_name}

Guidance:
{guidance}

Chief complaint:
{complaint}

Current HPI:
{hpi}

Current policy answers:
{policy_answers}

Rules:
- Return exactly one short patient-facing turn.
- Use plain patient-friendly language.
- Do not explain your reasoning.
- Do not include any text before the turn.
- Do not include any text after the turn.
- If asking a question, end with a question mark.
- If giving urgent advice, keep it brief and direct.

Output:
""".strip()

    def _call_backend(self, prompt):
        if hasattr(self.llm_backend, "generate"):
            return self.llm_backend.generate(prompt)

        return self.llm_backend(prompt)

    def generate_question(self, intake_state, target = None, intent = None):
        deterministic_question = self._deterministic_question_for_target(target)
        if deterministic_question is not None:
            return deterministic_question

        prompt = self.build_prompt(
            intake_state = intake_state,
            target = target,
            intent = intent,
        )

        raw_output = self._call_backend(prompt).strip()

        if not raw_output:
            raise ValueError("LLM question generator returned empty text")

        lines = [line.strip() for line in raw_output.splitlines() if line.strip()]

        for line in lines:
            if "?" in line:
                return line[: line.find("?") + 1].strip()

        return lines[0]