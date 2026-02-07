from fastapi import APIRouter, HTTPException, Path, Query

from config import ES_HOST, INDEX_NAME
from elasticsearch import Elasticsearch

from api.schemas import SearchInterpretation, SearchResponse, TrialDetail, TrialHit
from rag import correct_query_spelling, generate_summary, generate_thinking_message
from search.parser import parse_search_query
from search.es_query import search

router = APIRouter(tags=["search"])

_es: Elasticsearch | None = None


def get_es() -> Elasticsearch:
    global _es
    if _es is None:
        _es = Elasticsearch(ES_HOST)
    return _es


def _do_search(q: str, page: int, size: int) -> SearchResponse:
    es = get_es()
    if not es.ping():
        raise HTTPException(status_code=503, detail="Search service unavailable (Elasticsearch not connected)")
    q = correct_query_spelling(q)
    intent = parse_search_query(q)
    from_ = (page - 1) * size
    hits, total = search(es, intent, index=INDEX_NAME, from_=from_, size=size)
    interpretation = SearchInterpretation(**intent.to_interpretation_dict())
    results = [TrialHit.from_es_hit(h) for h in hits]
    interpretation_dict = intent.to_interpretation_dict()
    summary = generate_summary(
        q, results, total,
        interpretation=interpretation_dict,
        page=page,
        size=size,
    )
    return SearchResponse(
        interpretation=interpretation,
        results=results,
        total=total,
        page=page,
        size=size,
        summary=summary,
    )


@router.get(
    "/trial/{nct_id}",
    response_model=TrialDetail,
    summary="Trial details",
    description="Fetch full details for a single trial by NCT ID.",
)
def get_trial(nct_id: str = Path(..., description="NCT ID (e.g. NCT00001234)")) -> TrialDetail:
    es = get_es()
    if not es.ping():
        raise HTTPException(status_code=503, detail="Search service unavailable (Elasticsearch not connected)")
    resp = es.search(
        index=INDEX_NAME,
        body={"query": {"term": {"nct_id": nct_id}}, "size": 1},
    )
    hits = resp["hits"]["hits"]
    if not hits:
        raise HTTPException(status_code=404, detail=f"Trial {nct_id} not found")
    src = hits[0].get("_source") or {}
    return TrialDetail.from_es_source(src, score=hits[0].get("_score"))


@router.get(
    "/search/thinking/{query:path}",
    summary="Thinking message",
    description="Returns a short LLM-generated 'thinking' sentence for the given query (for display while search runs).",
)
def search_thinking(
    query: str = Path(..., description="Natural language query"),
) -> dict[str, str]:
    return {"thinking": generate_thinking_message(query.strip())}


@router.get(
    "/search/{query:path}",
    response_model=SearchResponse,
    summary="Search",
    description="Natural language search. GET /search/<natural language query>. Returns paginated trials. Optional: ?page=1&size=10",
)
def search_trials(
    query: str = Path(..., description="Natural language query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=10, description="Results per page (max 10)"),
) -> SearchResponse:
    return _do_search(query.strip(), page, size)