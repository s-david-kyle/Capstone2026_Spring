
# ## Notes
# - Currently using local LLM at url in code below (Use Ollama, LMStudio, etc)
# - Create a python environment using `requirements.txt` to ensure you have all needed modules

import json
from pprint import pprint
import re
import pandas as pd
import ollama

# external data needed for doctor conversation mimic
mts_dialogue = pd.read_csv('data/mts_dialogue/MTS-Dialog-TrainingSet (SDHP).csv')

# API keys
from config import UMLS_API_KEY, NCBI_API_KEY, UMLS_PATH

def ollama_llm_symptom_check(prompt, model):
    """
    Queries the LLM API.
    Returns back a list of symptoms based off of patient statement made
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
        response = ollama.chat(model=model, messages=[system_instruction] + [user_message])
        response = response['message']['content']
        symptoms = re.findall(r'\*\s[^\n]+', response)
        symptoms = [symptom.replace('* ', '') for symptom in symptoms]
        # remove any starting/ending spaces from each item
        symptoms = [symptom.strip() for symptom in symptoms]
        return symptoms
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

def llm_question_formation(symptoms, model):
    """Queries the LLM API."""
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
        response = ollama.chat(model=model, messages=[system_instruction])
        response = response['message']['content']

        return response
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

def llm_process_mts_dialogue(dialogues, patient_question, model):
    """
    Looks at sample dialogues on related topic, generates new question
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
        response = ollama.chat(model=model, messages=[system_instruction])
        response = response['message']['content']

        return response
    except Exception as e:
        return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

def extract_text(text):
    """Extracts text between 'Symptoms: ' and 'Diagnosis: '."""
    match = re.search(r"Symptoms: (.*?)\nDiagnosis: ", text)
    if match:
        return match.group(1)
    else:
        return None

def remove_floats(text):
    """Removes float values from the text, keeping only text."""
    if isinstance(text, (int, float)):
        return ''  # Replace numeric values with an empty string
    else:
        return text

def doctor_dialogue_mimic(symptoms, patient_question, model):
    """
    do a search in section_text to find matching dialogues with patient symptoms
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
        # dialogues = mts_dialogue[mts_dialogue['extracted_text'].apply(lambda text: any(item in text for item in symptoms))]
        dialogues = mts_dialogue[mts_dialogue['extracted_text'].apply(lambda text: text is not None and any(item in text for item in symptoms))]
    else:
        dialogues = None

    # handle None return type if no matches in mts_dialogue
    if dialogues is not None:
        # extract all dialogues and place into a string to feed to LLM
        for index, row in dialogues.iterrows():
            processed_dialogue += f"\ndialogue {index}: {row['dialogue']} "
        # print(processed_dialogue)
        question = llm_process_mts_dialogue(processed_dialogue, patient_question, model)
        mts_dialogue_used = True
    else:
        # generate general question using symptoms only if no dialogue available
        question = llm_question_formation(symptoms, model)
        mts_dialogue_used = False
        processed_dialogue = ''

    return question, mts_dialogue_used, processed_dialogue

if __name__ == "__main__":
    pass
    # conversation_log, symptom_log, article_log, umls_log = surface_patient_information(patient_statement_01)
