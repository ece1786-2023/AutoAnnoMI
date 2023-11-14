# AutoAnnoMI
### A Framework to Automate the Annotations of MI Conversations using LLMs

## Introduction
The project aims to build a large language model (LLM) based application that assists experts in annotating motivational interviewing (MI) transcripts. We experiment with an annotated dataset of MI conversations ([AnnoMI](https://github.com/uccollab/AnnoMI)) to generate prompts for GPT-4 and show their success in providing the correct [MISC](https://www.cambridge.org/core/journals/behavioural-and-cognitive-psychotherapy/article/motivational-interviewing-skill-code-reliability-and-a-critical-appraisal/AA20C5D4892F60725A753EFDEF71BB22) labels for client and therapist utterances. Through our experiments with different prompting strategies, we plan to demonstrate the viability of creating an LLM-in-the-loop annotation application that has the potential to aid expert annotators, increasing both the annotation efficiency and reliability.

## Requirements & Installation
-   Python 3.10
-   Install required python packages `pip install -r requirements.txt`.


## Contents
*   `data/`: All the data for the project.
*   `docs/`: Contains the documentation (project proposal, progress report, etc.)
*   `scripts/`: Data cleaning, GPT-4 API calls, etc.



