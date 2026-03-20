# Summary
Paada and Partha explained their UI and database work. Brandon demoed unified application with live database updates.

Dr. Yasaei outlined research needed to add functionality to application:
- Using MTS Dialogue solution to have LLM mimic doctor dialogues - find papers that mention MTS Dialogue, or switch to a dialogue datasource referenced by research papers
- Look up papers that work on human interaction with computer human interaction, specifically in the medical domain. Look at patient surveys and what they have extracted as the best experience for patients
- Create a ground rule so LLM specializes on the research read to influence tone, length, etc

Dr. Yasaei gave specific application suggestions:
- Summarization
	- Add more based on what the doctor needs
		- In addition to research above, review Kennedy's complete clerkship post in Teams
	- When application is more developed, Dr. Yasaei can set up a meeting with doctors to see what their comments are as well
- Part 2 (doctor-facing) side of project
	- Start this as soon as possible - divide the group up to focus on both part 1 and 2 simultaneously
	- Add confidence scores to differential diagnoses

Paada solicited additional features for UI
- Paada wants to focus on conditions that end the chat with the user
- Dr. Yasaei would like to make the chat more graphical - such as adding more animation icons to indicate application status when submitting answers
	- She suggested research should be done on improving the user interface as well
# Tasks
Based off of yesterday's meeting, here are the next batch of tasks we have. **Note that all tasks have a research aspect.**  Post in here which task you want to work on!
- (Everyone) **Run integrated application locally.** Set up the integrated application demoed yesterday. To do this, read our GitHub README.md.
	- Read Prerequisites, Local Setup, and Usage sections
	- Test the steps to ensure you are able to get the application running. Reach out to me if you run into any errors (requirements.txt, etc)
	- Read Code Structure section to see how source files have been split for our next tasks
- **Patient dialogue research:** Find papers focused on human/computer interaction in the medical domain. Determine how rules from these papers can positively influence the LLM dialogue. Add these rules to the system messages fed to the LLM to see if it improves the dialogue.
- **Summarization improvements:** Review Kennedy's complete clerkship post above, and do research to cite papers that support this summary format. Use adjustments to improve summary information added to database at the end of the patient conversation.
- **Symptom Drill-Down Dialogue:** Decide how to use LLM-extracted symptoms and UMLS term data to inform the LLM when it creates its next question. The next question should work to narrow down the list of symptoms. Find research papers that have tackled this task.
- **UI Improvements:** Research patient-facing user interfaces, and note useful sources. Determine what graphical aspects can be added to make it a more pleasant experience for the user. Implement these improvements.
- **Part 2 - initial research and buildout**: Examine our current database structure, and run the integrated application to generate data to populate it. Refer to Codebook notes to understand data that will be in the database in the future. Research tools doctors use to evaluate patient diagnoses. Build or outline preliminary visualizations derived from our data to support a view doctors would want to see.

# Original notes
- Demo
	- Paada’s UI
	- Kennedy & Partha’s DB
	- Unified code
- Share database schema with Yasaei
	- And SQL file
- Wants to see more research
	- MTS dialogue
	- Using doctor language - find specific paper
	- Look up papers that work on human interaction with computer human interaction, specifically in the medical domain
	- They do surveys, talk with human patients
	- Extract when they have the best experience
	- Create a ground rule - specialize based on the research you read
	- Base this on actual research
		- Tone, short, long
- Have next question differentiate between types of UMLS
- On the summarization
	- Add more, based on what the doctor needs
	- She can set up a meeting when it’s more developed so we can pitch it to the doctors to see what their comments are as well
- Mainly
	- Communication - research-based
	- Summary needs more
- Work on part 2?
	- Start this soon
	- Get confidence assigned to different diagnosis
- Paada - new things to add
	- Thinking of making user end chat
		- Do more with that
	- Add more graphic chat - animation icons
		- Read about this as well
# See also
- [[Meeting Notes]]