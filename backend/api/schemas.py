from pydantic import BaseModel, Field


class SearchInterpretation(BaseModel):
    phase: str | None = Field(None, description="Trial phase: PHASE1, PHASE2, PHASE3, PHASE4")
    condition: str | None = Field(None, description="Condition/disease, e.g. Breast Cancer")
    status: str | None = Field(None, description="Overall status, e.g. RECRUITING")
    keywords: list[str] = Field(default_factory=list, description="Keywords/genes, e.g. BRCA1")
    title_contains: str | None = None
    enrollment_min: int | None = None
    location: str | None = None


class TrialHit(BaseModel):
    nct_id: str | None = None
    brief_title: str | None = None
    official_title: str | None = None
    overall_status: str | None = None
    phase: str | None = None
    condition_names: list[str] = Field(default_factory=list)
    sponsor_names: list[str] = Field(default_factory=list)
    enrollment: int | None = None
    completion_date: str | None = None
    score: float | None = Field(None, description="Elasticsearch relevance score")

    @classmethod
    def from_es_hit(cls, hit: dict) -> "TrialHit":
        src = hit.get("_source") or {}
        return cls(
            nct_id=src.get("nct_id"),
            brief_title=src.get("brief_title"),
            official_title=src.get("official_title"),
            overall_status=src.get("overall_status"),
            phase=src.get("phase"),
            condition_names=src.get("condition_names") or [],
            sponsor_names=src.get("sponsor_names") or [],
            enrollment=src.get("enrollment"),
            completion_date=src.get("completion_date"),
            score=hit.get("_score"),
        )


class SearchResponse(BaseModel):
    interpretation: SearchInterpretation = Field(description="Extracted intent/entities")
    results: list[TrialHit] = Field(default_factory=list, description="Trials for this page")
    total: int = Field(description="Total hits (all pages)")
    page: int = Field(ge=1, description="Current page")
    size: int = Field(ge=1, le=100, description="Page size")
    summary: str | None = Field(
        None,
        description="RAG-generated natural language summary of results (null if LLM not configured or no results).",
    )