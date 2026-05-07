# Proposal Draft Sharing & Feedback
The proposal should address challenges identified in existing literature, highlight novel features (technical or user-focused) and demonstrate a plan to improve upon current solutions. Finer points:
- Sent a copy of Kennedy's shared proposal draft document to Dr. Yasaei 
- Discussed team's work on the proposal and the group allocations
- Dr. Yasaei's proposal  feedback:
	- Dr. Yasaei requested that her department be changed to the College of Information Science instead of Cyber Operations (they have been combined into InfoSci)
	- **The team needs to be clear about their approach and challenges they are addressing with their proposed solution**
	- The team should know what contribution they want to make and how their paper's contributions address most of the problems, while also identifying new issues
	- Potential ways to improve include
		- Discussing unique data features used by our model
		- Novel models (technical or user-related)
		- <mark>Exploring personalized and context-aware methods to better understand risk factors, and/or interact with patients more effectively</mark>
		- Utilize advanced models
# Patient-facing architecture (project part 1)
The goal for the patient-facing interface is a continuous conversation with patients for accurate information gathering. Finer points:
- **Conduct research on human-computer interaction to improve user experience and trust**
	- The LLM conversation should deliberate, and attempt to get new information from the patient
		- <mark>There are many opportunities in this area</mark>
- LLM - local vs online/commercial
	- **Research viable LLMs for patient interaction**
		- The model can be run locally using smaller versions of LLMs on university servers
		- Online versions come with limitations on queries, but we can consider paid versions if needed
- If we are able to address patient interactions with the LLM and if time allows, consider adding functionality to process uploaded images
	- Dr. Yasaei has ultrasound images from her research which include data like age and ethnicity, however these are focused on one particular area of medicine (this project has a more general focus)
- <mark>Test scenarios can be generated from data</mark> pulled from [[PubMed]]
# Data, Diagnosis & Key Metrics (project part 2)
The project will utilize data from [[PubMed]], potentially requiring integration with the website. A proof-of-concept will be developed to demonstrate the model's functionality. Key evaluation metrics depend on the nature of the model (LLM versus numerical) and how well techniques like RAG and [[Dynamic Knowledge Graphs (DKGs)]] are implemented. Finer points:
- Architecture
	- Dr. Yasaei interested in [[Dynamic Knowledge Graphs (DKGs)]]
	- <mark>They can give more info to LLM what is related to what, and how to synthesize information, especially relation and connection</mark>
	- New keywords can be surfaced
	- Explainability: you can say this relates to this in this manner
- Data
	- Use [[PubMed]] for data collection
		- **Connect the model to PubMed when testing scenarios (proof of concept)**
	- **Data preprocessing will likely be required depending on the dataset**
- Key metrics
	- Evaluating LLM interactions can be challenging (manual reviews, etc.)
	- Numerical models would require F1-score and other standard metrics
	- Evaluation will depend on the added features and how well they utilize RAG, [[Dynamic Knowledge Graphs (DKGs)]], etc.
# Project Research & Planning
 The team needs to manage the large volume of research papers by <mark>focusing on key publications and leveraging human-computer interaction principles for a user-friendly design.</mark> **Dr. Yasaei requested to review the completed proposal by Monday.** The proposal turn-in date has been extended to Thursday, March 5th.
# Next Steps
Timely completion of the proposal is crucial:
- **Ensure all tasks are clearly defined, including research, coding, data collection, and project management**
- **Divide the workload - the task is not just the coding**
	- Do more research and get related papers
		- Skim abstracts quickly to see if they are relevant
		- Pick top 10 papers that have similar goals to our project, and read these deeply
	- Work on code for proof of concept
	- Work on data collection
	- Create the plan for doing the project
- Share completed proposal in teams with Dr. Yasaei (make sure to @mention her for visibility)
# See also
- [[Meeting Notes]]