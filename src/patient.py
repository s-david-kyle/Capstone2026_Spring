import streamlit as st
import json
import os
from datetime import datetime

# team modules
from external_data_pull import umls_retrieval
from db_write import (add_new_session_data, 
                      get_session_id, 
                      add_turn_data, 
                      add_summary_data, 
                      add_session_metric_data)
from llm_processing import (llm_symptom_check,
                            get_llm_response,
                            generate_summary)

# --- AVATAR SYSTEM ---
def update_avatar(placeholder, state):
    # 1. Save the new state to memory
    st.session_state.robot_state = state
    path = f"assets/capsule_{state}.gif"
    
    # 2. Forcefully clear the frame and inject the new GIF instantly
    placeholder.empty()
    with placeholder.container():
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.image(path)

# ==========================================
# PART 1: SYSTEM CONFIGURATION
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PATH = os.path.join(SCRIPT_DIR, "patient_records.json")

if not os.path.exists(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)

# ==========================================
# PART 2: MODULAR BRAINS (LLM LOGIC)
# ==========================================
# Note: LLM functions moved to llm_processing.py

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

# 1. Use 'wide' layout so the chat isn't squished
st.set_page_config(page_title="Patient Intake", page_icon="🩺", layout="wide")
st.title("🩺 Patient Intake Assistant")

# Initialize the robot state
if "robot_state" not in st.session_state:
    st.session_state.robot_state = "idle"

# 2. Pin Avatar to Sidebar with an updatable Placeholder
with st.sidebar:
    st.header("Virtual Assistant")
    
    # Create an empty "picture frame" we can update later
    avatar_spot = st.empty() 
    st.divider()

# Draw the initial robot into the frame right away
update_avatar(avatar_spot, st.session_state.get("robot_state", "idle"))

# Initialize patient details and intake date
if "patient_name" not in st.session_state:
    st.session_state.patient_name = ""
if "intake_date" not in st.session_state:
    st.session_state.intake_date = datetime.now().strftime("%B %d, %Y")

# Registration Gate: Only show chat after name is entered
if not st.session_state.patient_name:
    st.subheader("Welcome. Please register to begin.")
    name_input = st.text_input("Enter your Full Name:")
    if st.button("Start Consultation"):
        if name_input:
            st.session_state.patient_name = name_input
            st.rerun()
        else:
            st.error("Please enter a name to continue.")
    st.stop() # This prevents the rest of the code from running until registered

# Display patient info in the sidebar once registered
st.sidebar.info(f"👤 Patient: **{st.session_state.patient_name}**")
st.sidebar.info(f"📅 Date: **{st.session_state.intake_date}**")

# Create unique session ID
session_id = get_session_id()
session_start = datetime.now()

# Initialize completion flag to track the UI state
if "conversation_complete" not in st.session_state:
    st.session_state.conversation_complete = False

# Initialize the conversation log in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hello. What symptoms are you experiencing today?",
            "time": datetime.now().strftime("%H:%M") # Save time here!
        }
    ]
    # create new symptoms and umls_terms lists
    st.session_state.symptoms = []
    st.session_state.umls_terms = []
    # log first dialogue in database turn table
    add_turn_data(session_id, datetime.now(), 'system', st.session_state.messages[0]['content'])

# --- CLEAN CHAT DISPLAY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # Fetch the saved time, or create one if it's missing
        saved_time = msg.get("time", datetime.now().strftime("%H:%M"))
        st.caption(f"Time: {saved_time}")

# Requirement: Text input box for the patient
# Logic to disable input once the session is complete
if not st.session_state.get("conversation_complete", False):
    prompt = st.chat_input("Type your response here...")
else:
    st.info("Intake complete. The clinical summary is available below.")
    prompt = None

if prompt:

    update_avatar(avatar_spot, "spin")
    time_now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": prompt, "time": time_now})
    
    with st.chat_message("user"):
        st.write(prompt)
        st.caption(f"Time: {time_now}")
        
    # pull symptoms here, place data inside db Session.SecondaryComplaint at the end
    new_symptoms = llm_symptom_check(prompt)
    st.session_state.symptoms.append(new_symptoms)
    # for testing/refinement (can remove - results are written to db at session close)
    print('LLM-extracted symptoms: ', st.session_state.symptoms)

    # call UMLS API and push terms to session_state
    try:
        new_umls_terms = umls_retrieval(new_symptoms)
    except Exception:
        new_umls_terms = [] 
        # Force UI to show Warning immediately
        update_avatar(avatar_spot, "warning") 
        st.sidebar.warning(" UMLS Offline (API Key Required)")
    
    st.session_state.umls_terms.append(new_umls_terms)
    # for testing/refinement
    print('UMLS terms: ', st.session_state.umls_terms)

    # update turn table with current patient dialogue
    add_turn_data(session_id, datetime.now(), 'patient', prompt)

    # UPGRADE: Use Status container for a smoother UI animation
    with st.status("Analyzing symptoms...", expanded=False) as status:
        update_avatar(avatar_spot, "spin") 
        try:
            response = get_llm_response(st.session_state.messages)
            status.update(label="Response ready!", state="complete", expanded=False)
        except Exception as e:
            # Force UI to show Error immediately
            update_avatar(avatar_spot, "error")
            status.update(label="System Error", state="error", expanded=True)
            response = "I'm sorry, I'm having trouble connecting to my diagnostic center."    

    if st.session_state.robot_state not in ["warning", "error"]:
        # Force UI back to idle instantly before writing the response
        update_avatar(avatar_spot, "idle")

    # Add assistant response to the log WITH saved time
    resp_time = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "assistant", "content": response, "time": resp_time})

    with st.chat_message("assistant"):
        st.write(response)
        st.caption(f"Time: {resp_time}")

    add_turn_data(session_id, datetime.now(), 'system', response)

    # UI LOGIC: Check if the AI is closing the conversation
    exit_keywords = ["book an appointment", "schedule", "goodbye", "take care"]
    if any(keyword in response.lower() for keyword in exit_keywords):
        st.session_state.conversation_complete = True
        st.rerun() 

    st.rerun() 

# Sidebar for actions
st.sidebar.header("Controls")
if st.sidebar.button("Finish & Generate Summary"):
    if len(st.session_state.messages) < 2:
        st.sidebar.warning("Please describe symptoms first.")
    else:
        # Force UI to instantly show the green laser scan
        update_avatar(avatar_spot, "scan")
        
        with st.spinner("Generating clinical summary..."):
            clinical_summary = generate_summary(st.session_state.messages)
            
            save_patient_data(st.session_state.messages, clinical_summary)
            st.session_state.final_summary = clinical_summary

            add_new_session_data(session_id, session_start, datetime.now(),
                                 clinical_summary, st.session_state.symptoms)
            add_summary_data(session_id, clinical_summary)
            add_session_metric_data(session_id)

            # Force UI to instantly show the rainbow success
            update_avatar(avatar_spot, "success")
            st.sidebar.success("Intake Saved Successfully!")
        
        st.rerun()

if "final_summary" in st.session_state:
    # Replace placeholders with real patient data
    final_note = st.session_state.final_summary.replace("[Patient Name - to be added]", st.session_state.patient_name)
    final_note = final_note.replace("[Date]", st.session_state.intake_date)
    
    st.divider()
    st.subheader(f"📋 Doctor's Summary Note for {st.session_state.patient_name}")
    st.info(final_note)

if st.sidebar.button("Clear Chat / New Patient"):
    clinical_summary = generate_summary(st.session_state.messages)
    add_new_session_data(session_id, session_start, datetime.now(),
                         clinical_summary, st.session_state.symptoms)
    add_summary_data(session_id, clinical_summary)
    add_session_metric_data(session_id)
    
    # Clear session data
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Force UI to reset to idle
    update_avatar(avatar_spot, "idle")
    
    # --- NEW: Refresh for new patient ---
    st.rerun()