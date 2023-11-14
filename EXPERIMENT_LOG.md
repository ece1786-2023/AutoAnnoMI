# Experiments Log
This is the log of what was done, the motivation behind a task, the results and the discussion.

The format of the log is:

[`DATE`]| [`EXPERIMENTER`] | [`TITLE`]
- [`Motivation`]
- [`Steps`]
- [`Input (files, scripts)`]
- [`Files created and their location`]
- [`Results`]
- [`Discussion`]

2023-11-14 | Zafar | Skip (7) transcripts/conversations annotated by more than one annotator
- Motivation: The [AnnoMI paper](https://www.mdpi.com/1999-5903/15/3/110) mentions that they calculated "utterance-level inter-annotator agreement (IAA) over the annotations on the 7 transcripts." I believe we should drop these transcripts from the data labelling as it will cause confusion down the line when we calculate the agreement between LLMs and annotators.
- Steps: I created the script `scripts/drop_transcripts_with_multiple_annotations.py` to drop those transcripts that had multiple annotations.
- Input files: `data/unprocessed/AnnoMI-full.csv`
- Output file: The script `scripts/drop_transcripts_with_multiple_annotations.py` creates `data/unprocessed/AnnoMI-full-unique-annotation.csv`.
- Results: The number of conversations dropped from 133 to 126.
- Discussion: **For future experimentation, we will NOT use `data/unprocessed/AnnoMI-full.csv`, but instead, will use `data/unprocessed/AnnoMI-full-unique-annotation.csv`.**



2023-11-14 | Zafar | Basic script to identify the mislabeled transcripts
- Motivation: We know that the original dataset from the AnnoMI repository does not have the correct labels for therapists and clients. It is essential to fix the data before adding therapist-specific labels (reflection, advice, etc.) using LLMs.
- Steps: I created a basic Python script that iterates over each conversation in `data/unprocessed/AnnoMI-full-unique-annotation.csv` and flags those conversations where any consecutive utterance has the same interlocutor label. The script assumes that no two consecutive utterances should be spoken by the same person. The script further assumes that if a conversation does not have consecutive utterances spoken by the same person/interlocutor, all the  interlocutor labels are correct.
- Input files: `data/unprocessed/AnnoMI-full-unique-annotation.csv`.
- Output files: The script `scripts/identify_mislabels.py` creates `data/unprocessed/potentially_mislabeled_transcripts.txt` which contains ids of the transcripts/conversations that are problematic.
- Results: 20 transcripts were flagged by the script as having mislabels.
- Discussion: I plan to manually check if the flagged conversations have mislabels. I may use LLMs to identify/fix such conversations.
