# Overview
PubMed® comprises more than 39 million citations for biomedical literature from MEDLINE, life science journals, and online books. Citations may include links to full text content from PubMed Central and publisher web sites.
# Content
Citations in PubMed primarily stem from the biomedicine and health fields, and related disciplines such as life sciences, behavioral sciences, chemical sciences, and bioengineering.

PubMed facilitates searching across several NLM literature resources:
- MEDLINE
	- [MEDLINE](https://www.nlm.nih.gov/bsd/medline.html) is the largest component of PubMed and consists primarily of citations from journals selected for MEDLINE; articles indexed with MeSH (Medical Subject Headings) and curated with funding, genetic, chemical and other metadata.
- PubMed Central (PMC)
	- Citations for [PubMed Central (PMC)](https://www.ncbi.nlm.nih.gov/pmc/about/intro/) articles make up the second largest component of PubMed. PMC is a full text archive that includes articles from journals reviewed and selected by NLM for archiving (current and historical), as well as individual articles collected for archiving in compliance with funder policies.
- Bookshelf
	- The final component of PubMed is citations for books and some individual chapters available on [Bookshelf](https://www.ncbi.nlm.nih.gov/books/)Bookshelf is a full text archive of books, reports, databases, and other documents related to biomedical, health, and life sciences.
# Uses
- In [[DKG-LLM Datasets]], this is used to evaluate the dynamic knowledge graph architecture
# Downloading data
- Annual baseline
	- Once a year, NLM produces a baseline set of PubMed citation records in XML format for download; the baseline file is a complete snapshot of PubMed data. When using this data in a local database, the best practice is to overwrite your local data each year with the baseline data.
		- PubMed 2026 Baseline: https://www.nlm.nih.gov/pubs/techbull/jf26/jf26_PubMed_2026_BaselineRelease.html
- Daily update files
	- Each day, NLM produces update files that include new, revised, and deleted citations. If you are incorporating these update XML files into a local database, load the baseline files first, then load the daily update files in numerical order. Revised or deleted citations should replace existing citations in your local database. More than one update file may become available on the same day.
# Querying data
- API information
	- https://www.ncbi.nlm.nih.gov/books/NBK25497/
- <mark>Python library for querying</mark>
	- https://metapub.org
		- https://metapub.readthedocs.io/en/latest/examples.html
		- https://metapub.readthedocs.io/en/latest/pubmedarticle_properties.html
# See also
- [[DKG-LLM Datasets]]
# Source
- https://pubmed.ncbi.nlm.nih.gov
- https://www.ncbi.nlm.nih.gov/myncbi/