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

# team modules
from knowledge_graph import convert_df_to_kg

def umls_retrieval(symptoms):
    """
    Retrieves UMLS concepts based on a list of symptoms.

    Args:
        symptoms (list): A list of symptoms to search for in the UMLS database.

    Returns:
        list: A list of dictionaries, where each dictionary contains a 'Symptom' 
        and its corresponding 'SemanticType' based on the UMLS search results.
        Returns an empty list if an error occurs during the search.
    """
    # base_uri = 'https://uts-ws.nlm.nih.gov/rest'

    # intialize API
    search_api = UMLSClient(api_key=UMLS_API_KEY).searchAPI
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
        print(search_results)
        search_results = eval(search_results)
    
    # create list of name and semanticTypes
    symptom_names = []
    semantic_types = []
    
    # try/catch in case server goes down again
    try:
        # extract search results
        for result in search_results['result']['results']:
            # add items to lists
            symptom_names.append(result['name'])
            semantic_types.append(result['semanticTypes'][0])
        # create a list of JSON pairs
        umls_json = [{'Symptom': symptom_names[i], 'SemanticType': semantic_types[i]} for i in range(len(symptom_names))]
    except:
        umls_json = [{'Symptom': None, 'SemanticType': None}]
    return umls_json

def umls_knowledge_graph(symptom, num_results):
    """
    Retrieves UMLS concepts based on a list of symptoms.

    Args:
        symptom (str): A symptom to search for in the UMLS database.

    Returns:
        df (DataFrame): A dataframe with 'Symptom' and 'SemanticType' columns.
        Returns an empty dataframe if an error occurs during the search.
    """
    # base_uri = 'https://uts-ws.nlm.nih.gov/rest'

    # intialize API
    search_api = UMLSClient(api_key=UMLS_API_KEY).searchAPI
    # basic search
    search_results = search_api.search(
        search_string=symptom,  # The term to search for
        input_type=None,  # None implies search for any input type
        include_obsolete=False,  # Don't include obsolete terms
        include_suppressible=False,  # Don't include suppressible terms
        return_id_type="concept",  # Return UMLS Concept Unique Identifiers (CUIs)
        search_type="words",  # Search using word-based matching
        page_number=1,  # Start from the first page
        page_size=num_results,  # Limit the result to 10 items per page
        save_to_file=False, # make true if needed later
        file_path=UMLS_PATH
    )
    # convert from string to dictionary for indexing
    # print(search_results)
    search_results = eval(search_results)
    
    # create list of name and semanticTypes
    symptom_names = []
    semantic_types = []
    
    # try/catch in case server goes down again
    try:
        # extract search results
        for result in search_results['result']['results']:
            # add items to lists
            symptom_names.append(result['name'])
            semantic_types.append(result['semanticTypes'][0])
        # put in dataframe
        df = pd.DataFrame({'symptom': symptom_names, 'semantic_type': semantic_types})
        # umls_json = [{'Symptom': symptom_names[i], 'SemanticType': semantic_types[i]} for i in range(len(symptom_names))]
    except:
        df = pd.DataFrame({'symptom': [None], 'semantic_type': [None]})
    print(f'New UMLS knowledge graph will have {len(df)} symptoms')
    print(df)
    return df

def symptom_drill_down(df, primary_symptom, include_other_types=False):
    """
    ['Sign or Symptom' 'Disease or Syndrome' 'Pathologic Function' 'Finding'
    'Manufactured Object' 'Clinical Attribute' 'Medical Device'
    'Organic Chemical' 'Injury or Poisoning' 'Intellectual Product']
    """
    # remove other semantic types for first search
    if include_other_types is False:
        df = df[df['semantic_type'] == 'Sign or Symptom'].copy()
    # TODO: filter out any matches with primary_symptom to remove circular reference
    # BUT only if include_other_types = False (may be useful for final selection)
    
    # build a KG out of this
    df['head'] = primary_symptom
    # rename columns for knowledge graph translation
    df.columns = ['tail', 'relation', 'head']
    graph = convert_df_to_kg(df)
    print(df)
    return graph

if __name__ == "__main__":
    pass
    # conversation_log, symptom_log, article_log, umls_log = surface_patient_information(patient_statement_01)
