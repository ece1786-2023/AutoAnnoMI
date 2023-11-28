# Directory where all the data lives

## Contents of the directory
*   `unprocessed`: All the unprocessed data. Intermediate data from our processing/cleaning also lives here.
    *   `unprocessed/AnnoMI-full.csv`: Original data (133 conversations) from the [AnnoMI repository](https://github.com/uccollab/AnnoMI/tree/main).
    *   `unprocessed/AnnoMI-full-unique-annotation.csv`: Dataset with 126 conversations, obtained after dropping those conversations that were annotated by multiple annotators. We decided to drop these seven conversations to avoid confusion, and the resulting dataset is stored here.
    *   `potentially_mislabeled_transcripts.txt`: Ids of the transcripts that were flagged as having potential issues with their interlocutor labels.

*   `fixed/`: Data after removing the inconsistencies in it. Refer to Section 3 (Source of Data and Processing) of the Project Proposal document for more information.

*   `added_labels/`: Data after adding "advice_exists" and "advice_subtype" columns.

*   `labeled/baseline/`: Will contain the labels from the baseline model or prompt.

*   `labeled/final`: Will contain the final labels from the GPT-4 model.
