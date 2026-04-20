
# ## Notes
# - Currently using local LLM at url in code below (Use Ollama, LMStudio, etc)
# - Create a python environment using `requirements.txt` to ensure you have all needed modules

from pprint import pprint
import re
import pandas as pd
import ollama
from datetime import datetime as dt
from config import MODEL

# team libraries
from db_read import (get_conversations, 
                     get_system_symptom_df, 
                     get_previous_drilldown_messages,
                     check_prev_rank_1,
                     retreive_system_symptom_kg,
                     check_symptom_rank_1,
                     check_session_consistency,
                     get_symptom_kg_df)
from knowledge_graph import convert_df_to_kg
from db_write import push_kg_to_db, push_ranking_to_db
from external_data_pull import umls_knowledge_graph

# external data needed for MTS dialogue doctor conversation mimic
mts_dialogue = pd.read_csv('data/mts_dialogue/MTS-Dialog-TrainingSet (SDHP).csv')

# API keys
from config import UMLS_API_KEY, NCBI_API_KEY, UMLS_PATH


# ==========================================
# PAADA'S ORIGINAL DIALOGUE FUNCTIONS 
# MODULAR BRAINS (LLM LOGIC)
# (capstone user interface.py)
# ==========================================

def get_llm_response(messages):
    """
    Handles the chat. Forces short, precise questions using SOCRATES.

    Args:
        messages (list): A list of message dictionaries, including a system instruction.
    Returns:
        str: The LLM's response as a string.
    """
    try:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a clinical intake bot. "
                "STRICT RULES: "
                "1. Ask only ONE question at a time. "
                "2. Keep responses under 15 words. "
                "3. No pleasantries or small talk. "
                "4. Be direct and precise."
            )
        }
        # Combines the system rules with the existing chat history
        # print(messages)
        response = ollama.chat(model=MODEL, messages=[system_instruction] + messages)
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

def generate_summary(messages):
    """
    Generates a summary of a patient interview.

    Args:
        messages (list): A list of message dictionaries representing the patient interview.
    Returns:
        str: A summary of the patient interview in a clinical note format.
    """
    try:
        # Formats the chat into a single string for easier summarization
        chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        summary_instruction = {
            "role": "system",
            "content": (
                "Summarize this patient interview into a professional clinical note. "
                "Include: Chief Complaint, Duration, Severity, and Associated Symptoms. "
                "Use bullet points. Max 60 words."
            )
        }
        
        response = ollama.chat(
            model=MODEL, 
            messages=[summary_instruction, {"role": "user", "content": chat_history}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Summary failed: {str(e)}"

# ==========================================
# SYMPTOM DIALOGUE FUNCTIONS
# ==========================================

def llm_symptom_check(prompt):
    """
    Checks a user's symptom statement against an Ollama LLM.

    Args:
        prompt (str): The user's symptom statement to analyze.

    Returns:
        list: A list of extracted symptoms from the LLM response.
              Returns an error message if an exception occurs.
    """
    try:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a clinical intake bot. "
                "STRICT RULES: "
                "1. List keywords for medical symptoms in this statement with bullet points and no additional information. "
                "2. Avoid vague singular words like 'pain'. "
                "3. No pleasantries or small talk. "
                "4. Be direct and precise."
            )
        }
        user_message = {"role": "user", "content": prompt}
        # print('symptom_check: ', user_message)
        # Combines the system rules with the existing chat history
        response = ollama.chat(model=MODEL, messages=[system_instruction] + [user_message])
        response = response['message']['content']
        symptoms = re.findall(r'\*\s[^\n]+', response)
        symptoms = [symptom.replace('* ', '') for symptom in symptoms]
        # remove any starting/ending spaces from each item
        symptoms = [symptom.strip() for symptom in symptoms]
        return symptoms
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"
    
def llm_single_symptom_check(prompt):
    """
    Checks a user's symptom statement against an Ollama LLM.

    Args:
        prompt (str): The user's symptom statement to analyze.

    Returns:
        list: A list of extracted symptoms from the LLM response.
              Returns an error message if an exception occurs.
    """
    try:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a clinical intake bot. "
                "STRICT RULES: "
                # "1. Come up with a single keyword to represent the medical symptom in this statement and no additional information. "
                "1. Come up with one to three words to represent the medical symptom in this statement and no additional information. "
                # "2. Avoid vague non-descriptive words like 'pain'. "
                # "2. Format the response in this format: ['keyword 1', 'keyword 2', 'keyword 3']"
                "2. Do not use any punctuation."
            )
        }
        user_message = {"role": "user", "content": prompt}
        # print('symptom_check: ', user_message)
        # Combines the system rules with the existing chat history
        response = ollama.chat(model=MODEL, messages=[system_instruction] + [user_message])
        response = response['message']['content']
        print('LLM symptom extracted:', response)
        # symptoms = re.findall(r'\*\s[^\n]+', response)
        # symptoms = [symptom.replace('* ', '') for symptom in symptoms]
        # remove any starting/ending spaces from each item
        # symptoms = [symptom.strip() for symptom in symptoms]
        return [response]  # returning as list to match previous constraint
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

def llm_question_formation(symptoms):
    """
    Formulates a clinical question based on a list of symptoms using a language model.

    Args:
        symptoms (str): A string containing a list of symptoms.

    Returns:
        str: A single, direct question formulated from the symptoms, or an error message if there was a problem.
    """
    try:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a clinical intake bot. "
                f"Take the following list of symptoms to form a question for a patient: {symptoms}"
                "STRICT RULES: "
                "1. Ask only ONE question at a time. "
                "2. Keep responses under 15 words. "
                "3. No pleasantries or small talk. "
                "4. Be direct and precise."
            )
        }
        response = ollama.chat(model=MODEL, messages=[system_instruction])
        response = response['message']['content']

        return response
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

# ==========================================
# MTS DIALOGUE FUNCTIONS
# (metapub_llm proof of concept)
# ==========================================

def llm_process_mts_dialogue(dialogues, patient_question):
    """
    Processes a dialogue and patient question to generate a follow-up question.

    Args:
        dialogues (str): A string containing the dialogue examples.
        patient_question (str): The patient's original question.

    Returns:
        str: A follow-up question generated by the LLM, or an error message if an exception occurs.
    """
    try:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a clinical intake bot. "
                "Use the following dialogue examples and the original patient question to generate a question that will give more insight into the patient's symptoms:"
                f"Patient question: {patient_question}. Dialogue examples: {dialogues}"
                "STRICT RULES: "
                "1. Ask only ONE question at a time. "
                "2. Keep responses under 15 words. "
                "3. No pleasantries or small talk. "
                "4. Be direct and precise."
                "5. Include only a question in the response"
            )
        }
        response = ollama.chat(model=MODEL, messages=[system_instruction])
        response = response['message']['content']

        return response
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

def extract_text(text):
    """
    Extracts symptoms from a text string using a regular expression,
    the text between 'Symptoms: ' and 'Diagnosis: '.
    Doctor_dialogue_mimic helper function.
    
    Args:
        text (str): The input text string.

    Returns:
        str or None: The extracted symptoms string if found, otherwise None.
    """
    match = re.search(r"Symptoms: (.*?)\nDiagnosis: ", text)
    if match:
        return match.group(1)
    else:
        return None

def remove_floats(text):
    """
    Removes numeric values from a string. Doctor_dialogue_mimic helper function.

    Args:
        text (str): The input string.

    Returns:
        str: The string with numeric values removed.
    """
    if isinstance(text, (int, float)):
        return ''  # Replace numeric values with an empty string
    else:
        return text

def doctor_dialogue_mimic(symptoms, patient_question):
    """
    Generates a follow-up question based on patient symptoms and dialogue examples.

    Args:
        symptoms (str): A string containing the patient's symptoms.
        patient_question (str): The patient's original question.

    Returns:
        tuple: A tuple containing the generated question, a boolean indicating whether
               the `mts_dialogue` method was used, and the processed dialogue string.
    """
    # flag for checking use of mts_dialogue method
    mts_dialogue_used = False
    # variable for combined dialogues based on symptoms
    processed_dialogue = ''

    # use regex to extract only symptoms from section_text column
    mts_dialogue['extracted_text'] = mts_dialogue['section_text'].apply(extract_text)
    mts_dialogue['extracted_text'] = mts_dialogue['extracted_text'].apply(remove_floats)

    # handle if no symptoms found
    if symptoms is not None:
        # take extracted_text closest to patient statement
        dialogues = mts_dialogue[mts_dialogue['extracted_text'].apply(lambda text: text is not None and any(item in text for item in symptoms))]
    else:
        dialogues = None

    # handle None return type if no matches in mts_dialogue
    if dialogues is not None:
        # extract all dialogues and place into a string to feed to LLM
        for index, row in dialogues.iterrows():
            processed_dialogue += f"\ndialogue {index}: {row['dialogue']} "
        # print(processed_dialogue)
        question = llm_process_mts_dialogue(processed_dialogue, patient_question)
        mts_dialogue_used = True
    else:
        # generate general question using symptoms only if no dialogue available
        question = llm_question_formation(symptoms)
        mts_dialogue_used = False
        processed_dialogue = ''

    return question, mts_dialogue_used, processed_dialogue

# ==========================================
# KNOWLEDGE GRAPH FUNCTIONS
# ==========================================

def llm_process_knowledge_graph(session):
    """
    Processes conversation dialogue to extract knowledge graph components.

    Args:
        session (int): the SessionId to filter conversations.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the extracted 
        'head', 'relation', and 'tail' components from the 
        conversation dialogue.
    """
    # read in coversation for the current session
    df = get_conversations(session)
    # convert conversation to single string
    result = ""
    for index, row in df.iterrows():
        speaker = row["Speaker"]
        message = row["Message"]
        result += f"'{speaker}: {message}'"
    # TODO: add a list of source nodes to build off of
    """
    Constitutional: fever, chills, night sweats, fatigue, weakness, weight loss, weight gain, loss of appetite
    Cardiovascular: chest pain, chest pressure/tightness, palpitations, irregular heartbeat, syncope, near syncope, orthopnea, paroxysmal nocturnal dyspnea, exertional dyspnea, leg swelling, Claudication
    Respiratory: shortness of breath, cough, sputum production, hemoptysis, wheezing, chest congestion, pleuritic pain
    Gastrointestinal: abdominal pain, nausea, vomiting, diarrhea, constipation, blood in stool, heartburn, bloating, loss of appetite
    Genitourinary: dysuria, urinary frequency, urgency, hematuria, flank pain, incontinence, vaginal bleeding, vaginal discharge, pregnancy status, testicular pain
    Neurological: headache, dizziness, lightheadedness, syncope, weakness, numbness, tingling, seizures, confusion, memory loss, speech difficulty, vision changes
    Musculoskeletal: joint pain, muscle pain, back pain, neck pain, joint swelling, stiffness, limited range of motion
    Skin: rash, itching, lesions, bruising, changes in moles, hair loss
    Endocrine: heat intolerance, cold intolerance, excessive thirst, excessive urination, excessive hunger
    Hematologic/Lymphatic: easy bruising, easy bleeding, swollen lymph nodes, anemia symptoms
    Psychiatric: anxiety, depression, mood changes, sleep disturbances, suicidal ideation, hallucinations
    Pertinent positives
    Pertinent negatives
    PMH / PSH
    Medications
    Allergies
    Social factors 
    Missing clarifications – this will be useful for estimating the coverage counts etc. 
    Flags (red-flag prompts)
    """
    # TODO: add try/catch to prevent crashes if parsing fails
    # try:
    system_instruction = {
        "role": "system",
        "content": (
            "You parse doctor and patient dialogue into three components that summarize the patient's attributes and symptoms"
            f"Use the following dialogue: {result}"
            "STRICT RULES: "
            "Each relationship you see in the dialogue can only be one of the following: "
            "1. Head: a concept or idea. "
            "2. Relation: the relationship attached the concept or idea. "
            "3. Tail: the concept or idea that the relationship connects to the head."
            "4. Format the text as: Head, Relation, Tail value;"
            "5. All relations must be one of these values: Constitutional, Cardiovascular, Respiratory, Gastrointestinal, Genitourinary, Neurological, Musculoskeletal, or Skin"
            "6. Only include the formatted text in the response."
        )
    }
    response = ollama.chat(model=MODEL, messages=[system_instruction])
    response = response['message']['content']
    # print(response)

    # Split the string into individual entries
    entries = response.strip().split('; ')
    # print(entries)

    # Create an empty list to store the data
    df_data = []

    # Iterate over the entries and extract the Head, Relation, and Tail
    for entry in entries:
        parts = entry.split(', ')
        head = parts[0]
        relation = parts[1]
        tail = parts[2]
        df_data.append({'head': head, 'relation': relation, 'tail': tail})
    
    # Create the pandas DataFrame
    # print(df_data)
    df = pd.DataFrame(df_data)
    return df
    
    # except Exception as e:
    #     return None
    #     # return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

def system_grouping(df, symptom, selected_session, turn_number):
    # generate system groupings for tail column data
    # use only symptoms for now
    df = df[df['semantic_type'] == 'Sign or Symptom'].copy()
    symptom_list = df['symptom'].tolist()
    # remove system searched for in UMLS
    if symptom in symptom_list:
        symptom_list.remove(symptom)
    # prep list for LLM
    symptom_string = ', '.join(symptom_list)
    # edges list (DKG-LLM)
    edges = [
        "Causal",
        "Therapeutic",
        "Associative",
        "Contraindicative",
        "Diagnostic",
        "Preventive",
        "Exacerbative",
        "Ameliorative",
        "Temporal",
        "Dosage-Related",
        "Side Effect",
        "Interaction",
        "Epidemiological",
        "Genetic",
        "Allergic",
        "Monitoring",
        "Supportive",
        "Concomitant",
        "Risk-Associated",
        "Symptom-Symptom",
        "Procedure-Related",
        "Outcome-Related",
        "Age-Related",
        "Lifestyle-Related",
        "Biomarker-Related",
        "Comorbidity-Related"
    ]
    edge_string = ', '.join(edges)
    # llm prompt
    # TODO: the 2 biological systems requirement will need to be modified when drilldown to final system is reached
    system_instruction = {
        "role": "system",
        "content": (
            "Assign a biological system (examples: musculoskeletal system, urinary system) to each item in the following list of symptoms:"
            f"{symptom_string} and the relation to the system using these relationships: {edge_string}"
            "STRICT RULES: "
            "The response must be formatted as followed: "
            "1. Each symptom must be followed by an :  the relationship : the biological system "
            "2. Each symptom, biological system, and relationship must be followed by a newline "
            # "3. There must be at least 2 biological systems"
            "3. Do not use diagnoses for biological systems"
            "4. Only include this formatted text in the response, do not add number to rows."
            "5. DO NOT NUMBER ROWS. "
        )
    }
    response = ollama.chat(model=MODEL, messages=[system_instruction])
    response = response['message']['content']
    # print(response)
    # Parse response into dataframe
    lines = response.strip().split('\n')
    data = []
    for line in lines:
        # print('LLM response for KG:', line)
        # match = re.match(r"(\d+\.) (\w+) : (\w+)", line)
        # match = re.match(r"^\d+\.\s*(.*?)\s+:\s+(.*)$", line)
        match = re.match(r"([^:]+)\s+:\s+([^:]+)\s+:\s+([^:]+)", line)
        if match:
            # formatting symptom - relation - system
            symptom = match.group(1)
            relationship = match.group(2)
            system = match.group(3)
            data.append({'symptom': symptom, 'system': system, 'relation': relationship})
    symptom_system = pd.DataFrame(data)
    print(symptom_system)

    # create a graph out of this with each system as it's own central node
    symptom_kg_df = symptom_system.copy()
    symptom_kg_df.columns = ['tail', 'head', 'relation']
    # symptom_kg_df['relation'] = 'symptom'
    symptom_kg = convert_df_to_kg(symptom_kg_df)

    # push this to database - include session number and turn number
    # temporary assignment
    symptom_system['turn'] = turn_number
    push_kg_to_db(symptom_system, 
                  selected_session, 
                  'SymptomSystemKG', 
                  overwrite=False,
                  continue_session=True)
    return symptom_kg

def symptom_grouping(df, freq_symptom, selected_session, turn_number, question_phase):
    # generate system groupings for tail column data
    # comment out if you want to broaden results to Finding, Intellectual Product, Pathologic Function, etc
    # TODO: remove this condition for more comprehensive drill-down
    df = df[df['semantic_type'] == 'Sign or Symptom'].copy()
    # print(df.head())
    symptom_list = df['symptom'].tolist()
    
    # lowercase both symptom_list and freq_symptom values for accurate removal
    symptom_list = [symptom.lower() for symptom in symptom_list]
    freq_symptom = freq_symptom.lower()

    print(f'Symptom list before removal of {freq_symptom}: {symptom_list}')
    # remove system searched for in UMLS
    if freq_symptom in symptom_list:
        symptom_list.remove(freq_symptom)
    print(f'{len(symptom_list)} UMLS symptom(s) pulled from {freq_symptom}: {symptom_list}')
    # TODO: if list is only one item move onto final phase
    if len(symptom_list) > 1:
        # prep list for LLM
        symptom_string = ', '.join(symptom_list)
        # edges list (DKG-LLM)
        edges = [
            "Causal",
            "Therapeutic",
            "Associative",
            "Contraindicative",
            "Diagnostic",
            "Preventive",
            "Exacerbative",
            "Ameliorative",
            "Temporal",
            "Dosage-Related",
            "Side Effect",
            "Interaction",
            "Epidemiological",
            "Genetic",
            "Allergic",
            "Monitoring",
            "Supportive",
            "Concomitant",
            "Risk-Associated",
            "Symptom-Symptom",
            "Procedure-Related",
            "Outcome-Related",
            "Age-Related",
            "Lifestyle-Related",
            "Biomarker-Related",
            "Comorbidity-Related"
        ]
        edge_string = ', '.join(edges)
        # llm prompt
        # this will hallucinate nodes when there are no connections to make
        system_instruction = {
            "role": "system",
            "content": (
                f"Assign a relationship to the primary symptom {freq_symptom} using the following list of symptoms:"
                f"{symptom_string}, and its relations using these relationships: {edge_string}"
                "STRICT RULES: "
                "The response must be formatted as followed: "
                "1. Primary system : relationship : related symptom "
                # "1. The primary symptom must be followed by an :  the relationship : the related symptom "
                "2. An example would be Itchy scalp : Symptom-Symptom : Pruritus of scalp"
                "3. Each primary symptom, relationship, and related system must be followed by a newline "
                "4. Only include this formatted text in the response, do not add number to rows."
            )
        }
        response = ollama.chat(model=MODEL, messages=[system_instruction])
        response = response['message']['content']
        # print(response)
        # Parse response into dataframe
        lines = response.strip().split('\n')
        data = []
        for line in lines:
            print('LLM response for KG:', line)
            # match = re.match(r"(\d+\.) (\w+) : (\w+)", line)
            # match = re.match(r"^\d+\.\s*(.*?)\s+:\s+(.*)$", line)
            match = re.match(r"([^:]+)\s+:\s+([^:]+)\s+:\s+([^:]+)", line)
            if match:
                # formatting symptom - relation - system
                kg_symptom = match.group(1)
                relationship = match.group(2)
                system = match.group(3)
                data.append({'symptom': kg_symptom, 'system': system, 'relation': relationship})
        symptom_system = pd.DataFrame(data)
        print(symptom_system)

        # create a graph out of this with each system as it's own central node
        # TODO: check symptom_kg_df and symptom_system are being used correctly here
        symptom_kg_df = symptom_system.copy()
        symptom_kg_df.columns = ['tail', 'head', 'relation']
        # symptom_kg_df['relation'] = 'symptom'
        symptom_kg = convert_df_to_kg(symptom_kg_df)

        # push this to database - include session number and turn number
        # temporary assignment
        symptom_system['turn'] = turn_number
        push_kg_to_db(symptom_system, 
                    selected_session, 
                    'SymptomSystemKG', 
                    overwrite=False,
                    continue_session=True)
    else:
        # making basic 1 node knowledge graph which relates to itself
        symptom_kg = pd.DataFrame({'symptom': [freq_symptom],
                                   'system': [freq_symptom],
                                   'relation': ['symptom-symptom'],
                                   'turn': [turn_number]})
        # TODO: push this dataframe to database (check column names, mimic push above)
        push_kg_to_db(symptom_kg, 
                    selected_session, 
                    'SymptomSystemKG', 
                    overwrite=False,
                    continue_session=True)
        # move onto final phase of question (diagnosis)
        question_phase +=1
    return symptom_kg, question_phase

def form_system_question(session_id, turn_number, symptom):
    """
    Forms a question to narrow down affected systems
    """
    # pull a list of the current systems
    df = get_system_symptom_df(session_id, turn_number)
    systems = df['system'].drop_duplicates().to_list()
    # convert list to a string and feed to LLM to form question
    systems_str = ", ".join(systems)
    try:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a clinical intake bot. "
                f"""Take the following list of biological systems: {systems_str} and 
                    form a question that narrows down which system to focus on for a 
                    patient with a symptom of {symptom}
                """
                "STRICT RULES: "
                "1. Ask only ONE question at a time. "
                "2. Keep responses under 15 words. "
                "3. Make sure language is easily understandable and non-threatening. "
                "4. Refer to biological systems in layman's terms that anyone could understand. "
                "5. Assume the patient cannot describe the systems themselves, and refer to something they may feel or see. "
                "6. No pleasantries or small talk. "
                # "6. Be direct and precise."
            )
        }
        response = ollama.chat(model=MODEL, messages=[system_instruction])
        response = response['message']['content']
    except Exception as e:
        response =  f"⚠️ Error: Ensure Ollama is running. ({str(e)})"
    return response

def drilldown_system(session_id, turn_number, symptom, prompt, drilldown_start, current_phase):
    
    # ----------------------------------------------------
    # Pull most recent KG, extract systems list
    # ----------------------------------------------------
    
    # query DB with session_id, turn_number
    df = get_system_symptom_df(session_id, turn_number)
    # print('drilldown system:', df)
    # pull unique systems
    systems = df['system'].unique().tolist()
    systems_str = ", ".join(systems)

    # ----------------------------------------------------
    # Rank systems
    # ----------------------------------------------------

    # code to rank KG systems
    system_instruction = {
        "role": "system",
        "content": (
            "You are a clinical intake bot. "
            f"""Take the following list of biological systems: {systems_str} and 
                a patient that has stated: {prompt}, and rank the systems in the
                order that they may likely the most affected based on patient statement.
            """
            "STRICT RULES: "
            "The response must be formatted as followed: "
            "1. Show the ranking number, followed by a colon and then the system"
            "2. Only include this formatted text in the response"
            "3. Do not include any notes or explanations"
        )
    }
    response = ollama.chat(model=MODEL, messages=[system_instruction])
    response = response['message']['content']
    # except Exception as e:
    #     response =  f"⚠️ Error: Ensure Ollama is running. ({str(e)})"
        
    # parse and log rankings in the database
    lines = response.strip().split('\n')
    data = [] # store rankings here
    for line in lines:
        match = re.match(r"(\d+): (.*)", line)
        if match:
            # formatting symptom - relation - system
            rank = int(match.group(1))
            relationship = match.group(2)
            data.append({'rank': rank, 'system': relationship})
    system_rank = pd.DataFrame(data)
    # print('system_rank df:', system_rank)
    
    # log rank, system, session_id, turn_number, something to indicate start of drilldown
    system_rank['SessionId'] = session_id
    system_rank['turn_number'] = turn_number + 1 # was decremented before function call
    system_rank['drilldown_start'] = drilldown_start
    system_rank['timestamp'] = dt.now()
    push_ranking_to_db(system_rank, 'SystemRank', session_id)
        
    # ----------------------------------------------------
    # Duplicate KG to show it was used in this conversation turn
    # ----------------------------------------------------

    # push last symptom system kg to SymptomSystemKg (will be redundant but tell story)
    symptom_system_kg = get_system_symptom_df(session_id, turn_number)
    symptom_system_kg['turn'] = turn_number + 1 # was decremented before function call
    push_kg_to_db(symptom_system_kg, 
                session_id, 
                'SymptomSystemKG', 
                overwrite=False,
                continue_session=True)
    
    # ----------------------------------------------------
    # Branching for drilldown start, current phase
    # 1. Drilldown Start
    #   - Generated question factors biological systems list, initial 
    #     symptom query sent to UMLS, and first user prompt
    #   - Only runs once (drilldown_start set to False after)
    # After Drilldown Start (regardless of Current Phase 2 or 3):
    #   - Retrieves previous conversation messages
    #       - Pulls most recent timestamp from SystemRank table for 
    #         session with drilldown_start flag set to 1
    #       - Pulls all conversations from Turn table with datetime
    #         greater or equal to most recent timestamp with
    #         drilldown start flag set
    #   - Checks ranking for systems to see if there a 3 matches
    #       - If 3 matches, current_phase is set to 3
    #       - If not 3 matches, current_phase stays at 2
    # 2. Current phase = 2
    #   - Generated question factors previous messages, biological 
    #     systems list, and intial symptom used to query UMLS
    # 3. Current phase = 3
    #   - EVALUATE IF THIS NEEDS TO BE HERE
    #   - Filters initial knowledge graphs to selected system
    #       - There are issues with this - especially if that system
    #         has few nodes attached
    #       - Consider querying UMLS with system and initial symptom
    #         to generate new nodes
    #   - Generated question factors in filtered symptom_list and
    #     previous messages
    # ----------------------------------------------------
    
    # branch here if drilldown_start is false (will want all conversations from start)
    print('Drilldown start: ', drilldown_start)
    if drilldown_start:
    # ask next question, factoring in prompt and list of systems
        try:
            system_instruction = {
                "role": "system",
                "content": (
                    "You are a clinical intake bot. "
                    f"""Take the following list of biological systems: {systems_str} and 
                        form a question that narrows down which system to focus on for a 
                        patient with a symptom of {symptom} who has said: {prompt}
                    """
                    "STRICT RULES: "
                    "1. Ask only ONE question at a time. "
                    "2. Keep responses under 15 words. "
                    "3. Make sure language is easily understandable and non-threatening. "
                    "4. Refer to biological systems in layman's terms that anyone could understand. "
                    "5. Assume the patient cannot describe the systems themselves, and refer to something they may feel or see. "
                    "6. Do not mention the biological system you are focusing on. "
                    "7. No pleasantries or small talk. "
                    # "6. Be direct and precise."
                )
            }
            response = ollama.chat(model=MODEL, messages=[system_instruction])
            response = response['message']['content']
        except Exception as e:
            response =  f"⚠️ Error: Ensure Ollama is running. ({str(e)})"
    else:
        # query database where drilldown_start is false, and grab previous messages
        drilldown_conversation, drilldown_datetime = get_previous_drilldown_messages(session_id)
        print(f'Drilldown conversation: \n{drilldown_conversation}')
        # start from turn where drilldown start is true (first true since current turn)
        # pull rank 1 systems for all previous rankings and see if there are 3 reoccuring
        freq_system = check_prev_rank_1(session_id, drilldown_datetime)
        # if there are 3 matches for rank 1 system, decide on that system, turn off system drill down 
        if freq_system:
            print(f'Will focus on: {freq_system}')
            # modify some phase var to move out of this phase
            current_phase = 3
        else:
            print('Still locating system for focus')
            current_phase = 2
        # skip this after focus found
        if current_phase == 2:
            # generate next question to drill down on system
            try:
                system_instruction = {
                    "role": "system",
                    "content": (
                        "You are a clinical intake bot. "
                        f"""Take the following list of biological systems: {systems_str} and 
                            form a question that narrows down which system to focus on for a 
                            patient with a symptom of {symptom}. Use these previous messages for 
                            context: {drilldown_conversation}.
                        """
                        "STRICT RULES: "
                        "1. Ask only ONE question at a time. "
                        "2. Keep responses under 15 words. "
                        "3. Make sure language is easily understandable and non-threatening. "
                        "4. Refer to biological systems in layman's terms that anyone could understand. "
                        "5. Assume the patient cannot describe the systems themselves, and refer to something they may feel or see. "
                        "6. Do not mention the biological system you are focusing on. "
                        "7. Do not repeat any questions the system has asked previously. "
                        "8. No pleasantries or small talk. "
                        # "6. Be direct and precise."
                    )
                }
                response = ollama.chat(model=MODEL, messages=[system_instruction])
                response = response['message']['content']
            except Exception as e:
                response =  f"⚠️ Error: Ensure Ollama is running. ({str(e)})"
        elif current_phase == 3:
            # TODO: replace following steps with query to UMLS with system and initial 
            # symptom to generate new nodes, and push these to KG table
            # freq_system + symptom
            new_umls_term = (freq_system + ' ' + symptom[0]).lower()
            new_symptoms_df = umls_knowledge_graph(new_umls_term, 50, partial_search=True)
            symptom_system_graph, question_phase = symptom_grouping(new_symptoms_df, 
                                            freq_system, 
                                            session_id, 
                                            turn_number + 2, # see if needs to be 2 or 1
                                            3) # symptom drilldown question_phase
            # TODO: switch this to system and test (was symptom) should smooth transition
            symptom_list = new_symptoms_df['symptom'].drop_duplicates().tolist()
            # TODO: verify above knowledge graph generation works before removing lines below
            # # filter current kg down to system
            # system_symptom_df = get_system_symptom_df(session_id, turn_number)
            # system_symptom_df = system_symptom_df[system_symptom_df['system'] == freq_system]
            # # push this kg to the SymptomSystemKG
            # system_symptom_df['turn'] = turn_number + 2  # needed to place in proper order
            # push_kg_to_db(system_symptom_df, 
            #                 session_id, 
            #                 'SymptomSystemKG', 
            #                 overwrite=False,
            #                 continue_session=True)
            # # generate a question from the list of symptoms in KG
            # # TODO: filtering here often creates random questions unrelated to previous questions
            # # this is more pronounced when it filters to a system with few nodes
            # symptom_list = system_symptom_df['symptom'].drop_duplicates().tolist()
            symptom_list = ", ".join(symptom_list)
            print('Phase 3 transition start, filtered symptom list: ', symptom_list)
            try:
                system_instruction = {
                    "role": "system",
                    "content": (
                        "You are a clinical intake bot. "
                        f"""Take the following list of symptoms: {symptom_list} and 
                            form a question that narrows down which symptom to focus on for a 
                            patient. Use these messages for context: {drilldown_conversation}.
                        """
                        "STRICT RULES: "
                        "1. Ask only ONE question at a time. "
                        "2. Keep responses under 15 words. "
                        "3. Make sure language is easily understandable and non-threatening. "
                        "4. Refer to symptoms in layman's terms that anyone could understand. "
                        # "5. Assume the patient cannot describe the exact symptoms themselves, and refer to something they may feel or see. "
                        # "6. Do not mention the biological system you are focusing on. "
                        "5. No pleasantries or small talk. "
                        # "6. Be direct and precise."
                    )
                }
                response = ollama.chat(model=MODEL, messages=[system_instruction])
                response = response['message']['content']
            except Exception as e:
                response =  f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

    # indicates symptom_drilldown_start is over
    drilldown_start = False
    # need to add extra turn since decremented for this function
    return response, turn_number + 2, drilldown_start, current_phase

def drilldown_symptom(prompt, session_id, turn_number, question_phase, symptom_phase):
    # pull a list of the symptoms from db (SymptomSystemKG)
    # TODO: uncomment once tables are created
    # check_session_consistency()

    # ----------------------------------------------------
    # Pull most recent KG, extract symptoms list
    # ----------------------------------------------------

    # TODO: see if this is failing to pull recent data
    system_symptom_df = get_symptom_kg_df(session_id)
    # TODO: switch this to system to see if it accurately pulls related symptoms (was symptom)
    # try for symptom_phase = 1 use symptom, symptom_phase > 1 use system
    # chart is symptom-only, and system field shows related symptoms
    print(f'Symptom phase: {symptom_phase}\nSessionID: {session_id}\nTurn: {turn_number}\n system_symptom_df:\n {system_symptom_df}')
    # symptom_list = system_symptom_df['symptom'].drop_duplicates().tolist()
    # TODO: check that this works (should be with smoother transition from phase 2)
    symptom_list = system_symptom_df['system'].drop_duplicates().tolist()
    # if symptom_phase > 1:
    #     symptom_list = system_symptom_df['system'].drop_duplicates().tolist()
    # # chart resembles structure from step 2 system investigation
    # else:
    #     symptom_list = system_symptom_df['symptom'].drop_duplicates().tolist()

    print('Drilldown symptom list:', symptom_list)

    # ----------------------------------------------------
    # Pull session discussions
    # ----------------------------------------------------

    # pull history of discussion from db (Turn)
    discussion = get_conversations(session_id)
    result = ""
    for index, row in discussion.iterrows():
        speaker = row["Speaker"]
        message = row["Message"]
        result += f"'{speaker}: {message}'"


    # ----------------------------------------------------
    # Rank symptoms
    # ----------------------------------------------------

    # create a new ranking of symptoms (store in new SymptomRank table)
    system_instruction = {
        "role": "system",
        "content": (
            "You are a clinical intake bot. "
            f"""Take the following list of symptoms: {symptom_list} and 
                the discussion that has stated: {discussion}, and rank the symptoms in the
                order that they may likely the most affected based on the discussion.
            """
            "STRICT RULES: "
            "The response must be formatted as followed: "
            "1. Show the ranking number, followed by a colon and then the symptom"
            "2. An example would be 1: Generalized pruritus"
            "3. Only include this formatted text in the response"
            "4. Do not include any notes or explanations"
        )
    }
    response = ollama.chat(model=MODEL, messages=[system_instruction])
    response = response['message']['content']
    
    # parse and log rankings in the database
    lines = response.strip().split('\n')
    data = [] # store rankings here
    for line in lines:
        # TODO: there may be an issue if there's no match made here, add test for 2 groups
        # TODO: sometimes it creates 1. Generalized pruritus instead of 1: Generalized pruritus
        # An error occurred: single positional indexer is out-of-bounds
        match = re.match(r"(\d+): (.*)", line)
        if match:
            # formatting symptom - relation - system
            rank = int(match.group(1))
            relationship = match.group(2)
            data.append({'rank': rank, 'symptom': relationship})
    print('Symptom rank LLM-parsed rankings: ', data)  #, lines)
    symptom_rank = pd.DataFrame(data)
    # print('symptom_rank df:', symptom_rank)
    # log rank, system, session_id, turn_number, something to indicate start of drilldown
    symptom_rank['SessionId'] = session_id
    symptom_rank['turn_number'] = turn_number
    symptom_rank['timestamp'] = dt.now()
    symptom_rank['symptom_phase'] = symptom_phase
    push_ranking_to_db(symptom_rank, 'SymptomRank', session_id)

    # ----------------------------------------------------
    # Check rankings for most prominent symptom
    # ----------------------------------------------------

    # pull rank 1 systems for all previous rankings and see if there are 3 reoccuring
    # TODO: this seems to take one extra turn for some reason
    freq_symptom = check_symptom_rank_1(session_id, symptom_phase)
    # when there are 3 matches:
    if freq_symptom:
        print(f'Will focus on: {freq_symptom}')
        # modify some phase var to move out of this phase
        symptom_phase += 1
        # trigger UMLS query for freq_symptom
        new_symptoms_df = umls_knowledge_graph(freq_symptom, 50)
        # print('New symptoms pulled from UMLS: ', new_symptoms_df)
        symptom_system_graph, question_phase = symptom_grouping(new_symptoms_df, 
                                            freq_symptom, 
                                            session_id, 
                                            turn_number + 1,
                                            question_phase)
        # TODO: update symptom_list here so that next question is valid
        system_symptom_df = get_symptom_kg_df(session_id)
        # symptom_list = system_symptom_df['symptom'].drop_duplicates().tolist()
        symptom_list = system_symptom_df['system'].drop_duplicates().tolist()
    else:
        print('Still locating symptom for focus')

    # ----------------------------------------------------
    # Generate next question
    # ----------------------------------------------------

    # generate next question
    # TODO: this overwrites previous symptom_list - compare with symptom drilldown output
    # symptom_list = symptom_rank['symptom'].drop_duplicates().tolist()
    symptom_list = ", ".join(symptom_list)
    print(f'\n\nSession: {session_id}, turn: {turn_number}, question_phase: {question_phase}, symptom_phase: {symptom_phase} \n \
            Question generated with symptom_list: {symptom_list}')
    try:
        system_instruction = {
            "role": "system",
            "content": (
                "You are a clinical intake bot. "
                f"""Take the following list of symptoms: {symptom_list} and 
                    form a question that narrows down which symptom to focus on for a 
                    patient. Use these messages for context: {discussion}.
                """
                "STRICT RULES: "
                "1. Ask only ONE question at a time. "
                "2. Keep responses under 15 words. "
                "3. Make sure language is easily understandable and non-threatening. "
                "4. Refer to symptoms in layman's terms that anyone could understand. "
                "5. Assume the patient cannot describe the exact symptoms themselves, and refer to something they may feel or see. "
                # "6. Do not mention the biological system you are focusing on. "
                "6. No pleasantries or small talk. "
                # "6. Be direct and precise."
            )
        }
        response = ollama.chat(model=MODEL, messages=[system_instruction])
        response = response['message']['content']
    except Exception as e:
        response =  f"⚠️ Error: Ensure Ollama is running. ({str(e)})"
    # response = '2nd question to narrow down system from freq_system'
    # need to add extra turn since decremented for this function
    return response, turn_number + 1, question_phase, symptom_phase

if __name__ == "__main__":
    pass
    # conversation_log, symptom_log, article_log, umls_log = surface_patient_information(patient_statement_01)
