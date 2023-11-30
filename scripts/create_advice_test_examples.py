"""Script to create a balanced advice test examples dataset

Creates a directory containing CSVs of conversations. Each conversation is from 
the original conversation and it has rows upto the therapist utterance with the 
target label.

This gives us 12 examples for each of the catagories: ADP, ADW, False
These examples can be used to test different prompting strategies
"""
import random
import uuid
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(2023)
np.random.seed(2023)

# Path globals
DATASET_PATH = Path("data")
TEST_DF_PATH = DATASET_PATH / "added_labels" / "ADP_ADW labeling - test.csv"
TEST_EXAMPLE_PATH = DATASET_PATH / "added_labels" / "advice_test_examples"
NUM_EXAMPLES_PER_LABEL = {"ADP": 11, "ADW": 19, "none": 15}


if __name__ == "__main__":
    test_df = pd.read_csv(TEST_DF_PATH)
    print(f"{len(test_df) = }")
    test_df = test_df.sort_values(
        by=["transcript_id", "utterance_id", "annotator_id"]
    )

    examples = {"ADP": [], "ADW": [], "none": []}
    for tx_id in test_df["transcript_id"].unique():
        df = test_df[test_df.transcript_id == tx_id].reset_index(drop=True)
        for idx in df.index:
            cur_row = df.loc[idx]
            if not cur_row.interlocutor == "therapist":
                continue
            # Save the dataframe upto this point in the conversation
            if cur_row.advice_subtype == "ADP":
                examples["ADP"].append(df.loc[:idx])
            if cur_row.advice_subtype == "ADW":
                examples["ADW"].append(df.loc[:idx])
            if not cur_row.advice_exists:
                examples["none"].append(df.loc[:idx])

    for name, example_dfs in examples.items():
        print(f"{name}, {len(example_dfs) = }")
        examples[name] = random.sample(example_dfs, NUM_EXAMPLES_PER_LABEL[name])
    for name, example_dfs in examples.items():
        print(f"After keeping only {NUM_EXAMPLES_PER_LABEL[name]} for {name} label: ")
        print(f"{name}, {len(example_dfs) = }")

    # Save
    for name, example_dfs in examples.items():
        out_dir = TEST_EXAMPLE_PATH / name
        out_dir.mkdir(parents=True, exist_ok=True)
        for df in example_dfs:
            transcript_id = list(df.transcript_id)[0]
            out_csv = out_dir / f"{transcript_id}_{uuid.uuid4()}.csv"
            df.to_csv(out_csv, index=False)
