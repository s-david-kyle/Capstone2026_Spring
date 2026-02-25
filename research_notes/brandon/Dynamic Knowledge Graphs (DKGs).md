# Overview
DKGs primarily focus on understanding structural changes in graphs over time
- This relies on evolving datasets to add or update nodes and edges
- Learning meta-knowledge shows the evolution of the graph's structural and semantic properties instead of specific content within individual nodes and edges
# How they work
- Much of the data we generate includes timestamps
	- When a new account is created
	- When a user follows another user
	- A user updates their profile
![[DKG construction.png]]
- Standard KGs are constructed by extracting entity and relationships, that get further broken down into NLP subtasks
- <mark>DKGs have an additional KG completion phase, which dynamically updates or adds new nodes and relations to an existing KG.</mark> This can be done in two ways:
	- **Inference-based completion**
		- New knowledge is derived from studying the existing graph and added into the KG
	- **Extraction-based completion**
		- A new KG is constructed with external data sources, then linked to the existing KG, fusing knowledge sources
# Applications
## Detecting emerging communities of knowledge
- For the Conference on Knowledge Discovery and Data Mining (KDD), a series of knowledge graphs were created every year from 2013 to 2021
- Comparing the graph structures allowed them to identified trends, like increased focus on topics like "graph" and "e-commerce"
- Emerging publications <mark>emphasizing interconnected topics rather than single topics</mark>
- Allows researchers to anticipate future research directions and organizations to see possible industry developments

## Linguistics - Updating graphs with neologisms
- Coining new words or assignment of new meanings to existing words
- Can reflect the evolution of language across generations
- <mark>Conversational chatbots, sentiment analysis systems, search engines, and other applications can benefit from these KGs through more effective understanding of user intent and semantics</mark>

# DKG-LLM Implementation
 A structured graph 𝐺 (𝑉, 𝐸), where 𝑉 represents nodes (e.g., diseases, symptoms, treatments, patient profiles) and 𝐸 denotes semantic relationships (e.g., "causes," "treats").
# See also
- [[Knowledge Graphs (KGs)]]
- [[Temporal Knowledge Graphs (TKGs)]]
- [[DKG-LLM Framework]]

# Source
https://hub.researchgraph.org/dynamic-knowledge-graphs-a-next-step-for-data-representation/

#DynamicKnowledgeGraph
