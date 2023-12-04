"""Script to run the more-context prompt on advice test examples and get the 
results.

To run MORE CONTEXT WITH EXAMPLES:

python experiments/05_advice_more_context/get_more_context_results.py \
    --prompt_file prompts/advice/more_context.txt \
    --test_dir data/added_labels/advice_test_examples \
    --output_file data/experiment_outputs/advice_fewshot_more_context.csv

To run MORE CONTEXT NO EXAMPLES:

python experiments/05_advice_more_context/get_more_context_results.py \
    --prompt_file prompts/advice/more_context_no_examples.txt \
    --test_dir data/added_labels/advice_test_examples \
    --output_file data/experiment_outputs/advice_fewshot_more_context_no_examples.csv
"""
"""Script to fix the transcripts mislabels using GPT-4.
"""
import argparse
import os
import random
import time
from pathlib import Path

import backoff
import openai
import pandas as pd
from openai import OpenAI

LABELS = ["ADP", "ADW", "none"]
MODEL = "gpt-4-1106-preview"


def collate_all_test_examples(test_dir):
    """
    Read all the CSVs in the test_dir and create
    (file_name, df, label) pairs
    """
    df_labels = []
    for label in LABELS:
        for csv_file in (Path(test_dir) / label).glob("*.csv"):
            df = pd.read_csv(csv_file)
            df_labels.append((str(csv_file), df, label))
    # shuffle the list
    random.shuffle(df_labels)
    return df_labels


def get_user_prompt_from_df(df):
    """Since this is the baseline, get the last client, therapist turn"""
    utterances = list(df.utterance_text)[-6:]
    interlocutors = list(df.interlocutor)[-6:]
    user_prompt = ''

    for interlocutor, utt in zip(interlocutors, utterances):
        user_prompt += f'{interlocutor.title()}: {utt}\n'
    return user_prompt


def get_system_prompt(prompt_file):
    with open(prompt_file, encoding="utf-8") as file:
        return file.read().strip()


@backoff.on_exception(backoff.expo, openai.RateLimitError)
def run_api(client, system_prompt, user_prompt) -> str:
    response = client.with_options(
        timeout=30, max_retries=2
    ).chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.0,
        max_tokens=4,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt_file", required=True, type=str)
    parser.add_argument("--test_dir", required=True, type=str)
    parser.add_argument("--output_file", required=True, type=str)
    return parser.parse_args()


def api_output_to_label(output):
    for label in LABELS:
        if label.lower() in output.lower():
            return label
    return output

if __name__ == "__main__":
    args = parse_args()
    # api_key = os.environ["OPENAI_API_KEY"]
    # org_id = os.environ["OPENAI_ORG_ID"]
    # client = OpenAI(organization=org_id, api_key=api_key)
    client = OpenAI()

    print(f"{args.prompt_file = }")
    system_prompt = get_system_prompt(args.prompt_file)
    print("-" * 80)
    print("SYSTEM PROMPT:")
    print(system_prompt)
    print("-" * 80)
    print(f"{args.test_dir = }")
    print(f"{args.output_file = }")

    # If output file already exists, read it. Otherwise, create it
    try:
        out_df = pd.read_csv(args.output_file, index_col="csv_file")
    except FileNotFoundError:
        out_df = pd.DataFrame(
            columns=[
                "system_prompt",
                "user_prompt",
                "true_label",
                "predicted_label",
                "success",
                "done",
            ]
        )
        out_df.index.name = "csv_file"

    df_labels = collate_all_test_examples(args.test_dir)
    print(f'{len(df_labels) = }')
    num_done = 0
    for csv_file, df, label in df_labels:
        print("-" * 80)
        print(f'{csv_file = }')
        if not out_df.done.get(csv_file, False):
            print(f"Index {csv_file} has no results. Running the API")

            user_prompt = get_user_prompt_from_df(df)
            print("User prompt: ")
            print(user_prompt)
            api_output = run_api(
                client=client,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            print(f"{api_output = }")
            print(f"{label = }")
            api_output = api_output.strip().lower()
            predicted_label = None
            predicted_label = api_output_to_label(api_output)
            out_df.loc[csv_file] = {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "true_label": label,
                "predicted_label": predicted_label,
                "success": predicted_label == label,
                "done": True,
            }
            if (predicted_label == label):
                print('SUCCESS')
            else:
                print(f'{predicted_label}!={label} -> failed')
            num_done += 1

            time.sleep(1)
        else:
            print(f"Index {csv_file} has already been completed. SKIPPING")
        out_df.to_csv(args.output_file, index_label="csv_file")

    print(f"{num_done = }")
    print(
        f"Accuracy = "
        f"{sum(out_df.true_label == out_df.predicted_label) / len(out_df)}"
    )
