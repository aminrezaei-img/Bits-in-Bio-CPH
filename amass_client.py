"""
Bio Project Triage — Amass API client.
Unlocks data silos: literature, trials, drugs.
"""
import os
import requests
from functools import lru_cache

BASE_URL = "https://api.amass.tech/api/v1/cores"


def _load_api_key():
    """Load API key from file or environment."""
    key_file = os.path.join(os.path.dirname(__file__), "AMASS-API-KEY.md")
    if os.path.exists(key_file):
        with open(key_file) as f:
            return f.read().strip()
    return os.environ.get("AMASS_API_KEY", "")


API_KEY = _load_api_key()
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

# Core name -> (path, display name, icon)
CORES = {
    "biomedcore": ("biomedcore", "Literature", "📄"),
    "trialcore": ("trialcore", "Clinical Trials", "🔬"),
    "drugcore": ("drugcore", "Drugs & Interventions", "💊"),
    "regulatorycore": ("regulatorycore", "Regulatory", "🏛️"),
    "patentcore": ("patentcore", "Patents", "📜"),
}


def search_core(core_name: str, query: str, limit: int = 20) -> dict:
    """
    Search a single Amass core. Returns {"records": [...], "total": N, "error": None}
    or {"records": [], "total": 0, "error": "message"} on failure.
    """
    if core_name not in CORES:
        return {"records": [], "total": 0, "error": f"Unknown core: {core_name}"}

    core_path, _, _ = CORES[core_name]
    url = f"{BASE_URL}/{core_path}/records"

    try:
        r = requests.get(
            url,
            params={"query": query, "limit": limit},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        body = r.json()
        data = body.get("data", body)  # API wraps in {"data": ...}
        records = data.get("records", data) if isinstance(data, dict) else data
        if isinstance(records, list):
            return {"records": records, "total": len(records), "error": None}
        return {"records": [], "total": 0, "error": None}
    except requests.exceptions.Timeout:
        return {"records": [], "total": 0, "error": "Request timed out"}
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else None
        if status == 429:
            return {"records": [], "total": 0, "error": "Rate limited — try again shortly"}
        if status == 401:
            return {"records": [], "total": 0, "error": "API key invalid"}
        return {"records": [], "total": 0, "error": f"API error ({status})"}
    except Exception as e:
        return {"records": [], "total": 0, "error": str(e)}


def search_all(query: str, cores=None, limit: int = 20) -> dict:
    """
    Search multiple cores. Returns {"core_name": {"records": [...], "total": N, "error": ...}, ...}
    """
    if cores is None:
        cores = list(CORES.keys())
    results = {}
    for core_name in cores:
        results[core_name] = search_core(core_name, query, limit)
    return results


def extract_field(record, *keys, default=""):
    """Safely extract nested fields from a record."""
    val = record
    for key in keys:
        if isinstance(val, dict):
            val = val.get(key)
        elif isinstance(val, list) and isinstance(key, int):
            val = val[key] if key < len(val) else None
        else:
            return default
    return val if val is not None else default
