import streamlit as st
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge
import json
import os
from datetime import datetime

# team modules
from external_data_pull import umls_retrieval
from db_read import (get_session_ids)
from knowledge_graph import (create_demo_graph)

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

# knowledge graph
graph = StreamlitGraphWidget.from_graph(create_demo_graph())
graph.show()


# Sidebar for actions
st.sidebar.header("Controls")
# add dropdowns
session_ids = get_session_ids()
option1 = st.sidebar.selectbox(
    'Choose session',
    session_ids
)

# st.sidebar.write('Selected:', option1)
