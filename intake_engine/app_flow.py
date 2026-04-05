from intake_engine.IntakeState import IntakeState
from intake_engine.clinical_normalizer import ClinicalNormalizer
from intake_engine.config import LLM_CONFIG
from intake_engine.llm_adapter import create_llm_adapter
from intake_engine.llm_extractor import BoundedLLMExtractor
from intake_engine.llm_question_generator import LLMQuestionGenerator

from intake_engine.db.session_repository import create_session
from intake_engine.db.session_persistence import sync_session_state, load_session_state


class IntakeAppFlow:
    def __init__(
        self,
        conn = None,
        session_id = None,
        llm_config = None,
    ):
        self.llm_config = dict(LLM_CONFIG)
        if llm_config is not None:
            self.llm_config.update(llm_config)

        self.adapter = create_llm_adapter(self.llm_config)

        self.extractor = BoundedLLMExtractor(self.adapter.generate)
        self.normalizer = ClinicalNormalizer()
        self.question_generator = LLMQuestionGenerator(self.adapter)

        self.conn = conn
        self.session_id = session_id
        self.state = IntakeState()

    def new_session(
        self,
        session_name = "Intake session",
        model_version = "prototype_v1",
        primary_complaint = None,
        initial_data = None,
        auto_save = False,
    ):
        self.state = IntakeState(data = initial_data)

        if self.conn is not None and self.session_id is None:
            self.session_id = create_session(
                conn = self.conn,
                session_name = session_name,
                model_version = model_version,
                primary_complaint = primary_complaint,
            )

        if auto_save:
            self.save()

        return self.state.to_dict()

    def load_state(self, saved_state):
        self.state = IntakeState(data = saved_state)
        return self.state.to_dict()

    def load_session(self, session_id):
        if self.conn is None:
            raise ValueError("Cannot load session without a database connection")

        loaded_state = load_session_state(
            conn = self.conn,
            session_id = session_id,
        )

        if loaded_state is None:
            raise ValueError(f"No saved intake state found for session_id = {session_id}")

        self.session_id = session_id
        self.state = loaded_state
        return self.state.to_dict()

    def start_intake(self, auto_save = False):
        result = self.state.get_next_question(
            question_generator = self.question_generator
        )

        if auto_save:
            self.save()

        return result

    def submit_answer(self, patient_answer, auto_save = False):
        result = self.state.process_answer_with_llm(
            patient_answer = patient_answer,
            extractor = self.extractor,
            normalizer = self.normalizer,
            question_generator = self.question_generator,
        )

        if auto_save:
            self.save()

        return result

    def save(self):
        if self.conn is None:
            raise ValueError("Cannot save without a database connection")

        if self.session_id is None:
            raise ValueError("Cannot save without an active session_id")

        return sync_session_state(
            conn = self.conn,
            session_id = self.session_id,
            intake_state = self.state,
        )

    def get_state(self):
        return self.state.to_dict()

    def get_transcript(self):
        return self.state.to_dict()["conversation_meta"]["transcript"]