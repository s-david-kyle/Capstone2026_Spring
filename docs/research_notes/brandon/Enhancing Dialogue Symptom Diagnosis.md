# Abstract
Symptom diagnosis is a challenging yet profound problem in natural language processing. Most previous research focus on investigating the standard electronic medical records for symptom diagnosis, while the dialogues between doctors and patients that contain more rich information are not well studied. In this paper, we first construct a dialogue symptom diagnosis dataset based on an online medical forum with a large amount of dialogues between patients and doctors. Then, we provide some benchmark models on this dataset to boost the research of dialogue symptom diagnosis. In order to further enhance the performance of symptom diagnosis over dialogues, we propose a global attention mechanism to capture more symptom related information, and build a symptom graph to model the associations between symptoms rather than treating each symptom independently. Experimental results show that both the global attention and symptom graph are effective to boost dialogue symptom diagnosis. In particular, our proposed model achieves the state-of-the-art performance on the constructed dataset.
# Paper Summary
The provided text describes a model for symptom recognition from dialogue, focusing on the problem of ambiguity and leveraging both document-level and corpus-level attention mechanisms. Here's a summary:

**The core problem:** Dialogue understanding for symptom recognition is challenging due to word ambiguity.

**The proposed solution:** The authors propose a model that utilizes a Bi-LSTM encoder to process dialogues and employs attention mechanisms to handle ambiguity.

**Key components:**

- **Bi-LSTM Encoder:** This model processes each sentence (or document) in the dialogue to generate hidden states representing the information.
- **Document-Level Attention:** This mechanism focuses on the relationships between sentences within a single dialogue to better understand the context and resolve ambiguity. It weights hidden states of different sentences based on their relevance.
- **Corpus-Level Attention:** To capture information from a broader range of dialogues, the model also uses corpus-level attention. This mechanism finds supporting sentences from a larger collection of dialogues that contain the same word, allowing the model to leverage broader associations.
- **Integration:** The outputs of both document-level and corpus-level attention are combined and fed into another Bi-LSTM model to create a final contextualized representation of each word.
- **Symptom Recognition:** The model uses a Conditional Random Field (CRF) as a decoder to perform symptom recognition, leveraging the contextualized word representations.
- **Symptom Graph:** The authors also explored using a symptom graph to understand the associations between different symptoms, finding that incorporating this graph improves the accuracy of symptom inference, especially for highly associated symptoms.

**In essence, the work aims to improve symptom recognition by going beyond individual sentence context and incorporating information from the entire dialogue and a broader corpus, while also considering relationships between symptoms.**
# Paper
![[D19-1508.pdf]]
# See also
[[Research Paper Summaries]]
# Source
- https://aclanthology.org/D19-1508/