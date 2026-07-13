import os
from typing import List

import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def _headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "attack-enrichment-service",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers
def get_sigma_rules(technique_id: str) -> List[dict]:
    query = f"{technique_id} repo:SigmaHQ/sigma"

    response = requests.get(
        f"{GITHUB_API}/search/code",
        params={
            "q": query,
            "per_page": 3,
        },
        headers=_headers(),
        timeout=30,
    )

    if response.status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            raise RuntimeError(
                "GitHub API rate limit exceeded. Configure GITHUB_TOKEN in your .env file."
            )

    response.raise_for_status()

    data = response.json()

    rules = []

    for item in data.get("items", [])[:3]:
        raw_url = (
            item["html_url"]
            .replace(
                "https://github.com/",
                "https://raw.githubusercontent.com/",
            )
            .replace("/blob/", "/")
        )

        rules.append(
            {
                "title": item["name"],
                "raw_url": raw_url,
            }
        )

    return rules