"""Script to fix the transcripts mislabels using GPT-4.
"""
import argparse
import os
import time
from pathlib import Path

import backoff
import openai
import pandas as pd
from openai import OpenAI

# Path globals
DATASET_PATH = Path("data")
INPUT_DF_PATH = (
    DATASET_PATH / "unprocessed" / "AnnoMI-full-unique-annotation.csv"
)
MISLABELED_IDS_PATH = (
    DATASET_PATH / "unprocessed" / "potentially_mislabeled_transcripts.txt"
)
FIXED_LABELS_PATH = DATASET_PATH / "fixed" / "fixed_by_gpt4"
DONE_FILES = DATASET_PATH / "fixed" / "fixed_by_gpt4" / "done"
VERIFIED_PATH = DATASET_PATH / "fixed" / "fixed_labels_manually_verified.csv"
FINAL_FIXED_PATH = DATASET_PATH / "fixed" / "AnnoMI-full-fixed.csv"

# GPT-4 globals
MODEL = "gpt-4-1106-preview"
SYSTEM_PROMPT = (
    "Imagine a dialogue between a therapist and a client presented in a "
    "structured format. Each statement is represented as follows: "
    "'[utterance id] | [interlocutor label] | [utterance text]'. In some "
    "cases, the labels identifying who is speaking (therapist or client) may "
    "be incorrect. Your task is to identify any statements where the speaker "
    "label does not match the content of the utterance. For each incorrect "
    "label, provide your response in the format: '[utterance id]', listing "
    "each one on a new line. DO NOT output the utterance text, just the "
    "utterance id"
)


@backoff.on_exception(backoff.expo, openai.RateLimitError)
def get_fixed_labels(utterances: str, client: OpenAI) -> str:
    response = client.with_options(
        timeout=30, max_retries=2
    ).chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": utterances,
            },
        ],
        temperature=0.0,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


def parse_args():
    parser = argparse.ArgumentParser(
        prog="get_fixed_labels_using_gpt4.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--step",
        required=True,
        type=int,
        help="Step to run in the script",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    api_key = os.environ["OPENAI_API_KEY"]
    org_id = os.environ["OPENAI_ORG_ID"]
    client = OpenAI(organization=org_id, api_key=api_key)

    df = pd.read_csv(INPUT_DF_PATH)
    with open(MISLABELED_IDS_PATH, encoding="utf-8") as file:
        mislabeled_tx = list(map(int, file.read().split()))

    if args.step == 1:
        # Get GPT-4 fixed labels and store it somewhere ($$$ expensive step)
        user_answer = input(
            "You are going to re-generate the fixed labels using the GPT-4 "
            "API. Type 'Y' to continue: "
        )
        if user_answer != "Y":
            exit()
        messages = dict()
        for tx_id in mislabeled_tx:
            messages[tx_id] = []
            for idx, row in df[df.transcript_id == tx_id].iterrows():
                text = f"{idx:4d} | {row.interlocutor} | {row.utterance_text}"
                messages[tx_id].append(text)

        for tx_id in mislabeled_tx:
            if (DONE_FILES / f"{tx_id}.done").exists():
                print(f"{tx_id} already done. Skipping")
                continue
            utterances = "\n".join(messages[tx_id])
            print(tx_id)
            try:
                fixed_labels = get_fixed_labels(
                    utterances=utterances, client=client
                )
                print(fixed_labels)
                print("-" * 80)
                with open(
                    FIXED_LABELS_PATH / f"{tx_id}.txt", "w", encoding="utf-8"
                ) as file:
                    file.write(fixed_labels)
                with open(
                    DONE_FILES / f"{tx_id}.done", "w", encoding="utf-8"
                ) as file:
                    pass
            except Exception as exc:
                print(exc, f"{tx_id=}")
                pass
            time.sleep(5)

    if args.step == 2:
        user_answer = input(
            "Before proceeding, make sure you have manually verified the "
            "fixed label suggestions bu GPT-4 and have created "
            "fixed_labels_manually_verified. Press 'Y' to continue: "
        )
        if user_answer != "Y":
            exit()
        df_original = pd.read_csv(INPUT_DF_PATH)
        df_verified = pd.read_csv(VERIFIED_PATH)
        assert len(df_original) == len(df_verified)
        for idx, row in df_original.iterrows():
            if row.interlocutor != df_verified.loc[idx, "interlocutor"]:
                print(idx)
        user_answer = input("Press 'Y' to proceed: ")
        if user_answer != "Y":
            exit()
        df_original.interlocutor = df_verified.interlocutor
        df_original.to_csv(FINAL_FIXED_PATH)
