import streamlit as st
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge
import json
import os
from datetime import datetime

# team modules
from external_data_pull import umls_retrieval
from db_read import (add_new_session_data, 
                      get_session_id, 
                      add_turn_data, 
                      add_summary_data, 
                      add_session_metric_data)

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PATH = os.path.join(SCRIPT_DIR, "patient_records.json")

if not os.path.exists(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)

# ==========================================
# STORAGE LOGIC
# ==========================================

# TODO: add database access (add db_write functions as needed)

# ==========================================
# USER INTERFACE (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Doctor Summary", page_icon="🩺")
st.title("🩺 Doctor Patient Diagnosis")

# demo yfiles library
nodes = [
    Node(id=0, properties={"firstName": "Alpha", "label": "Person A"}),
    Node(id=1, properties={"firstName": "Bravo", "label": "Person B"}),
    Node(id=2, properties={"firstName": "Charlie", "label": "Person C", "has_hat": False}),
    Node(id=3, properties={"firstName": "Delta", "label": "Person D", "likes_pizza": True})
]
edges = [
    Edge(start=0, end=1, properties={"since": "1992", "label": "knows"}),
    Edge(start=1, end=3, properties={"label": "knows", "since": "1992"}),
    Edge(start=2, end=3, properties={"label": "knows", "since": "1992"}),
    Edge(start=0, end=2, properties={"label": "knows", "since": 234})
]

StreamlitGraphWidget(nodes, edges).show()

# Sidebar for actions
st.sidebar.header("Controls")
