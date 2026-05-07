# A Human-Centered AI for Structured Symptom Collection and Diagnosis Support

**A project to leverage Large Language Models for assisting physicians in diagnosis by extracting patient symptoms.**

## 1. Overview
This project aims to build a system that utilizes a Large Language Model (LLM) to analyze patient conversations to assist doctors with identifying diagnoses. It makes use of knowledge graphs and medical APIs like UMLS to structure questions, focus on specific bioligical systems and symptoms, and drill down to the most specific symptom a patient is experiencing. It exposes this processes to doctors through a doctor-facing interface, which summarizes conversations and shows data structures created throughout the patient conversation. This tool is intended to support, not replace, the judgment of a qualified physician.
## 2. Features
* **Symptom Extraction:** LLM-powered extraction of symptoms from LLM-powered patient chat.
* **Differential Diagnosis Generation:** Generates the most likely symptom a patient is experiencing based on the conversations held with the patient and relevant UMLS queries.
* **User Interface (UI):** A web interface for gathering information and viewing results.
* **Data Visualization:** Knowledge graphs displaying conversation summaries and maps of systems and symptoms accessed during the patient conversation.
## 3. Technology Stack
*   **LLM:** Llama, Gemma
*   **Programming Language:** Python
*   **Frameworks/Libraries:**  Ollama, NetworkX, yFiles
*   **Database:** SQLite
*   **UI Framework:** Streamlit
## 4. Installation & Setup
### 4.1. Prerequisites
* Python 3.13
	* `conda create -n myenv python=3.13`
* Install [Ollama](https://ollama.com)
* [UMLS](https://www.nlm.nih.gov/research/umls/index.html) API key
* [PubMed](https://account.ncbi.nlm.nih.gov/signup/) API key
### 4.2. Local Setup
1. **Clone the repository:**  `git clone git@github.com:s-david-kyle/Capstone2026_Spring.git`
2. **Navigate to the project directory:** `cd Capstone2026_Spring`
3. **Install Dependencies:** Switch to virtual environment created in step 4.1, and install packages using `pip install -r requirements.txt`
4. **Set up local LLM:**  Open up Ollama. Download the model of your choice. Open `config.py` and assign to `MODEL` variable. Example: `MODEL = 'gemma3:4b'` 
5. **Set up UMLS API key:** `export UMLS_API_KEY="YOUR_API_KEY"`
6. **Set up PubMed API key:** `export NCBI_API_KEY="YOUR_API_KEY"`
7. **Set up local database:**
	1. `cd dynamic_knowledge_graph`
	2. `python Initiate_db_creation.py`

## 5. Usage
* **Running the Application:** 
	* `cd dynamic_knowledge_graph`
	* `streamlit run patient_kg.py` (patient interface) or
	* `streamlit run doctor.py` (doctor interface)
* **Inputting Patient Data:** After entering a patient name, the UI will display patient questions, with a dialogue box for typing responses below. 
	* Continue engaging with the chatbot, typing responses and hitting enter
	* When the most specific symptom is found, the conversation will end and a summary will be generated.
	* Alternatively, the top left of the UI has a clickable << button which will display controls for ending the conversation
	* click "Finish & Generate Summary" or "Clear Chat / New Patient" to end the conversation
* **Interpreting Results:** The UI wil display pre and post summaries of patient conversations, the coversations themselves, and a knowledge graph of the conversation
    * Click the << button on the upper left if Session filters are not visible
    * Choose a patient session from the Choose session dropdown
    * Review Pre Summary and conversation
    * Relationships in the knowledge graph can be filtered by choosing available relationships and clicking the Filter relationships button
    * Enter additional notes in the Post Summary section, and click Save Post Summary to save them to the database

## 6. Code Structure

* `assets/`: Contains animated avatar files
* `docs/`: Research, diagrams, and slides used to demo project
* `db/`: Files needed to generate SQLite db
    * `patient_kg.py`:  Entry point for the patient application. Contains Streamlit interface, and all calls to llm and database functions.
    * `doctor.py`:  Entry point for the doctor application. Contains Streamlit interface, and all calls to database functions.
    * `llm_processing.py`: Contains the LLM interaction logic. Sets dialogue for patient interactions and extracting symptoms from patient statements.
    * `external_data_pull.py`: Contains API calls to external data sources, such as UMLS or PubMed.
    * `knowledge_graph.py`: Methods for manipulating knowledge graph structures
    * `db_write.py`: Updates the database with session, conversation, symptom, and summary information
    * `db_read.py`: Queries used for reading stored knowledge graphs, conversations, and more from database
    * `Initiate_db_creation.py` creates SQLite database
    * `db_tests.sql`: Queries to check database integrity
    * `misc_tests.ipynb`: Notebook for checking data integrity