import streamlit as st

from intake_engine.app_flow import IntakeAppFlow
from intake_engine.db.connection import create_connection
from intake_engine.db.schema import create_tables


st.set_page_config(page_title = "Patient Intake", page_icon = "🩺")
st.title("🩺 Patient Intake Assistant")


def init_flow():
    conn = create_connection()
    create_tables(conn)

    flow = IntakeAppFlow(conn = conn)

    flow.new_session(
        session_name = "Engine-backed intake session",
        model_version = "intake_engine_v1",
        auto_save = True,
    )

    flow.start_intake(auto_save = True)

    st.session_state.conn = conn
    st.session_state.flow = flow
    st.session_state.session_id = flow.session_id


def reset_engine_session():
    try:
        if "conn" in st.session_state and st.session_state.conn is not None:
            st.session_state.conn.close()
    except Exception:
        pass

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()


def format_list(values):
    if not values:
        return "None reported"
    return ", ".join(str(v) for v in values)


def format_bool(value):
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Unknown"


def build_patient_summary(state):
    chief_complaint = state.get("chief_complaint_primary") or "Not recorded"

    hpi = state.get("hpi", {})
    policy_answers = state.get("policy_answers", {})
    conversation_meta = state.get("conversation_meta", {})

    summary_lines = [
        f"**Chief complaint:** {chief_complaint}",
        f"**Onset:** {hpi.get('onset') or 'Not recorded'}",
        f"**Duration:** {hpi.get('duration') or 'Not recorded'}",
        f"**Severity:** {hpi.get('severity') or 'Not recorded'}",
        f"**Location:** {hpi.get('location') or 'Not recorded'}",
        f"**Timing:** {hpi.get('timing') or 'Not recorded'}",
        f"**Course:** {hpi.get('course') or 'Not recorded'}",
        f"**Character:** {hpi.get('character') or 'Not recorded'}",
        f"**Associated symptoms:** {format_list(hpi.get('associated_symptoms', []))}",
        f"**Pertinent positives:** {format_list(state.get('pertinent_positives', []))}",
        f"**Pertinent negatives:** {format_list(state.get('pertinent_negatives', []))}",
        "",
        "**Safety / red-flag screening:**",
        f"- Sudden severe onset: {format_bool(policy_answers.get('sudden_severe_onset'))}",
        f"- Neurologic symptoms: {format_bool(policy_answers.get('neurologic_symptoms'))}",
        f"- Neurologic symptom terms: {format_list(policy_answers.get('neurologic_symptom_terms', []))}",
        f"- Visual changes: {format_bool(policy_answers.get('visual_changes'))}",
        f"- Confusion or altered mental status: {format_bool(policy_answers.get('confusion_or_ams'))}",
        f"- Fever or neck stiffness: {format_bool(policy_answers.get('fever_or_neck_stiffness'))}",
        f"- Head trauma: {format_bool(policy_answers.get('head_trauma'))}",
        f"- Pregnancy or postpartum context: {format_bool(policy_answers.get('pregnancy_or_postpartum_context'))}",
        "",
        f"**Other concerns:** {format_list(state.get('other_concerns', []))}",
        f"**Missing clarifications:** {format_list(state.get('missing_clarifications', []))}",
        f"**Flags:** {format_list(state.get('flags', []))}",
        f"**Intake complete:** {'Yes' if conversation_meta.get('intake_complete') else 'No'}",
    ]

    return "\n".join(summary_lines)


if "flow" not in st.session_state:
    init_flow()


flow = st.session_state.flow


st.sidebar.header("Controls")
st.sidebar.write(f"Session ID: {st.session_state.session_id}")

if st.sidebar.button("Save now"):
    result = flow.save()
    st.sidebar.success(f"Saved. Turn IDs: {result['saved_turn_ids']}")

if st.sidebar.button("Finish Intake"):
    flow.save()
    st.session_state.final_state = flow.get_state()
    st.session_state.final_summary = build_patient_summary(st.session_state.final_state)
    st.sidebar.success("Intake saved successfully.")

if st.sidebar.button("Clear Chat / New Patient"):
    reset_engine_session()


transcript = flow.get_transcript()

for turn in transcript:
    speaker = "assistant" if turn["speaker"] == "system" else "user"
    with st.chat_message(speaker):
        st.write(turn["text"])


patient_input = st.chat_input("Type your response here...")

if patient_input:
    flow.submit_answer(
        patient_answer = patient_input,
        auto_save = True,
    )
    st.rerun()


if "final_summary" in st.session_state:
    st.divider()
    st.subheader("Doctor Summary")
    st.markdown(st.session_state.final_summary)

    with st.expander("Structured Intake State"):
        st.json(st.session_state.final_state)