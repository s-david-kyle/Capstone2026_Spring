# Summary
Here are high level notes from our team meeting yesterday!
Our current tasks:
- David is going to be working on implementing Kennedy's summarizer template into the LLM questioning flow (which is used by medical professionals to record patient data)
- Kennedy and Partha are pushing the database code they have created to our GitHub
- I'll turn my LLM data-retrieval code from the proof of concept into a python module, and then import the module into a copy of Paada's UI code. This will be a trial to see how we can link together our different codebases with minimal overlap.
Outline of what we spoke about 3/17
- Reminders: 
	- Make sure you are updating your weekly capstone logs here: https://uarizona.co1.qualtrics.com/jfe/form/SV_b18UwU4Om9gesho?Q_CHL=qr
	- We have all the signatures we need to submit our proposals in d2l, make sure you submit the proposal under the assignments section in the course page
- David demoed his proof of concept code, which utilizes a local gemma model to gather patient symptom data. A saturator acts as a dynamic stop criteria, and differential diagnosis is performed at the end of the questioning.
- We ran Paada's UI, and discussed libraries needed to run and the Ollama server app
- Partha showed his schema code for Session and Turn tables to be used by the LLM application. David suggested some additional fields to track record creation dates.
- I demoed the proof of concept code I had written, and covered the data sources it was accessing as the LLM interacted with the patient (UMLS, MTS-dialogue, PubMed), and the data being stored from the conversation/data pulls.
- Kennedy discussed his logic for the tables he and Partha were creating for the database, modifications that can be used for the discussion flow with the LLM by applying a template used by doctors, and the importance of physical exam results in the diagnosis

# Original notes
Agenda
- David
	- Prototype
		- Using biomedical-ner-all and gemma
		- Categorizes knee symptoms
		- Saturator
			- Acts as stop criteria
			- Ask the patient is that all, does this include all your symptoms
		- Differential diagnosis performed at the end
			- Performed by Gemma model
- Make sure everyone has submitted their proposal in d2l
	- Gemma
- Demo Paada's patient interface (UI)
- Partha (DB work)
	- Showed schema for first two tables
		- Session
		- Turn
	- Using SQLViewer
		- David has suggestions
			- Wants auto incrementer for unique ID
			- Wants modify dates added (when database)
- Demo proof of concept, and show how data sources are being used (UMLS, MTS-Dialogue, PubMed)
- Kennedy
	- Will push work up tonight
	- Showed David’s saturiser
		- Has template for summarizer
			- Uses templates
			- Takes about 5 minutes
	- Partha shows David’s suggestions for database
	- They will put code to GitHub tonight
- David - will work on LLM asking for facets of data from Kennedy’s template (summarizer)
- Gathering data need both:
	- Clinical questions (summarizer)
	- Physical exam
		- Needed to see if you are right
		- Make up physical exams
- Discuss how to combine current work
	- David 
- Discuss database format (SQL vs noSQL)
	- SQL
- Any other progress made since we last met
	- David will communicate over teams on Tuesday
		- Will try next
	- Kennedy/Partha: Code tonight
	- Virtual environment
		- Post in Teams