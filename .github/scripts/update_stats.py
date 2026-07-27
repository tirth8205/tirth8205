#!/usr/bin/env python3
"""Refresh the star and fork counts shown in README.md.

Fetches live numbers from the GitHub API, rounds them down so wording
like "reached 26,800+ stars" always stays true, and rewrites the values
between the invisible <!--STARS--> and <!--FORKS--> markers. The result
renders as ordinary text, not a badge.
"""

import json
import os
import re
import sys
import urllib.request

REPO = "tirth8205/code-review-graph"
README = "README.md"
ROUND_TO = 100  # 1 = exact counts, 1000 = chunkier numbers


def fetch_counts():
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "readme-stats-updater",
        },
    )
    token = os.environ.get("GH_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    return data["stargazers_count"], data["forks_count"]


def replace(text, marker, value):
    pattern = rf"(<!--{marker}-->).*?(<!--/{marker}-->)"
    updated, count = re.subn(pattern, rf"\g<1>{value:,}\g<2>", text)
    if count == 0:
        sys.exit(f"Marker <!--{marker}--> not found in {README}")
    return updated


def main():
    stars, forks = fetch_counts()
    shown_stars = stars // ROUND_TO * ROUND_TO
    shown_forks = forks // ROUND_TO * ROUND_TO

    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = replace(text, "STARS", shown_stars)
    text = replace(text, "FORKS", shown_forks)
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Live: {stars:,} stars / {forks:,} forks "
          f"-> shown as {shown_stars:,} / {shown_forks:,}")


if __name__ == "__main__":
    main()
