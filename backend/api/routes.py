from fastapi import APIRouter, HTTPException, Path, Query

from config import ES_HOST, INDEX_NAME
from elasticsearch import Elasticsearch

from api.schemas import SearchInterpretation, SearchResponse, TrialHit
from rag import generate_summary
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
    "/search/{query:path}",
    response_model=SearchResponse,
    summary="Search",
    description="Natural language search. GET /search/<natural language query>. Returns paginated trials. Optional: ?page=1&size=10",
)
def search_trials(
    query: str = Path(..., description="Natural language query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Results per page"),
) -> SearchResponse:
    return _do_search(query.strip(), page, size)