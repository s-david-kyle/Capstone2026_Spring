# Overview 3-5-2026
The proof of concept is a single Jupyter notebook written with python code that simulates a conversation between a physician and a patient - part 1 of our project. It poses a simple question to the user - "How are you feeling today?" and then logs their response. The response is passed to a local LLM (currently Google's [[Gemma-3n-e4b]]), which extracts symptoms from the patient's statement, which are also logged. [[Unified Medical Language System (UMLS)]] is used as a medical thesaurus to find synonyms for the extracted symptoms, for differential diagnosis later in the process.  [[MTS Dialogue Clinical Note]], a dataset containing doctor/patient conversations, is queried using the symptom list, pulling conversations that may discuss similar symptoms the patient is facing. The potentially relevant example conversations and the patient's response are passed to the LLM to generate the next question. This process repeats three more times, logging both questions and answers as well as a growing list of symptoms that correspond to each dialogue. The resulting data can be pushed to a database, where the 2nd stage of the project begins - creating an output for differential analysis by a doctor.

Some finer points:
- [[Unified Medical Language System (UMLS)]] data is not currently being logged; the prototype is pulling it, but it hasn't been folded (data extracted into a DataFrame suited for pushing to our database) into the process yet
- [[PubMed]] data is also being pulled but not used at this stage. As Kennedy had suggested, the articles are too vast and deep to query before getting a clearer picture of the problem. This should be handled in part 2 of the project.
- The conversation and symptom logs includes a "dialogue_turn" number, to indicate where in the conversation the information comes from. David's idea about presenting the full conversation history to the doctor in part 2 can use this to parse that out.

Sample conversation generated using the proof of concept. Q represent questions from the LLM, A are answers from a volunteer:
Q: How are you feeling today?
A: Not great. My stomache hurts. I'm bloated, constipated, and gassy.
Q: Could you describe the pain in your stomach more specifically – is it sharp, cramping, a dull ache, or something else? And could you tell me if you've noticed any changes in your diet recently?
A: It is cramping and mostly in the lower abdomen. No changes in my diet.
Q: Can you describe the cramping - is it sharp, dull, or a pulling sensation? And could you tell me if anything seems to make the cramping better or worse, such as movement or certain positions?
A: The cramping is sharp. Nothing seems to make the cramping better or worse.
Q: What is your activity level like outside of work?
A: Not much activity, just sitting down and walking for like an hour.

Symptoms generated from conversation:
- Stomach ache
- Bloating
- Constipation
- Gas
- Abdominal cramping
- Lower abdominal pain
- Cramping
- Sharp
- Unrelieved
- Fatigue
- Reduced activity level
- Postural discomfort
- Possible muscle strain
# Papers that influenced the proof of concept
- [[DKG-LLM - A Framework for Medical Diagnosis and Personalized Treatment Recommendations via Dynamic Knowledge Graph and Large Language Model Integration]] (August 2025)
	- This research paper shows how an LLM ([[Grok 3]]) can be used to process semantic information from patient records, [[PubMed]] and the [[MIMIC-III Clinical Database]], extracting the information into a single [[Dynamic Knowledge Graphs (DKGs)]]
	- They innovate with their [[Adaptive Semantic Fusion Algorithm (ASFA)]], which extracts entities from these data sources with the LLM to add new nodes and edges to their [[Dynamic Knowledge Graphs (DKGs)]]
		- This algorithm is the paper's major contribution, utilizing [[Markov Random Field (MRF)]] for graph pruning and constrained optimization
		- <mark>This algorithm would strengthen the logic behind extracting symptoms from patient dialogue, as well as inform the construction of a patient-specific knowledge graph to show doctors for their diagnoses. The approach also allows for updating terms beyond the static UMLS data</mark>
	- This is used to give treatment recommendations tailed to patient profiles and more precise diagnoses, with more up-to-date knowledge than a static [[Knowledge Graphs (KGs)]] would provide.
	- **In relation to our work:**
		- Our proof of concept currently uses an LLM ([[Gemma-3n-e4b]] instead of [[Grok 3]]) to extract a list of symptoms, but does not integrate these into a knowledge graph yet
		- We make use of the static [[Knowledge Graphs (KGs)]] [[Unified Medical Language System (UMLS)]] to find synonyms for symptoms extracted by the LLM from patient statements
		- <mark>Opportunities listed are related to privacy </mark> (using [[Federated learning]]) and incorporating biodata
			- Our proof of concept **processes everything locally**, which affords privacy assuming the data is never exposed to an outside source
- [[LLM-Driven Medical Document Analysis -  Enhancing Trustworthy Pathology and Differential Diagnosis]] (June 24, 2025)
	- Uses a fine-tuned LLM ([[LLaMa-v3]]) with the [[DDXPlus]] dataset with the aim to provide accurate, explainable diagnostic results.
		- [[LoRA]] approach used to update self-attention modules in each layer of the [[LLaMa-v3]] model. 
	- Sees the potential for LLMs in medical diagnosis, record summarization, and medical literature interpretation
		- Uses [[DDXPlus]] as a benchmark dataset for [[Differential Diagnosis (DDx)]]
	- Defines two critical tasks for AI systems to address: [[Pathology Prediction]] and [[Differential Diagnosis (DDx)]]
	- Explainability techniques: 
	- **In relation to our work:**
		- Privacy is being observed in a similar fashion in our proof of concept, however we are using [[Gemma-3n-e4b]] instead of [[LLaMa-v3]]
		- For part 2, using [[DDXPlus]] **to benchmark our differential diagnosis** will be useful
		- Code for fine-tuned model is available on GitHub, and we can learn from and/or use it
		- Opportunities listed:
			- Enhancing usability and functionality for rapid analysis of patient records
			- <mark>Explainability of this application</mark>
- [[Knowledge graph–based thought - a knowledge graph-enhanced LLM framework for pan-cancer question answering]] (October 10, 2024)
	- **In relation to our work:**
		- They extract important information from a question, then use graph schema-based inference to find optimal relationships within a knowledge graph that is relevant to a question. The knowledge graph is then processed with output in natural language format.
		- The project is available on GitHub, and requires a Linux (Ubuntu) operating system with specific hardware resources (at least 2 CPU cores, 32 GB VRAM for inference; 60 GB VRAM for GPU) and programming languages (Shell Script/Bash with Python 3.10.13). It also utilizes libraries like neo4j.
		- <mark>The paper does mention "catastrophic forgetting" when fine-tuning models, where the model forgets previously learned information as a consequence of parameter modifications made during the acquisition of new tasks.</mark>
		- Opportunities listed:
			-  Further exploration of different KG architectures, retrieval methods, and reasoning strategies within the KG framework could lead to more robust and reliable systems.
			- <mark>Research into techniques that reduce the computational cost of training and deploying LLMs would be beneficial.</mark>
				- Utilizing smaller models for more targeted tasks could help (proof of concept uses a relatively small model)
			- <mark>The system does not perform fuzzy matching - if a drug is misspelled by even one letter it will fail to retrieve information from the knowledge graph</mark>
			- The constructed QA dataset was designed to validate the effectiveness of the framework, but does not cover all potential use cases
# What we can add to existing research
**Data privacy** is missing from [[DKG-LLM - A Framework for Medical Diagnosis and Personalized Treatment Recommendations via Dynamic Knowledge Graph and Large Language Model Integration]], while **explainability** is missing from [[LLM-Driven Medical Document Analysis -  Enhancing Trustworthy Pathology and Differential Diagnosis]]. [[Knowledge graph–based thought - a knowledge graph-enhanced LLM framework for pan-cancer question answering]] mentions issue with fuzzy matching - drug names being misspelled failing to retrieve information on its knowledge graph.
- <mark>We can take the DKG structure from the first paper with a local model use mentioned in the second to provide differential diagnosis tools that are explainable and private. We can improve on "fuzzy-matching" techniques to be able to more accurately navigate knowledge maps</mark>

# Ideas from current proof of concept
- Part 1
	- Further processing on collected information as the dialogue continues could be valuable in generating better questions
		- Conversation history is not being summarized, and previous statements made with the the LLM are not being given to it (just the last statement from the patient)
			- This may lead the model into looping the same questions if we go beyond the limited 4 questions
		- Monitoring the symptom list to see if duplicate entries are being added (and how often) may signal the end of the conversation, versus a static number (4 currently)
		- 
- Part 2
	- Data gathered is structured with conversation turns, joining the turns and presenting additional information in an intuitive way for the doctor will be important
	- Each patient could have their own knowledge graph, which gets updated with every visit/interaction
		- The doctor should be able to traverse this graph
		- Potentially beyond scope, the doctor should be able to update the graph
		- This graph could be used as a patient history in part 1 (after patient's initial visit)
		- <mark>Overall, the ability to show the question/answers generated from the patient/LLM interaction and the output generated from those interactions in an intuitive, understanding way is priority</mark>
			- While the logic of the LLM is impossible to explain, the output generated at each step should be easily interpretable and provide a bridge for the doctor to get to their diagnosis