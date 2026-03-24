
# ## Notes
# - Currently using local LLM at url in code below (Use Ollama, LMStudio, etc)
# - Create a python environment using `requirements.txt` to ensure you have all needed modules

from pprint import pprint
import re
import pandas as pd
import ollama
from config import MODEL

# team libraries
from db_read import get_conversations

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
    Converts conversation to knowledge graph
    """
    # read in coversation for the current session
    df = get_conversations(session)
    # TODO: convert conversation to single string
    result = ""
    for index, row in df.iterrows():
        speaker = row["Speaker"]
        message = row["Message"]
        result += f"'{speaker}: {message}'"

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
            "5. Only include the formatted text in the response."
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

if __name__ == "__main__":
    pass
    # conversation_log, symptom_log, article_log, umls_log = surface_patient_information(patient_statement_01)
