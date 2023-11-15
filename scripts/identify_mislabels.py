"""Script to flag transcripts/conversations from the original AnnoMI dataset 
that may have misplaced interlocutor labels.

The script is simple. It assumes that consecutive utterances in any transcript 
should be spoken by different interlocutors. If this condition is violated, it
flags such transcripts.
"""
from pathlib import Path

import pandas as pd

DATASET_PATH = Path(__file__).parents[1] / "data"
INPUT_PATH = DATASET_PATH / "unprocessed" / "AnnoMI-full-unique-annotation.csv"
OUTPUT_PATH = (
    DATASET_PATH / "unprocessed" / "potentially_mislabeled_transcripts.txt"
)

if __name__ == "__main__":
    input_df = pd.read_csv(INPUT_PATH)
    flagged_transcript_ids = []
    for transcript_id, transcript in input_df.groupby("transcript_id"):
        transcript = transcript.sort_values(by="utterance_id").reset_index(
            drop=True
        )
        even_indices = range(0, len(transcript), 2)
        odd_indices = range(1, len(transcript), 2)
        even_interlocutors = transcript.iloc[even_indices].interlocutor.unique()
        odd_interlocutors = transcript.iloc[odd_indices].interlocutor.unique()
        if (
            len(even_interlocutors) == 1
            and len(odd_interlocutors) == 1
            and not set(even_interlocutors).intersection(set(odd_interlocutors))
        ):
            continue
        flagged_transcript_ids.append(transcript_id)

    print(f"{len(flagged_transcript_ids) = }")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        for _id in flagged_transcript_ids:
            file.write(f"{_id}\n")
