import json
import os
import time
from typing import Any

import requests

from config import API_URL, HEADERS, REQUEST_DELAY_SECONDS, RAW_HTML_DIR


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def safe_name(title: str) -> str:
    return (
        title.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace(":", "_")
    )


def fetch_parse_text(title: str) -> dict[str, Any]:
    params = {
        "action": "parse",
        "page": title,
        "prop": "text|sections",
        "format": "json",
        "redirects": 1,
    }

    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise RuntimeError(f"API error for {title}: {data['error']}")

    return data


def save_raw_payload(title: str, payload: dict[str, Any]) -> str:
    ensure_dir(RAW_HTML_DIR)
    path = os.path.join(RAW_HTML_DIR, f"{safe_name(title)}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def fetch_and_cache_page(title: str) -> dict[str, Any]:
    payload = fetch_parse_text(title)
    save_raw_payload(title, payload)
    time.sleep(REQUEST_DELAY_SECONDS)
    return payload