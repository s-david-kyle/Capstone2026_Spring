import streamlit as st
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge
import json
import os
from datetime import datetime

# team modules
from external_data_pull import umls_retrieval
from db_read import (get_session_ids, get_conversations,
                     get_summary, update_summary)
from knowledge_graph import (create_demo_graph)
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
st.title("🩺 Doctor Patient Diagnosis")


# Sidebar for actions
st.sidebar.header("Controls")
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

# TODO: stack interface elements for now, until you refine use
# summary
summary = get_summary(selected_session)
edited_summary = st.data_editor(summary)
# TODO: write edited_summary to database
update_summary(selected_session, edited_summary)

# favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
# st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

# conversations
conversations = get_conversations(selected_session)
st.dataframe(conversations)

# knowledge graph
print(llm_process_knowledge_graph(selected_session))

graph = StreamlitGraphWidget.from_graph(create_demo_graph())
graph.show()

# st.sidebar.write('Selected:', selected_session)
