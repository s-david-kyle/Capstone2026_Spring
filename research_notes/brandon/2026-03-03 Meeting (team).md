# Overall Goal (Dr. Yasaei)
The proposal should address challenges identified in existing literature, highlight novel features (technical or user-focused) and demonstrate a plan to improve upon current solutions.
- **Ensure all tasks are clearly defined, including research, coding, data collection, and project management**
- **Divide the workload - the task is not just the coding**
	- Do more research and get related papers
		- Skim abstracts quickly to see if they are relevant
		- Pick top 10 papers that have similar goals to our project, and read these deeply
	- Work on code for proof of concept
	- Work on data collection
	- Create the plan for doing the project
- Share completed proposal in teams with Dr. Yasaei (make sure to @mention her for visibility)

# Proposed System Architecture and Subtasks
## Part 1
![[Pasted image 20260303181806.png]]
### Patient interface
- <mark>Subtask: Design a user interface that can interact with a conversation log and the LLM</mark>
	- Paada
	- Proof of concept
		- Chat interface
			- Form created that saves user input as a string
			- String is passed to LLM
			- LLM response is displayed in form
- Requirements
	- Will need to display text (questions) from LLM
	- Will need text input box for the patient to fill out
	- Will need to directly interface with LLM
	- Will need to add entries to a conversation log
- Considerations
	- Which language - Python
		- Python examples
			- Web-based: [[Streamlit]]
			- Desktop: [[Tkinter]]
		- Pre-built online solutions
			- Make sure it suits our needs
- MVP - text only
	- If time - speech, image, etc
### Conversation log
<mark>Subtask: Write code that can log responses</mark>
Partha & Kennedy
- Proof of concept
	- Write Python code that uses the input method to take in a theoretical patient response to the question "How are you feeling?"
	- Write the initial question to DataFrame column "question"
	- Write the patient response to DataFrame column "answer"
	- Database
		- Start with this if we are comfortable, will need it eventually anyway
- Requirements
	- Data structure will need enough fields to store:
		- User ID
		- Questions asked to patient
		- Responses from LLM
		- Symptoms
		- Retrieved article information (DDXPlus)
		- Patient history
	- Note: this should be the output to process in Part 2
		- In dashboard have a button to show conversation history to doctor
		- Good for follow-up questions
- Considerations
	- What should be used for conversation history?
		- Does not have to be a database for proof of concept or small-scale interactions - even a DataFrame could work
### LLM - Processing patient responses
<mark>Subtask: Read conversation log and generate list of symptoms</mark>
- Proof of concept - can use existing proof of concept in GitHub for starter code
	- Take patient response from conversation log. Prototype can use  generic place holder data for this
		- example: I have a stomachache
	- Extract symptoms from patient response
	- Load symptoms as a list into "symptoms" field in conversation log
- Requirements
	- Have LLM process patient response and pull out list of symptoms (see existing proof of concept code for example)
	- Log list of symptoms in "symptoms" DataFrame column
- Considerations
	- Local model? (greater privacy, opportunities for fine-tuning)
	- Online model? (larger training sets, no privacy)
	- David - prototype code for the following and find research related to the techniques below:
		- <mark>Subtask: Research other potential datasources/models that can be used for symptom extraction - David's link</mark>
			- Extractor
			- Grounder
			- Reasoner
### External data query
<mark>Subtask: form query from patient statement and symptoms, query DDXPlus or UMLS</mark>
Brandon
- Proof of concept
	- Take patient response and list of symptoms from conversation log. Prototype can use  generic place holder data for this
		- example: "I have stomach pain and it hurts more after I eat", Symptoms: Stomach pain, Pain, Eating, Postprandial (after eating)
	- Query datasource [[DDXPlus]] / [[UMLS]] / [[PubMed]]
	- Summarize / extract / clean returned data
- <mark>Potentially involve Knowledge Graph at this stage (research)</mark>
### LLM processing related symptom information and patient history
<mark>Subtask: research combining summarized / extracted / cleaned data to form a question for the patient that is calm and reassuring</mark>
All of us tackle this, through meetings, independent research, etc
- Proof of concept
	- Skip fine-tuning initially; try prompt engineering techniques to make use of [[MTS Dialogue Clinical Note]] and data returned from the external data query to form a good question for the patient
		- Use place holder data initially from this (pull sample articles from [[DDXPlus]] / [[UMLS]] / [[PubMed]])
	- Output text for follow-up question, save to conversation log
	- When patient interface is created, pass this text into that interface

## Part 2
- Data sources for surfacing follow-up questions with patient
	- [[UMLS]] (terminology, classification, coding standards)
	- [[PubMed]] (medical articles, book citations)
- Storage for LLM context and explainability
	- RAG
	- [[Knowledge Graphs (KGs)]]
- Output for doctor differential diagnosis
	- (same as above for follow-up questions)
		- [[UMLS]] (terminology, classification, coding standards)
		- [[PubMed]] (medical articles, book citations)

# Time-saving opportunities
- Knowledge Graphs
	- [[Knowledge graph–based thought - a knowledge graph-enhanced LLM framework for pan-cancer question answering]]
		- KGT framework is openly available at: https://github.com/yichun10/bioKGQA-KGT
			- Hardware requirements will necessitate running it on the University's servers
	- [[UMLS]]
		- Contains key terminology, classification, coding standards, and resources for biomedical information systems and services
		- Includes health records
		- Files can be downloaded
		- License requested 2/28, takes 3 business days for approval
			- Approved 3/2! Provides access to:
				- [Value Set Authority Center (VSAC)](https://url.usb.m.mimecastprotect.com/s/hMRRCOJpWjf01O8PZuEfLSGhrg-?domain=3pl83q4d.r.us-east-1.awstrack.me "https://url.usb.m.mimecastprotect.com/s/hMRRCOJpWjf01O8PZuEfLSGhrg-?domain=3pl83q4d.r.us-east-1.awstrack.me")
				- [RxNorm](https://url.usb.m.mimecastprotect.com/s/dPOuCP6q0kCoz6wDNU0hESxIrQq?domain=3pl83q4d.r.us-east-1.awstrack.me "https://url.usb.m.mimecastprotect.com/s/dPOuCP6q0kCoz6wDNU0hESxIrQq?domain=3pl83q4d.r.us-east-1.awstrack.me")
				- [SNOMED CT](https://url.usb.m.mimecastprotect.com/s/wqYLCQArYlf3vRQDlCMigSGsqpb?domain=3pl83q4d.r.us-east-1.awstrack.me "https://url.usb.m.mimecastprotect.com/s/wqYLCQArYlf3vRQDlCMigSGsqpb?domain=3pl83q4d.r.us-east-1.awstrack.me")
				- [NIH Common Data Elements (CDE) Repository](https://url.usb.m.mimecastprotect.com/s/Pa3eCR8vZmtR4O6K0hOs1S1MMrJ?domain=3pl83q4d.r.us-east-1.awstrack.me "https://url.usb.m.mimecastprotect.com/s/Pa3eCR8vZmtR4O6K0hOs1S1MMrJ?domain=3pl83q4d.r.us-east-1.awstrack.me")
	- [[LLM-Driven Medical Document Analysis -  Enhancing Trustworthy Pathology and Differential Diagnosis]]
		- Project code available at: https://github.com/leitro/Differential-Diagnosis-LoRA
	- [[DKG-LLM - A Framework for Medical Diagnosis and Personalized Treatment Recommendations via Dynamic Knowledge Graph and Large Language Model Integration]]
		- Reach out to saba.hesaraki@iau.ir to see if they would share their code or KG

# Novel Opportunities
## Potential Opportunities (Dr. Yasaei)
- <mark>Gather existing research papers to understand how to speak with patients and the process of getting correct symptoms</mark>
- When a patient comes in with a series of symptoms, not all symptoms they provide are correct as <mark>they may use the wrong names or keywords.</mark>
- <mark>We are focusing on giving information to the doctor instead of competing with tools that give individuals information about their health. From Dr. Yasaei’s discussions with medical doctors, this is a pain point because of the speed at which they must work.</mark> 
## Ideas from research papers
- [[Knowledge graph–based thought - a knowledge graph-enhanced LLM framework for pan-cancer question answering]] (October 10, 2024)
	- Further exploration of different KG architectures, retrieval methods, and reasoning strategies within the KG framework could lead to more robust and reliable systems.
	- Research into techniques that reduce the computational cost of training and deploying LLMs would be beneficial.
	- <mark>The system does not perform fuzzy matching - if a drug is misspelled by even one letter it will fail to retrieve information from the knowledge graph</mark>
	- The constructed QA dataset was designed to validate the effectiveness of the framework, but does not cover all potential use cases
- [[LLM-Driven Medical Document Analysis -  Enhancing Trustworthy Pathology and Differential Diagnosis]] (June 24, 2025)
	- Enhancing usability and functionality for <mark>rapid analysis of patient records</mark>
	- <mark>Explainability of this application</mark>
- [[Enhancing Dialogue Symptom Diagnosis]] (2019)
	- Building a larger symptom graph
	- <mark>Using external medical information to improve the performance of symptom diagnosis on dialogues</mark>
	- Exploring more sophisticated attention mechanisms - such as hierarchal or graph attention
	- Handling different types of dialogues (languages, varying levels of noise)
- [[Symptoms perceived and recorded by patients]] (1975)
	- More detailed analysis on self-medication
	- Studying social factors on symptom recording and reporting
	- <mark>Looking at the consulting behavior of the participants family</mark>
		- This could be very interesting for part 1 - where we are gathering information from the patient. Here it may be referring to the ability of family to act as consultants, but for our purposes they can provide additional insight (perhaps less biased) than the patient themselves.
	- Short-term study completed - look at long-term effects and trends
- [[Leveraging Medical Knowledge Graphs Into Large LanguageModels for Diagnosis Prediction - Design and Application Study]] (published February 24 2025)
	- [[UMLS]] concept extractors (Clinical Text Analysis and Knowledge Extraction System and [[QuickUMLS]]) have limitations with identifying indirect or nuanced medical concepts
	- <mark>Relies on cosine similarity (common in RAG framework) and is limited by the quality of embedding representations</mark>
		- These need to capture the semantic nuances of medical concepts
		- This can lead to retrieving less relevant or noisy knowledge paths
- [[DKG-LLM - A Framework for Medical Diagnosis and Personalized Treatment Recommendations via Dynamic Knowledge Graph and Large Language Model Integration]] ()
	- Ensuring data privacy
		- <mark>Using federated learning to protect patient data</mark>
	- Optimizing for larger datasets
	- <mark>Incorporating biosensor data</mark>
	- Extending to emerging disease prediction
- [[SymptoTrackAI - Hybrid RAG Chatbot for Symptom Monitoring]] (June 22, 2025)
	- Expanding its symptom database for better medical coverage
	- Integrating live-expert consultations for real-time support
	- <mark>Enhancing conversational AI for a more interactive experience</mark>