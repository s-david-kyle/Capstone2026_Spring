import os

# LLM model
MODEL = 'gemma3:4b' # modify as needed

# API keys
# UMLS
UMLS_API_KEY = os.environ.get("UMLS_API_KEY")
# PubMed
NCBI_API_KEY = os.environ.get("NCBI_API_KEY")

# filepaths
UMLS_PATH = 'data/UMLS'
