from elasticsearch import Elasticsearch

from config import ES_HOST, INDEX_NAME
from search.parser import SearchIntent


def build_query(intent: SearchIntent) -> dict:
    must: list[dict] = []
    should: list[dict] = []
    filter_clauses: list[dict] = []

    if intent.phase:
        filter_clauses.append({"term": {"phase": intent.phase}})
    if intent.overall_status:
        filter_clauses.append({"term": {"overall_status": intent.overall_status}})
    if intent.facility_country:
        filter_clauses.append({"term": {"facility_countries": intent.facility_country}})

    _fuzzy = {"fuzziness": 1}
    _exact_boost = 2.0
    _fuzzy_boost = 0.5

    if intent.condition:
        must.append({
            "bool": {
                "should": [
                    {"match_phrase": {"condition_names.text": {"query": intent.condition, "boost": _exact_boost}}},
                    {"match": {"condition_names.text": {"query": intent.condition, **_fuzzy, "boost": _fuzzy_boost}}},
                ],
                "minimum_should_match": 1,
            }
        })

    if intent.title_contains:
        q = intent.title_contains
        must.append({
            "bool": {
                "should": [
                    {"match_phrase": {"brief_title": {"query": q, "boost": _exact_boost}}},
                    {"match_phrase": {"official_title": {"query": q, "boost": _exact_boost}}},
                    {"match_phrase": {"brief_summaries_description": {"query": q, "boost": _exact_boost}}},
                    {"match": {"brief_title": {"query": q, **_fuzzy, "boost": _fuzzy_boost}}},
                    {"match": {"official_title": {"query": q, **_fuzzy, "boost": _fuzzy_boost}}},
                    {"match": {"brief_summaries_description": {"query": q, **_fuzzy, "boost": _fuzzy_boost}}},
                ],
                "minimum_should_match": 1,
            }
        })

    if intent.keywords and not intent.title_contains:
        for kw in intent.keywords:
            should.append({
                "bool": {
                    "should": [
                        {"match_phrase": {"brief_title": {"query": kw, "boost": _exact_boost}}},
                        {"match_phrase": {"official_title": {"query": kw, "boost": _exact_boost}}},
                        {"match_phrase": {"condition_names.text": {"query": kw, "boost": _exact_boost}}},
                        {"match": {"brief_title": {"query": kw, **_fuzzy, "boost": _fuzzy_boost}}},
                        {"match": {"official_title": {"query": kw, **_fuzzy, "boost": _fuzzy_boost}}},
                        {"match": {"brief_summaries_description": {"query": kw, **_fuzzy, "boost": _fuzzy_boost}}},
                        {"match": {"condition_names.text": {"query": kw, **_fuzzy, "boost": _fuzzy_boost}}},
                    ],
                    "minimum_should_match": 1,
                }
            })
    elif intent.keywords and intent.title_contains:
        for kw in intent.keywords:
            should.append({
                "bool": {
                    "should": [
                        {"multi_match": {
                            "query": kw,
                            "fields": ["brief_title^2", "official_title^2", "brief_summaries_description", "condition_names.text^2"],
                            "type": "phrase",
                            "boost": _exact_boost,
                        }},
                        {"multi_match": {
                            "query": kw,
                            "fields": ["brief_title", "official_title", "brief_summaries_description", "condition_names.text"],
                            "type": "best_fields",
                            **_fuzzy,
                            "boost": _fuzzy_boost,
                        }},
                    ],
                    "minimum_should_match": 1,
                }
            })
    if intent.enrollment_min is not None:
        filter_clauses.append({"range": {"enrollment": {"gte": intent.enrollment_min}}})

    if not filter_clauses and not must and not should:
        body = {"query": {"match_all": {}}, "track_total_hits": True}
    else:
        bool_query: dict = {
            "must": must if must else [{"match_all": {}}],
            "filter": filter_clauses,
        }
        if should:
            bool_query["should"] = should
        body = {
            "query": {"bool": bool_query},
            "track_total_hits": True,
        }
    return body


def search(
    es: Elasticsearch,
    intent: SearchIntent,
    *,
    index: str = INDEX_NAME,
    from_: int = 0,
    size: int = 10,
) -> tuple[list[dict], int]:
    query_body = build_query(intent)
    query_body["from"] = from_
    query_body["size"] = size
    query_body["sort"] = [{"_score": {"order": "desc"}}, {"completion_date": {"order": "desc", "missing": "_last"}}]
    query_body["_source"] = [
        "nct_id", "brief_title", "official_title", "overall_status", "phase",
        "condition_names", "sponsor_names", "enrollment", "completion_date",
    ]

    resp = es.search(index=index, body=query_body)
    hits = resp["hits"]["hits"]
    total = resp["hits"]["total"]
    total_value = total["value"] if isinstance(total, dict) else total
    return hits, total_value