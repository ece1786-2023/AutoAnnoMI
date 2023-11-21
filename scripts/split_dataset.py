"""Script to split the fixed dataset into train and test.
Train size = 4 conversations
Test size = 16 conversations
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Path globals
DATASET_PATH = Path("data")
INPUT_DF_PATH = DATASET_PATH / "fixed" / "AnnoMI-full-fixed.csv"
SPLIT_PATH = DATASET_PATH / "split"

# Split globals
PREFERRED_TOPICS = [
    "reducing alcohol consumption",
    "smoking cessation",
    "diabetes management",
    "reducing drug use",
]
PREFERRED_QUALITY = ["high"]
TRAIN_SIZE = 4
TEST_SIZE = 16

if __name__ == "__main__":
    df = pd.read_csv(INPUT_DF_PATH)
    print(f"{len(df) = }")

    print(f"Keeping only transcripts with quality in {PREFERRED_QUALITY}")
    df = df[df.mi_quality.isin(PREFERRED_QUALITY)]
    df = df.drop('Unnamed: 0', axis=1)
    print(f"{len(df) = }")

    print(f"Keeping only transcripts with topic in {PREFERRED_TOPICS}")
    df = df[df.topic.isin(PREFERRED_TOPICS)]
    print(f"{len(df) = }")

    dfs = [
        df[df.transcript_id == tx_id].reset_index(drop=True)
        for tx_id in df.transcript_id.unique()
    ]
    filtered_dfs = []
    for _df in dfs:
        _df = _df.reset_index(drop=True)
        even_indices = list(range(0, len(_df), 2))
        odd_indices = list(range(1, len(_df), 2))
        even_interlocutor = set(_df.iloc[even_indices].interlocutor)
        odd_interlocutor = set(_df.iloc[odd_indices].interlocutor)
        if (
            len(even_interlocutor) == 1
            and len(odd_interlocutor)
            and even_interlocutor.intersection(odd_interlocutor) == set()
        ):
            filtered_dfs.append(_df)
    dfs = filtered_dfs

    train, test = train_test_split(
        np.array([list(df.transcript_id)[0] for df in dfs]),
        test_size=TEST_SIZE,
        train_size=TRAIN_SIZE,
        random_state=None,
        shuffle=True,
        stratify=np.array([list(df.topic)[0] for df in dfs]),
    )

    splits = {"train": train, "test": test}

    for split_name, split_ids in splits.items():
        print("-" * 80)
        print(f"{split_ids = }")
        print(f"{split_name = }")
        df_split = df[df.transcript_id.isin(split_ids)]
        print()
        print(df_split.topic.value_counts())
        print()
        print(f"{len(df_split) = }")
        print(f"{len(df_split[df_split.reflection_exists == True]) = }")
        print(f"{len(df_split[df_split.reflection_exists == False]) = }")
        print(f'{len(df_split[df_split.reflection_subtype == "simple"]) = }')
        print(f'{len(df_split[df_split.reflection_subtype == "complex"]) = }')
        df_split.to_csv(SPLIT_PATH / f"{split_name}.csv", index=False)
