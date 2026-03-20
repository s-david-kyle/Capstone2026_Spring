# Overview
Main Dataset The MTS-Dialog dataset is a new collection of 1.7k short doctor-patient conversations and corresponding summaries (section headers and contents).

The training set consists of 1,201 pairs of conversations and associated summaries.

The validation set consists of 100 pairs of conversations and their summaries.

The "dialogue" column contain Doctor-Patient conversation. The "section_text" column contains the Clinical Note of the Doctor-Patient conversation. This clinical note is of the format : 

- Symptoms:
- Diagnosis:
- History of Patient:
- Plan of Action: *** N/A is given if no information is found for each of the sections.
# See also
- [[Part 1]]
# Source
- https://huggingface.co/datasets/har1/MTS_Dialogue-Clinical_Note