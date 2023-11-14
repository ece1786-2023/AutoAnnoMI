"""
Seven transcripts/conversations in the original AnnoMI dataset has multiple 
annotations. These conversations were used to measure the IAA in the original 
paper.  We decided to drop these conversations from out experiments as they 
could cause confusion down-the-line.
"""
from pathlib import Path

import pandas as pd

DATASET_PATH = Path(__file__).parents[1] / "data"
INPUT_PATH = DATASET_PATH / "unprocessed" / "AnnoMI-full.csv"
OUTPUT_PATH = DATASET_PATH / "unprocessed" / "AnnoMI-full-unique-annotation.csv"


if __name__ == "__main__":
    input_df = pd.read_csv(INPUT_PATH)
    print(f"{len(input_df.transcript_id.unique())=}")
    transcript_ids_with_multiple_annotations = [
        transcript_id
        for transcript_id, transcript in input_df.groupby("transcript_id")
        if len(transcript.annotator_id.unique()) > 1
    ]

    output_df = input_df[
        ~input_df.transcript_id.isin(transcript_ids_with_multiple_annotations)
    ]
    print(f"{len(output_df.transcript_id.unique())=}")
    output_df.to_csv(OUTPUT_PATH, index=False)
