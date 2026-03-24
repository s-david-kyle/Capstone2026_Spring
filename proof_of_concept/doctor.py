import streamlit as st
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge
import json
import os
from datetime import datetime

# team modules
from external_data_pull import umls_retrieval
from db_read import (get_session_ids, get_conversations,
                     get_summary, update_summary)
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
st.title("🩺 Doctor Patient Diagnosis")


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
df_kg = llm_process_knowledge_graph(selected_session)
# TODO: push this to database for retreival/filtering
push_kg_to_db(df_kg, selected_session)
graph = convert_df_to_kg(df_kg)

graph = StreamlitGraphWidget.from_graph(graph)
graph.show()

# checkboxes for knowledge graph relationships
# Create a list of checkboxes
options = df_kg.relation.drop_duplicates().to_list()

# Create the checkbox list
checkbox_list = st.sidebar.multiselect("Filter relationships:", options, default=[])

# Display the selected options
st.sidebar.write("Visible relationships:", checkbox_list)

# TODO: filter df_kg by checkbox_list

# Example of how to use the Apply Button or Agent Mode
if st.sidebar.button("Apply Changes"):
    st.sidebar.write("Changes applied (simulated).")

# st.sidebar.write('Selected:', selected_session)
