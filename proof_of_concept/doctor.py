import streamlit as st
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge
import json
import os
from datetime import datetime
import pandas as pd

# team modules
from external_data_pull import umls_retrieval
from db_read import (get_session_ids, get_conversations,
                     get_summary, update_summary,
                     check_for_conversation_kg,
                     get_conversation_kg,
                     filter_conversation_kg)
from db_write import (push_kg_to_db)
from knowledge_graph import (create_demo_graph, convert_df_to_kg)
from llm_processing import (llm_process_knowledge_graph)

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PATH = os.path.join(SCRIPT_DIR, "patient_records.json")

if not os.path.exists(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)

# ==========================================
# USER INTERFACE (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Doctor Summary", page_icon="🩺")
st.title("🩺 Diagnosis Tool")
# initial state vars
if "checkbox_list" not in st.session_state:
    st.session_state.checkbox_list = []

# Sidebar for actions
st.sidebar.header("Session filters")
# add dropdowns
session_ids = get_session_ids()
selected_session = st.sidebar.selectbox(
    'Choose session',
    session_ids
)

# # create side-by-side views
# col1, col2 = st.columns(2)
# with col1:
#     # conversations
#     conversations = get_conversations(selected_session)
#     st.dataframe(conversations)

# with col2:
#     # knowledge graph
#     graph = StreamlitGraphWidget.from_graph(create_demo_graph())
#     graph.show()

# TODO: stack interface elements for now, until you refine usage
# summary
summary = get_summary(selected_session)
edited_summary = st.data_editor(summary)
# write edited_summary to database
update_summary(selected_session, edited_summary)

# conversations
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
graph.show()

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
