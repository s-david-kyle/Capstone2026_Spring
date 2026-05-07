# Overview
Visualization tool
# Implementation
Uses Chart.js for visualization, to assist in medical diagnosis. Users answer questions, and the system provides results through radar and bar charts.
- **User Interaction:** JavaScript handles form inputs, validates data, and communicates with the back-end asynchronously. 
- **Visualization:** Chart.js renders real-time charts (bar and radar) based on the model’s outputs, enhancing interpretability.
# Interface
![[Pasted image 20260223174736.png]]
## User input questions w/ sample answers
- How old are you?
	- 49
- What is your gender?
	- Female
- What is your region?
	- North America
- Do you have pain or any other symptoms?
	- I feel pain. The pain is: haunting, sensitive, tugging, burning
- If you are experiencing pain, how would you rate its intensity on a scale of 0 to 10, and how quickly does the pain appear on a scale of 0 to 10?
	- 6.2
- If applicable, where is your pain located, and how precisely can you describe its location on a scale of 0 to 10?
	- lower chest, upper chest. 3
- Please describe your situation in more detail
	- I have recently had stools that were black (like coal). I have a burning sensation that starts...
- Please provide a brief medical history and family history
	- I am significantly overweight compared to people of the same height as me. I drink alcohol...
## Output of differential diagnosis results
- Radar chart with measures scaled 0-1 for:
	- Anemia
	- Unstable angina
	- Stable angina
	- Possible NSTEMI / STEMI
	- Pericarditis
	- GERD
	- Bronchitis
	- Boerhaave
- Bar chart with same measures above scaled 0-1 for comparison
## Interaction with Flask-backend
- **User Interaction:** The user inputs data (e.g., age, sex, symptoms, medical history, etc.) into the form on the web page.
- **Data Submission:** JavaScript sends the form data to the Flask back-end.
- **LLM Processing:** The Flask server forwards the user data to our LLM, which analyzes it and makes predictions.
- **Result Generation:** The Flask back-end prepares the results and sends them back to the front-end.
- **Visualization:** JavaScript <mark>processes the returned results and uses Chart.js to create a dynamic chart</mark>, presenting the results to the user in a clear and interactive manner.
# See also
- [[Web-based Interface]]
- [[Flask back-end]]