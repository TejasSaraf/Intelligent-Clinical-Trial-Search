import json
import sys
from pathlib import Path
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from config import ES_HOST, INDEX_NAME, DATA_DIR, CLINICAL_TRIALS_JSON
from elasticsearch_mapping import get_index_mapping

BACKEND_ROOT = Path(__file__).resolve().parent


def load_json_path(json_path: Path) -> list[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected clinical_trials.json to be a JSON array")
    return data


def _parse_boolean(value, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    s = str(value).strip().upper()
    if s in ("", "NA", "N/A", "NONE", "UNKNOWN"):
        return default
    if s in ("TRUE", "YES", "1", "1.0"):
        return True
    if s in ("FALSE", "NO", "0", "0.0"):
        return False
    return default


def _parse_enrollment(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    s = str(value).strip().replace(",", "")
    if not s or s.lower() in ("none", "na", ""):
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def _flatten_doc(raw: dict) -> dict:
    doc = {k: v for k, v in raw.items()}

    conditions = raw.get("conditions") or []
    doc["condition_names"] = [
        c.get("name") for c in conditions
        if isinstance(c, dict) and c.get("name")
    ]
    doc["conditions"] = conditions

    sponsors = raw.get("sponsors") or []
    doc["sponsor_names"] = [
        s.get("name") for s in sponsors
        if isinstance(s, dict) and s.get("name")
    ]
    doc["sponsors"] = sponsors

    facilities = raw.get("facilities") or []
    countries = set()
    states = set()
    cities = set()
    for f in facilities:
        if not isinstance(f, dict):
            continue
        if f.get("country"):
            countries.add(f["country"].strip())
        if f.get("state"):
            states.add(f["state"].strip())
        if f.get("city"):
            cities.add(f["city"].strip())
    doc["facility_countries"] = list(countries)
    doc["facility_states"] = list(states)
    doc["facility_cities"] = list(cities)
    doc["facilities"] = facilities

    age_list = raw.get("age") or []
    doc["age_categories"] = [
        a.get("age_category") for a in age_list
        if isinstance(a, dict) and a.get("age_category")
    ]
    doc["age"] = age_list

    doc["enrollment"] = _parse_enrollment(raw.get("enrollment"))
    doc["healthy_volunteers"] = _parse_boolean(
        raw.get("healthy_volunteers"), default=False)

    for date_field in (
        "study_first_submitted_date", "last_update_submitted_date",
        "last_update_posted_date", "start_date", "completion_date",
        "primary_completion_date", "results_first_posted_date"
    ):
        if doc.get(date_field) is None:
            continue
        val = doc[date_field]
        if hasattr(val, "isoformat"):
            doc[date_field] = val.isoformat()

    return doc


def create_index(es: Elasticsearch, index: str, mapping: dict) -> None:
    if es.indices.exists(index=index):
        es.indices.delete(index=index)
    es.indices.create(index=index, body=mapping)


def bulk_index(es: Elasticsearch, index: str, docs: list[dict], batch_size: int = 500) -> int:
    def gen():
        for d in docs:
            yield {"_index": index, "_source": d}

    success, failed = bulk(
        es, gen(), chunk_size=batch_size,
        raise_on_error=False, raise_on_exception=True
    )
    return success


def run_ingest() -> None:
    json_path = BACKEND_ROOT / DATA_DIR / CLINICAL_TRIALS_JSON
    if not json_path.exists():
        sys.exit(1)

    raw_docs = load_json_path(json_path)

    docs = [_flatten_doc(d) for d in raw_docs]

    es = Elasticsearch(ES_HOST)
    if not es.ping():
        sys.exit(1)

    mapping = get_index_mapping()
    create_index(es, INDEX_NAME, mapping)
    es.indices.refresh(index=INDEX_NAME)