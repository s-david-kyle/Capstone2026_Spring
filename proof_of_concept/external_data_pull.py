#!/usr/bin/env python
# coding: utf-8

# # MetaPub
# 
# ## Documentation links
# - https://metapub.org
# - https://metapub.readthedocs.io/en/latest/examples.html
# - https://metapub.readthedocs.io/en/latest/pubmedarticle_properties.html
# 
# ## Notes
# - Using an API key requires env variable to be set
#   - `export NCBI_API_KEY="Your_key_here"`
# - Currently using local LLM at url in code below (Use Ollama, LMStudio, etc)
# - Create a python environment using `requirements.txt` to ensure you have all needed modules



from metapub import PubMedFetcher
import requests
import json
from pprint import pprint
import re
import pandas as pd
import os
from umls_python_client import UMLSClient
import ollama

# API keys
from config import UMLS_API_KEY, NCBI_API_KEY, UMLS_PATH

def ollama_llm_symptom_check(prompt, model):
    """
    Queries the LLM API.
    Returns back a list of symptoms based off of statement made
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

if __name__ == "__main__":
    pass
    # conversation_log, symptom_log, article_log, umls_log = surface_patient_information(patient_statement_01)

