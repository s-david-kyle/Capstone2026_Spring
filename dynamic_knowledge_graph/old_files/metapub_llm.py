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

# In[1]:


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


# In[2]:


# modify this endpoint if using different LLM
url = "http://127.0.0.1:1234/v1/chat/completions"


# In[3]:


# first patient interaction
# patient_statement_01 = 'I have a headache'
# patient_statement_01 = 'I have a stomach ache that has been there for two weeks and it hurts more after I eat'
# patient_statement_01 = 'I have been sneezing and I have a runny nose for two weeks'
patient_statement_01 = 'I have stomach pain and it hurts more after I eat'
# patient_statement_01 = 'I have a stomach ache and it hurts more after I eat'


# In[4]:


# use LLM to pull out potential symptom information only
def query_llm_symptom_check(prompt):
    """
    Queries the LLM API.
    Returns back a list of symptoms based off of statement made
    """

    headers = {
        "Content-Type": "application/json"
    }

    # look for symptom information
    prompt = f'''List keywords for medical symptoms in this statement with bullet points 
                and no additional information. Avoid vague singular words like "pain": {prompt}'''

    data = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        # process symptom text into a list
        response = response.json()["choices"][0]["message"]["content"]
        symptoms = re.findall(r'\*\s[^\n]+', response)
        symptoms = [symptom.replace('* ', '') for symptom in symptoms]
        # remove any starting/ending spaces from each item
        symptoms = [symptom.strip() for symptom in symptoms]
        return symptoms
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


# In[5]:


def retrieve_pubmed_articles(symptoms):
    """ Returns a list of 10 pubmed articles relevant to symptoms"""
    # retreive relevant topics to send to PubMed
    symptom_string = symptoms = ', '.join(symptoms)

    # Initialize the fetcher
    fetch = PubMedFetcher()

    # Let user know what's going on
    print(f'Finding articles on:\n{symptom_string}')

    # Search for articles
    pmids = fetch.pmids_for_query(symptom_string, retmax=10)

    article_collection = []

    # Get article details
    for pmid in pmids:
        article = fetch.article_by_pmid(pmid)
        article_collection.append(article)

    return article_collection, pmids


# In[6]:


def llm_question_formation(symptoms):
    """Queries the LLM API."""
    headers = {
        "Content-Type": "application/json"
    }

    # look for symptom information
    prompt = f'''Take the following list of symptoms to form a question for a 
                patient that is calm, reassuring, and easily understandable with 
                no complex terms. Only include the question text. Give no explanations
                as to why the question was formed. Symptoms: 
                {symptoms}'''

    data = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


# In[7]:


def llm_article_summary(article):
    """
    Queries the LLM API.
    Summarizes article text
    """
    headers = {
        "Content-Type": "application/json"
    }

    # look for symptom information
    prompt = f'Summarize the following text in a single paragraph: {article}'

    data = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response = response.json()["choices"][0]["message"]["content"]
        return response
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


# # Ideas to improve PubMed article retreival
# 
# Examples taken from https://metapub.readthedocs.io/en/latest/tutorials.html
# 
# - Order articles with more recent dates at top, take the top most recent
# - Check full-text availability, create a flag for this (maybe prioritize these too)
# - Check access patterns to prioritize use as well

# In[8]:


def pubmed_article_logging(pubmed_articles, pmids, article_log, user_id, dialogue_turn):
    """
    Extracts each pubmed article's pmid, year, title, authors, journal, abstract, and 
    citation_bibtex. Adds each as a row into article_log.
    """
    # go through all articles
    for pubmed_article, pmid in zip(pubmed_articles, pmids):
        # pull article title, author, abstract, body, llm_summary
        article_source = 'PubMed'
        pubmed_article_id = pmid
        pubmed_article_year = pubmed_article.year
        pubmed_title = pubmed_article.title
        pubmed_authors = ', '.join(pubmed_article.authors)
        pubmed_journal = pubmed_article.journal
        pubmed_abstract = pubmed_article.abstract
        pubmed_citation = pubmed_article.citation_bibtex

        # generate llm summary from abstract (use entire article later)
        pubmed_llm_summary = llm_article_summary(pubmed_abstract)

        # update article_log
        article_log_row = [user_id, dialogue_turn, pubmed_article_id, article_source, 
                            pubmed_article_year, pubmed_title,
                            pubmed_authors, pubmed_journal,
                            pubmed_abstract, 'No article body (TBD)',
                            pubmed_llm_summary, pubmed_citation]
        article_log.loc[len(article_log)] = article_log_row
    return article_log


# In[9]:


def umls_retrieval(symptoms, user_id, dialogue_turn):
    # base_uri = 'https://uts-ws.nlm.nih.gov/rest'

    # intialize API
    search_api = UMLSClient(api_key=UMLS_API_KEY).searchAPI
    # TODO: find out why API request is failing
    # basic search
    for symptom in symptoms:
        search_results = search_api.search(
            search_string=symptom,  # The term to search for
            input_type=None,  # None implies search for any input type
            include_obsolete=False,  # Don't include obsolete terms
            include_suppressible=False,  # Don't include suppressible terms
            return_id_type="concept",  # Return UMLS Concept Unique Identifiers (CUIs)
            search_type="words",  # Search using word-based matching
            page_number=1,  # Start from the first page
            page_size=10,  # Limit the result to 10 items per page
            save_to_file=False, # make true if needed later
            file_path=UMLS_PATH
        )
        # convert from string to dictionary for indexing
        # print(search_results)
        search_results = eval(search_results)
    
    # create list of name and semanticTypes
    symptom_names = []
    semantic_types = []
    
    # check for error retreiving from API
    if search_results['status_code'] == 500:
        umls_symptoms = pd.DataFrame({'user_id': user_id,
                                  'dialogue_turn': dialogue_turn,
                                  'symptom_name': symptom_names,
                                  'semantic_types': semantic_types})
    else:
        # extract search results
        for result in search_results['result']['results']:
            # add items to lists
            symptom_names.append(result['name'])
            semantic_types.append(result['semanticTypes'][0])
        umls_symptoms = pd.DataFrame({'user_id': user_id,
                                    'dialogue_turn': dialogue_turn,
                                    'symptom_name': symptom_names,
                                    'semantic_types': semantic_types})
    return umls_symptoms


# In[10]:


# helper function to search through mts_dialogue more effectively
def extract_text(text):
    """Extracts text between 'Symptoms: ' and 'Diagnosis: '."""
    match = re.search(r"Symptoms: (.*?)\nDiagnosis: ", text)
    if match:
        return match.group(1)
    else:
        return None  # Or return an empty string "" if preferred


# In[11]:


# helper function to remove numbers from extracted text
def remove_floats(text):
    """Removes float values from the text, keeping only text."""
    if isinstance(text, (int, float)):
        return ''  # Replace numeric values with an empty string
    else:
        return text


# In[12]:


def llm_process_mts_dialogue(dialogues, patient_question):
    """
    Looks at sample dialogues on related topic, generates new question
    """
    headers = {
        "Content-Type": "application/json"
    }

    # look for symptom information
    prompt = f'''Use the following dialogue examples and the original patient question
                to generate a question that will give more insight into the patient's
                symptoms. Include the question only in the response. 
                Patient question: {patient_question}. Dialogue examples: {dialogues}'''

    data = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response = response.json()["choices"][0]["message"]["content"]
        return response
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


# In[ ]:


# examine mts dialogue
mts_dialogue = pd.read_csv('data/mts_dialogue/MTS-Dialog-TrainingSet (SDHP).csv')
# do a search in section_text to find matching dialogues with patient symptoms
def doctor_dialogue_mimic(symptoms, patient_question):
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
        question = llm_process_mts_dialogue(processed_dialogue, patient_question)
        mts_dialogue_used = True
    else:
        # generate general question using symptoms only if no dialogue available
        question = llm_question_formation(symptoms)
        mts_dialogue_used = False
        processed_dialogue = ''

    return question, mts_dialogue_used, processed_dialogue


# In[14]:


def surface_patient_information(sample_response=None):
    """ 
    Main function for part 1
    Generates 4 questions for the patient, returns back a dataframe 
    for differential diagnosis
    """
    # generate dataframes
    conversation_log = pd.DataFrame(columns=['user_id', 'dialogue_turn',
                                             'mts_dialogue_used', 'llm_question', 
                                             'patient_answer', 'mts_dialogue'])
    symptom_log = pd.DataFrame(columns=['user_id', 'dialogue_turn', 'symptom'])
    article_log = pd.DataFrame(columns=['user_id', 'dialogue_turn', 'article_id',
                                        'article_source', 'article_year',
                                        'article_title', 'article_authors',
                                        'article_journal', 'article_abstract', 
                                        'article_body', 'article_llm_summary',
                                        'article_citation'])

    # generate user_id
    # temporary assignment for now
    user_id = 1
    dialogue_turn = 1
    # 0 used for mts_dialogue first round
    mts_dialogue_used = 0
    mts_dialogue = ''

    # ask first question
    initial_question = 'How are you feeling today?'
    if sample_response == None:
        initial_response = input(initial_question)
    else:
        initial_response = sample_response

    # update conversation log
    conversation_log_row = [user_id, dialogue_turn, mts_dialogue_used,
                            initial_question, initial_response,
                            mts_dialogue]
    conversation_log.loc[len(conversation_log)] = conversation_log_row

    # find symptoms from initial_response
    symptoms = query_llm_symptom_check(initial_response)

    # update symptom log - 1 row per symptom
    for symptom in symptoms:
        symptom_log.loc[len(symptom_log)] = [user_id, dialogue_turn, symptom]

    # reach out to data sources to gather additional info
    # UMLS
    umls_log = umls_retrieval(symptoms, user_id, dialogue_turn)

    # use MTS dialogue to find sample conversations related to symtoms
    next_question, mts_dialogue_used, mts_dialogue = doctor_dialogue_mimic(symptoms, initial_response)

    # loop for remaining 3 questions
    for x in range(3):
        dialogue_turn += 1
        next_response = input(next_question)
        # update conversation log
        conversation_log_row = [user_id, dialogue_turn, mts_dialogue_used,
                                next_question, next_response,
                                mts_dialogue]
        conversation_log.loc[len(conversation_log)] = conversation_log_row

        # find symptoms from next_response
        symptoms = query_llm_symptom_check(next_response)

        # update umls_log with new symptom query
        new_umls_log = umls_retrieval(symptoms, user_id, dialogue_turn)
        umls_log = pd.concat([umls_log, new_umls_log])

        # update symptom log - 1 row per symptom
        for symptom in symptoms:
            symptom_log.loc[len(symptom_log)] = [user_id, dialogue_turn, symptom]

        # use MTS dialogue to find sample conversations related to symtoms
        next_question, mts_dialogue_used, mts_dialogue = doctor_dialogue_mimic(symptoms, next_response)

    # pubmed - save this for the end of questioning to get most relevant articles
    pubmed_articles, pmids = retrieve_pubmed_articles(symptoms)
    # pubmed_article = pubmed_articles[0]
    article_log = pubmed_article_logging(pubmed_articles, pmids, article_log, user_id, dialogue_turn)

    return conversation_log, symptom_log, article_log, umls_log


# In[15]:


# automatic prompt
# conversation_log, symptom_log, article_log, umls_log = surface_patient_information(patient_statement_01)
# user prompt
# conversation_log, symptom_log, article_log = surface_patient_information()


# In[ ]:


# conversation_log


# In[ ]:


# symptom_log


# In[ ]:


# umls_log


# In[ ]:


# article_log


# # PubMed article exploration

# In[ ]:


# for index, row in article_log.iterrows():
#     pprint(row['article_llm_summary'])


def ollama_llm_symptom_check(prompt, model):
    """
    Queries the LLM API.
    Returns back a list of symptoms based off of statement made
    """
    # try:
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
    # except Exception as e:
    #     return f"⚠️ Error: Ensure Ollama is running. ({str(e)})"

# In[ ]:

if __name__ == "__main__":
    conversation_log, symptom_log, article_log, umls_log = surface_patient_information(patient_statement_01)


