import streamlit as st
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge, Layout, EdgeStyle
import json
import os
from datetime import datetime
import pandas as pd
from external_data_pull import umls_knowledge_graph, symptom_drill_down

# team modules
from external_data_pull import umls_retrieval
from db_read import (get_session_ids, get_conversations,
                     get_summary,
                     check_for_conversation_kg,
                     get_conversation_kg,
                     filter_conversation_kg)
from db_write import (push_kg_to_db, update_post_summary)
from knowledge_graph import (convert_df_to_kg)
from llm_processing import (llm_process_knowledge_graph)

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PATH = os.path.join(SCRIPT_DIR, "patient_records.json")

if not os.path.exists(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)

# initial state vars
if "checkbox_list" not in st.session_state:
    st.session_state.checkbox_list = []

if "selected_symptom" not in st.session_state:
    st.session_state.selected_symptom = None

if "include_all_semantics" not in st.session_state:
    st.session_state.include_all_semantics = False

# ==========================================
# USER INTERFACE (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Doctor Summary", page_icon="🩺")
st.title("🩺 Diagnosis Tool")


# Sidebar for actions
st.sidebar.header("Session filters")
# add dropdowns
session_ids = get_session_ids()
selected_session = st.sidebar.selectbox(
    'Choose session',
    session_ids
)

col1, col2 = st.columns(2)
with col1:
    st.write('#### Pre Summary')
    # presummary
    summary = get_summary(selected_session)
    st.markdown(summary['PreSummary'][0])
with col2:
    st.write('#### Post Summary')
    # Editable text box
    summary = get_summary(selected_session)
    post_summary = st.text_area("Enter notes:", 
                                summary['PostSummary'][0],
                                height="stretch")
    if st.button("Save Post Summary", width='stretch'):
        # update database
        update_post_summary(selected_session, post_summary)

# conversations
st.write('#### Conversation Log')
conversations = get_conversations(selected_session)
st.dataframe(conversations)

# knowledge graph rendering
# check to see if graph exists in database
is_conversation_kg = check_for_conversation_kg(selected_session)
# if knowledge graph exists in db, load it instead of processing
if is_conversation_kg:
    # load database kg
    print('Using db conversation kg')
    print(st.session_state.checkbox_list)
    df_kg = get_conversation_kg(selected_session, st.session_state.checkbox_list)
else:
    df_kg = llm_process_knowledge_graph(selected_session)
# push this to database for retreival/filtering/persistence
push_kg_to_db(df_kg, selected_session)
graph = convert_df_to_kg(df_kg)

# convert graph for visualization
graph = StreamlitGraphWidget.from_graph(graph)
graph.show(overview=False)

# checkboxes for knowledge graph relationships
options = df_kg.relation.drop_duplicates().to_list()

# store selections in the checkbox list
checkbox_list = st.sidebar.multiselect("Filter relationships:", 
                                       options, default=[])

# Example of how to use the Apply Button or Agent Mode
# TODO: fix lag (have to click filter button twice to refresh)
if st.sidebar.button("Filter relationships"):
    # filter conversation_kg by checkbox_list
    st.session_state.checkbox_list = checkbox_list

# TODO: button to regenerate knowledge graph - needs more testing
if st.sidebar.button("Generate Knowledge Graph"):
    new_df_kg = llm_process_knowledge_graph(selected_session)
    print('New kg:', new_df_kg.head())
    push_kg_to_db(new_df_kg, selected_session, overwrite=True)

# place temporary input box to type a primary symptom for UMLS query
primary_symptom = st.sidebar.text_input("Enter Symptom for UMLS:")
if st.session_state.selected_symptom:
    primary_symptom = st.session_state.selected_symptom
umls_symptoms = umls_knowledge_graph(primary_symptom, 20)
# print(umls_symptoms)
# print(umls_symptoms['semantic_type'].unique())
if st.session_state.include_all_semantics is True:
    symptom_graph = symptom_drill_down(umls_symptoms, primary_symptom, True)
else:
    symptom_graph = symptom_drill_down(umls_symptoms, primary_symptom)
    st.session_state.include_all_semantics = False
# convert graph for visualization
symptom_graph = StreamlitGraphWidget.from_graph(symptom_graph)
# symptom_graph.show(overview=False)
st.write('#### Symptom Drill Down')
selected_nodes, selected_edges = symptom_graph.show(sync_selection=True, 
                                                    graph_layout=Layout.HIERARCHIC, 
                                                    overview=False)
# st.sidebar.write("Selected Edges: ", ", ".join(str(edge["id"]) for edge in selected_edges))
st.sidebar.write("Selected Nodes: ", ", ".join(str(node["properties"]["label"]) for node in selected_nodes))
# if node selected, run another UMLS query and refresh
# print(type(selected_nodes))
if selected_nodes:
    # assuming only 1 node is ever selected
    st.session_state.selected_symptom = selected_nodes[0]['properties']['label']
    print(selected_nodes[0]['properties']['label'])
    st.session_state.include_all_semantics = True

# button to clear symptom
if st.sidebar.button("Clear symptom graph"):
    # filter conversation_kg by checkbox_list
    st.session_state.selected_symptom = None
    st.session_state.include_all_semantics = False

