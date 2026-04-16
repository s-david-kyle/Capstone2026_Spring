# Overview
The first part of the project is taking in the information from the patient. When a patient comes in with a series of symptoms, not all symptoms they provide are correct as they may use the wrong names or keywords. For example, they may say they have a migraine when they actually have a headache. We want to utilize a chatbot interface that resembles the interaction a nurse or doctor has with a patient when they initially meet. The goal in this part is to get accurate symptoms and the condition of the patient. Some finer points:

- The chatbot’s language must be simple so the patient does not have to read many words, and the words should be calm and reassuring
- We will make use of a pre-trained model, with a goal of fine-tuning it to make it more personalized.
- We will consider privacy issues with relaying this information to a chatbot to be resolved (or the interactions to be local) for this proof of concept, however if we do have time to address privacy directly that would also be good.
# Implementation Questions
- Information gathering
	- User form?
		- [[Chart.js]]
		- [[Flask back-end]]
	- Less structured user prompts to LLM?
		- Agentic?
	- If using LLM, will it be fine-tuned for more patient-focused (calm, reassuring, etc) language?
	- Will this be processing images?
		- [[GLoRIA]]
	- Will this be run locally or online?
- Existing LLMs
	- [Clinical Modern BERT](https://huggingface.co/Simonlee711/Clinical_ModernBERT)
	- [[Me-LLaMA]]
- Relaying information to part 2
	- <mark>How should the output be formatted to hand off to part 2?</mark>
- Testing
	- [[Synthetic Scenarios]]
- Where this fits in the broader context of current work
	- What papers do we have that help assist us with this part?
	- What papers show opportunities that this part may address?
# See also
- [[Project Proposal]]