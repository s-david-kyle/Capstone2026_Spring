import streamlit as st
import json
import os
from datetime import datetime

# team modules
from external_data_pull import umls_retrieval, umls_knowledge_graph
from db_write import (add_new_session_data, 
                      get_session_id, 
                      add_turn_data, 
                      add_summary_data, 
                      add_session_metric_data)
from llm_processing import (llm_symptom_check,
                            llm_single_symptom_check,
                            get_llm_response,
                            generate_summary,
                            system_grouping,
                            form_system_question,
                            drilldown_system)

# ==========================================
# PART 1: SYSTEM CONFIGURATION
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PATH = os.path.join(SCRIPT_DIR, "patient_records.json")

# state vars
if "turn_number" not in st.session_state:
    st.session_state.turn_number = 1

if "session_id" not in st.session_state:
    st.session_state.session_id = get_session_id()

if "system_drilldown" not in st.session_state:
    st.session_state.system_drilldown = False

if "system_drilldown_start" not in st.session_state:
    st.session_state.system_drilldown_start = False

if "question_phase" not in st.session_state:
    st.session_state.question_phase = 1

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

st.set_page_config(page_title="Patient Intake", page_icon="🩺")
st.title("🩺 Patient Intake Assistant")

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
session_id = st.session_state.session_id
session_start = datetime.now()

# Initialize completion flag to track the UI state
if "conversation_complete" not in st.session_state:
    st.session_state.conversation_complete = False

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

for msg in st.session_state.messages:
    # Display message with a small time caption
    time_str = datetime.now().strftime("%H:%M") 
    st.chat_message(msg["role"]).write(msg["content"])
    st.caption(f"Time: {time_str}")

# Requirement: Text input box for the patient
# Logic to disable input once the session is complete
if not st.session_state.get("conversation_complete", False):
    prompt = st.chat_input("Type your response here...")
else:
    st.info("Intake complete. The clinical summary is available below.")
    prompt = None

if prompt:

    # Add patient response to the log
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # pull symptoms here, place data inside db Session.SecondaryComplaint at the end
    # new_symptoms = llm_symptom_check(prompt)

    # -------------------------------------------------------------------------------------
    # 1: research intial response and build knowledge graph of related symptoms and systems
    # -------------------------------------------------------------------------------------
    # if st.session_state.system_drilldown == False:
    if st.session_state.question_phase == 1:
        # gather list of symptoms and systems, create kg to search through
        new_symptom = llm_single_symptom_check(prompt)
        st.session_state.symptoms.append(new_symptom)
        # for testing/refinement (can remove - results are written to db at session close)
        print('LLM-extracted symptoms: ', st.session_state.symptoms)

        # call UMLS API and push terms to session_state
        # UI-Safe UMLS call: Prevents crashing if API Key is missing
        try:
            # UMLS KG function call here
            umls_symptoms = umls_knowledge_graph(new_symptom, 50)  # modify number for tests
            symtom_system_graph = system_grouping(umls_symptoms, 
                                                new_symptom, 
                                                session_id, 
                                                st.session_state.turn_number)
        except Exception:
            # new_umls_terms = [] # Fallback to empty list so UI stays active
            st.sidebar.warning(" UMLS Offline (API Key Required)")
        
        # removing session_state storage to use database instead
        # st.session_state.umls_terms.append(new_umls_terms)
        # for testing/refinement
        # print('UMLS terms: ', st.session_state.umls_terms)

        # update turn table with current patient dialogue
        add_turn_data(session_id, datetime.now(), 'patient', prompt)

        # UPGRADE: Use Status container for a smoother UI animation
        with st.status("Analyzing symptoms...", expanded=False) as status:
            # put call to form_system_question here to start next phase of system drilldown
            response = form_system_question(session_id, st.session_state.turn_number, new_symptom)
            # increment turn
            st.session_state.turn_number += 1
            # move to drill down sytem next turn
            # st.session_state.system_drilldown = True
            # TODO: change to increment phase by 1 here
            st.session_state.question_phase += 1
            st.session_state.system_drilldown_start = True
            # response = get_llm_response(st.session_state.messages)
            status.update(label="Response ready!", state="complete", expanded=False)

    # -------------------------------------------------------------------------------------
    # 2: Drill down to affected system
    # -------------------------------------------------------------------------------------
    # TODO: use phase number instead
    elif st.session_state.question_phase == 2:
        # drilldown on system
        # update turn table with current patient dialogue
        add_turn_data(session_id, datetime.now(), 'patient', prompt)
        # pull most recent symptom into this function calls
        response, turn_number, system_drilldown_start, current_phase = drilldown_system(session_id, 
                                                st.session_state.turn_number - 1, 
                                                st.session_state.symptoms[-1], # grabs last extracted symptom
                                                prompt,
                                                st.session_state.system_drilldown_start,
                                                st.session_state.question_phase)
        # want to note what turn drilldown_start happened
        st.session_state.system_drilldown_start = system_drilldown_start
        # update state turn_number
        st.session_state.turn_number = turn_number
        # TODO: update session_state.question_phase
        st.session_state.question_phase = current_phase

    # -------------------------------------------------------------------------------------
    # 3: Drill down to specific system
    # -------------------------------------------------------------------------------------
    elif st.session_state.question_phase == 3:
        response = '2nd question to narrow down system from freq_system'
        
    else:
        # likely end conversation here
        pass
    
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
    
    # log system message to database
    add_turn_data(session_id, datetime.now(), 'system', response)

    # TODO: temporarily disabling while question logic is being modified
    # UI LOGIC: Check if the AI is closing the conversation
    # exit_keywords = ["book an appointment", "schedule", "goodbye", "take care"]
    # if any(keyword in response.lower() for keyword in exit_keywords):
    #     st.session_state.conversation_complete = True
    #     st.rerun()   

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
            # TODO: session_end does not appear to be using the correct timestamp
            add_new_session_data(session_id, session_start, datetime.now(),
                                 clinical_summary, st.session_state.symptoms)
            # Summary
            add_summary_data(session_id, clinical_summary)

            # SessionMetric
            add_session_metric_data(session_id)

            st.sidebar.success("Intake Saved Successfully!")
if "final_summary" in st.session_state:
    # Replace placeholders with real patient data
    final_note = st.session_state.final_summary.replace("[Patient Name - to be added]", st.session_state.patient_name)
    final_note = final_note.replace("[Date]", st.session_state.intake_date)
    
    st.divider()
    st.subheader(f"📋 Doctor's Summary Note for {st.session_state.patient_name}")
    st.info(final_note)

if st.sidebar.button("Clear Chat / New Patient"):
    # save session to db
    clinical_summary = generate_summary(st.session_state.messages)
    add_new_session_data(session_id, session_start, datetime.now(),
                        clinical_summary, st.session_state.symptoms)
    add_summary_data(session_id, clinical_summary)
    add_session_metric_data(session_id)
    # remove previous session data
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
    