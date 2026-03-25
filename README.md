# DUAL FRAMEWORK FOR STRUCTURED CLINICAL HISTORY-TAKING AND DIFFERENTIAL DIAGNOSIS GENERATION IN EMERGENCY CARE SETTINGS 

**A project to leverage Large Language Models for assisting physicians in diagnosis by extracting patient diagnoses and generating differential diagnoses.**
## 1. Overview
This project aims to build a system that utilizes a Large Language Model (LLM) to analyze patient clinical notes and accurately identify diagnoses. Furthermore, it will generate a prioritized list of differential diagnoses based on the extracted primary diagnosis and relevant contextual information. This tool is intended to support, not replace, the judgment of a qualified physician.
## 2. Features
* **Diagnosis Extraction:**  LLM-powered extraction of diagnoses from free-text clinical notes.
* **Differential Diagnosis Generation:**  Generates a ranked list of potential differential diagnoses based on the primary diagnosis and patient data.
* **User Interface (UI):** A web interface for inputting patient notes and viewing results.
* **Data Visualization:** **TBD**
## 3. Technology Stack
*   **LLM:** Llama, Gemma
*   **Programming Language:** Python
*   **Frameworks/Libraries:**  Ollama, NetworkX, yFiles
*   **Database (if applicable):** SQLite
*   **UI Framework (if applicable):** Streamlit
## 4. Installation & Setup
### 4.1. Prerequisites
* Python 3.12
	* `conda create -n myenv python=3.12`
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
	1. `cd src`
	2. `python Initiate_db_creation.py`
## 5. Usage
* **Running the Application:** 
	* `cd src`
	* `streamlit run patient.py` (patient interface) or
	* `streamlit run doctor.py` (doctor interface)
* **Inputting Patient Data:** The UI will display patient questions, with a dialogue box for typing responses below. 
	* Continue engaging with the chatbot, typing responses and hitting enter
	* The top left of the UI has a clickable << button which will display controls for ending the conversation
	* Click "Finish & Generate Summary" or "Clear Chat / New Patient" to end the conversation
* **Interpreting Results:** The UI wil display pre and post summaries of patient conversations, the coversations themselves, and a knowledge graph of the conversation
    * Click the << button on the upper left if Session filters are not visible
    * Choose a patient session from the Choose session dropdown
    * Review Pre Summary and conversation
    * Relationships in the knowledge graph can be filtered by choosing available relationships and clicking the Filter relationships button
    * Enter additional notes in the Post Summary section, and click Save Post Summary to save them to the database
## 6. Code Structure
*  `src/`: Contains the main application code.
    * `main.py`:  Entry point for the application. Contains Streamlit interface, and all calls to llm and database functions.
    * `llm_processing.py`: Contains the LLM interaction logic. Sets dialogue for patient interactions and extracting symptoms from patient statements.
    * `external_data_pull.py`: Contains API calls to external data sources, such as UMLS or PubMed.
    * `db_write.py`: Updates the database with session, conversation, symptom, and summary information
* `stable/`: Contains most recent stable application code. Updated only after testing performed in `src/` folder.
* `docs/`: Research notes and papers used to guide project
* `Database/`: Original code for initializing database. Includes template and documentation for designing database
* `proof_of_concept/`: Initial prototype of application
## 7. Contributing
TBD
## 8. License
TBD