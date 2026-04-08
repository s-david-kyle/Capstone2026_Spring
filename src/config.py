import os

# LLM model
MODEL = 'gemma3:4b' # modify as needed

# API keys
# UMLS
UMLS_API_KEY = "c5fd9b7d-e6c0-42d6-90ef-177decf95932"
# PubMed
NCBI_API_KEY = os.environ.get("NCBI_API_KEY")

# filepaths
UMLS_PATH = 'data/UMLS'
