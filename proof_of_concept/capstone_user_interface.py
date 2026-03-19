import streamlit as st
import ollama
import json
import os
from datetime import datetime

# team modules
from external_data_pull import ollama_llm_symptom_check
from db_write import add_data_to_db, add_new_session_data, get_session_id, add_turn_data, add_summary_data

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

# Initialize the conversation log in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. What symptoms are you experiencing today?"}
    ]

# Create unique session ID
# TODO: check if this is running each dialogue turn
session_id = get_session_id()
# new_session = True
session_start = datetime.now()

# Display the conversation history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Requirement: Text input box for the patient
if prompt := st.chat_input("Type your response here..."):
    # Add patient response to the log
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    user_time_of_message = datetime.now()
    system_time_of_message = datetime.now() # this will get updated below

    # TODO: pull symptoms here
    # temporary code - will place data inside db
    symptoms = ollama_llm_symptom_check(prompt, MODEL)
    # TODO: see if this is printing False in UI
    print(symptoms)

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
            
            # Save to JSON
            save_patient_data(st.session_state.messages, clinical_summary)
            
            # Store in session state to keep it visible on screen
            st.session_state.final_summary = clinical_summary
            print(st.session_state.final_summary)

            # final DB updates for session
            # Add to session table (complete after information gathered)
            add_new_session_data(session_id, MODEL, session_start, datetime.now(),
                                 clinical_summary)
            # summary
            add_summary_data(session_id, clinical_summary)
            # TODO: load session metric into database
            # new_row = [1, 8, 7, 6, 5, .833, 1, "{'symptom': 'radiation'}", 320, 1,
            #            "{'symptom': 'radiation'}", .72, 1, 1, 0, "{'hallucinated phrases': 'None'}"]
            # add_data_to_db('SessionMetric', new_row)

            st.sidebar.success("Intake Saved Successfully!")

# Display the Summary Note
if "final_summary" in st.session_state:
    st.divider()
    st.subheader("📋 Doctor's Summary Note")
    st.info(st.session_state.final_summary)

if st.sidebar.button("Clear Chat / New Patient"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()