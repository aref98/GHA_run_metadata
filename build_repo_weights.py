"""
** You do NOT need to run this script **
** For anyone wondering, where this script fits in:
This is a one-time script to build the repo_weights.csv file, which assigns a weight to each repository based on the number of historical runs it has in the collected data. This weighting is used to prioritize repositories with more activity when sharding the workload for the new 10-worker collection. This was used in our data collection process to ensure that we focus more on repositories that have more historical runs, which are likely to yield richer data for our analysis.

"""

import glob
import json
from collections import Counter
import pandas as pd
import config

RUNS_PATTERN = "graphql/runs_shard_*.jsonl"
OUTPUT_FILE = "repo_weights.csv"


def build_weights():
    files = sorted(glob.glob(RUNS_PATTERN))
    print(f"[*] Found {len(files)} runs files.")

    counts = Counter()
    total_lines = 0

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    run = json.loads(line)
                except json.JSONDecodeError:
                    continue
                repo = run.get('repository', {})
                if isinstance(repo, dict):
                    name = repo.get('full_name')
                else:
                    name = repo  # fallback if already a string
                if name:
                    counts[name] += 1
                    total_lines += 1

    print(f"[*] Counted {total_lines:,} runs across {len(counts):,} repos.")

    # Load the full repo list from the input CSV so every repo appears,
    # even those with 0 historical runs.
    df_all = pd.read_csv(config.INPUT_FILE)
    all_repos = df_all['repository'].drop_duplicates().tolist()
    print(f"[*] Total repos in input CSV: {len(all_repos):,}")

    weights = pd.DataFrame({'repository': all_repos})
    weights['run_count'] = weights['repository'].map(counts).fillna(0).astype(int)
    weights = weights.sort_values('run_count', ascending=False).reset_index(drop=True)

    weights.to_csv(OUTPUT_FILE, index=False)
    print(f"[*] Saved {len(weights):,} repos to {OUTPUT_FILE}")
    print("\nTop 10 most active repos:")
    print(weights.head(10).to_string(index=False))
    print(f"\nRepos with 0 historical runs: {(weights['run_count'] == 0).sum():,}")


if __name__ == "__main__":
    build_weights()
