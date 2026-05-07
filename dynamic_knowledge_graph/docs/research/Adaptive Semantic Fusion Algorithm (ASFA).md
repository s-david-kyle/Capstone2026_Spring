# Overview
The approach also introduces an adaptive semantic fusion algorithm (ASFA) that combines probabilistic reasoning with graph-based optimization. This semantic fusion ensures scalability and accuracy in medical applications.

DKG-LLM uses the Adaptive Semantic Fusion Algorithm (ASFA) that combines probabilistic modelling, Bayesian inference, and graph optimization to achieve three key goals: 
- 1- Extraction of semantic entities in DKG and their accurate fusion. 
- 2- Real-time graph updates that add approximately 150 new nodes and edges per dataset for this purpose. A maximum of 987654 edges is maintained for scalability. 
- 3- Accurate treatment recommendations tailored to patient profiles and precise diagnoses. 

The algorithm that <mark>integrates Grok 3 outputs with the DKG</mark>, using probabilistic modeling and graph optimization for updates and reasoning
# How it works
The Adaptive Semantic Fusion Algorithm (ASFA) is the core innovation, integrating Grok 3 outputs with the DKG while ensuring semantic consistency and computational efficiency. ASFA operates in five phases:
- Data Ingestion (DI)
	- Collects clinical reports, PubMed articles, and X posts
- Semantic Extraction (SE)
	- Extracts entities and relationships using Grok 3, computes confidence scores
- Graph Update (GU)
	- Add new nodes and edges to the DKG, optimizes with MRF, and updates edge weights
- Reasoning and Recommendation
	- Perform Bayesian inference for diagnosis and optimization for treatment recommendations.
- Feedback Integration
	- Use clinician feedback to refine parameters via reinforcement learning

# See Also
- [[DKG-LLM Framework]]
- [[Markov Random Field (MRF)]]