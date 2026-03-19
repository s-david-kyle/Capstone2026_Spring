import streamlit as st
import ollama
import json
import os
from datetime import datetime

# team modules
from external_data_pull import umls_retrieval
from db_write import (add_new_session_data, get_session_id, 
                      add_turn_data, add_summary_data, 
                      add_session_metric_data)
from llm_processing import ollama_llm_symptom_check

# ==========================================
# PART 1: SYSTEM CONFIGURATION
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PATH = os.path.join(SCRIPT_DIR, "patient_records.json")

MODEL = 'gemma3:4b' # modify as needed

if not os.path.exists(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)
# ==========================================
# PART 2: MODULAR BRAINS (LLM LOGIC)
# ==========================================

def get_llm_response(messages):
    """
    Handles the chat. Forces short, precise questions using SOCRATES.
    """
    try:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a clinical intake bot. "
                "STRICT RULES: "
                "1. Ask only ONE question at a time. "
                "2. Keep responses under 15 words. "
                "3. No pleasantries or small talk. "
                "4. Be direct and precise."
            )
        }
        # Combines the system rules with the existing chat history
        # print(messages)
        response = ollama.chat(model=MODEL, messages=[system_instruction] + messages)
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

def generate_summary(messages):
    
    try:
        # Formats the chat into a single string for easier summarization
        chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        summary_instruction = {
            "role": "system",
            "content": (
                "Summarize this patient interview into a professional clinical note. "
                "Include: Chief Complaint, Duration, Severity, and Associated Symptoms. "
                "Use bullet points. Max 60 words."
            )
        }
        
        response = ollama.chat(
            model=MODEL, 
            messages=[summary_instruction, {"role": "user", "content": chat_history}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Summary failed: {str(e)}"

# ==========================================
# PART 3: STORAGE LOGIC
# ==========================================

def save_patient_data(conversation_log, summary):
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "full_log": conversation_log
    }
    
    data = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    
    data.append(record)
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

# ==========================================
# PART 4: USER INTERFACE (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Patient Intake", page_icon="🩺")
st.title("🩺 Patient Intake Assistant")

# Create unique session ID
session_id = get_session_id()
session_start = datetime.now()

# Initialize the conversation log in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. What symptoms are you experiencing today?"}
    ]
    # create new symptoms and umls_terms lists
    st.session_state.symptoms = []
    st.session_state.umls_terms = []
    # log first dialogue in database turn table
    add_turn_data(session_id, datetime.now(), 'system', st.session_state.messages[0]['content'])

# Display the conversation history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Requirement: Text input box for the patient
if prompt := st.chat_input("Type your response here..."):
    # Add patient response to the log
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # pull symptoms here, place data inside db Session.SecondaryComplaint at the end
    new_symptoms = ollama_llm_symptom_check(prompt, MODEL)
    st.session_state.symptoms.append(new_symptoms)
    # for testing/refinement (can remove - results are written to db at session close)
    print('LLM-extracted symptoms: ', st.session_state.symptoms)

    # call UMLS API and push terms to session_state
    new_umls_terms = umls_retrieval(new_symptoms)
    st.session_state.umls_terms.append(new_umls_terms)
    # for testing/refinement
    print('UMLS terms: ', st.session_state.umls_terms)

    # update turn table with current patient dialogue
    add_turn_data(session_id, datetime.now(), 'patient', prompt)

    # Get and display LLM response
    with st.spinner("Thinking..."):
        response = get_llm_response(st.session_state.messages)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
        # update turn table with current system dialogue
        add_turn_data(session_id, datetime.now(), 'system', response)


# Sidebar for actions
st.sidebar.header("Controls")

if st.sidebar.button("Finish & Generate Summary"):
    if len(st.session_state.messages) < 2:
        st.sidebar.warning("Please describe symptoms first.")
    else:
        with st.spinner("Generating clinical summary..."):
            clinical_summary = generate_summary(st.session_state.messages)
            
            # Save to JSON - can remove since data pushed to db
            save_patient_data(st.session_state.messages, clinical_summary)
            
            # Store in session state to keep it visible on screen
            st.session_state.final_summary = clinical_summary

            # final DB updates for session
            # TODO: use LLM to filter down UMLS terms based on conversation data

            # Session
            add_new_session_data(session_id, MODEL, session_start, datetime.now(),
                                 clinical_summary, st.session_state.symptoms)
            # Summary
            add_summary_data(session_id, clinical_summary)

            # SessionMetric
            add_session_metric_data(session_id)

            st.sidebar.success("Intake Saved Successfully!")

# Display the Summary Note
if "final_summary" in st.session_state:
    st.divider()
    st.subheader("📋 Doctor's Summary Note")
    st.info(st.session_state.final_summary)

if st.sidebar.button("Clear Chat / New Patient"):
    # save session to db
    clinical_summary = generate_summary(st.session_state.messages)
    add_new_session_data(session_id, MODEL, session_start, datetime.now(),
                                 clinical_summary, st.session_state.symptoms)
    add_summary_data(session_id, clinical_summary)
    add_session_metric_data(session_id)
    # remove previous session data
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()