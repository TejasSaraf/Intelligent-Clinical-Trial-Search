import re
from dataclasses import dataclass, field
from typing import Any

PHASE_VALUES = {"PHASE1", "PHASE2", "PHASE3",
                "PHASE4", "NA", "EARLY_PHASE1", "NOT_APPLICABLE"}

STATUS_VALUES = {
    "RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING",
    "COMPLETED", "SUSPENDED", "TERMINATED", "WITHDRAWN", "UNKNOWN",
}

STATUS_SYNONYMS = {
    "open": "RECRUITING", "recruiting": "RECRUITING", "active": "RECRUITING",
    "ongoing": "RECRUITING", "completed": "COMPLETED", "closed": "COMPLETED",
}


@dataclass
class SearchIntent:
    phase: str | None = None
    condition: str | None = None
    overall_status: str | None = None
    keywords: list[str] = field(default_factory=list)
    title_contains: str | None = None
    enrollment_min: int | None = None
    facility_country: str | None = None
    raw_query: str = ""

    def to_interpretation_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.phase:
            d["phase"] = self.phase
        if self.condition:
            d["condition"] = self.condition
        if self.overall_status:
            d["status"] = self.overall_status
        if self.keywords:
            d["keywords"] = self.keywords
        if self.title_contains:
            d["title_contains"] = self.title_contains
        if self.enrollment_min is not None:
            d["enrollment_min"] = self.enrollment_min
        if self.facility_country:
            d["location"] = self.facility_country
        return d


def _normalize_status(s: str) -> str | None:
    s = s.strip().lower()
    if s.upper() in STATUS_VALUES:
        return s.upper()
    return STATUS_SYNONYMS.get(s)


CONDITION_SYNONYMS = {
    "alzheimer's": "Alzheimer Disease",
    "alzheimers": "Alzheimer Disease",
    "alzheimer's disease": "Alzheimer Disease",
    "alzheimers disease": "Alzheimer Disease",
    "alzheimer": "Alzheimer Disease",
    "alzemer": "Alzheimer Disease",
    "alzhemer": "Alzheimer Disease",
    "alzimer": "Alzheimer Disease",
}


def _normalize_condition(condition: str) -> str:
    s = condition.strip().replace("\u2019", "'").replace("\u2018", "'")
    return CONDITION_SYNONYMS.get(s.lower(), s)


def _intent_from_llm_extraction(d: dict, raw_query: str) -> SearchIntent:
    """Build SearchIntent from LLM extraction dict."""
    intent = SearchIntent(raw_query=raw_query)
    intent.phase = d.get("phase") if isinstance(d.get("phase"), str) else None
    intent.condition = _normalize_condition(d["condition"]) if d.get("condition") else None
    intent.overall_status = d.get("status") if isinstance(d.get("status"), str) else None
    loc = d.get("location")
    if loc:
        loc_lower = str(loc).lower()
        if "united states" in loc_lower or "usa" in loc_lower or loc_lower == "us":
            intent.facility_country = "United States"
        else:
            intent.facility_country = str(loc).strip()
    kw = d.get("keywords")
    intent.keywords = [str(k).strip() for k in (kw or [])] if isinstance(kw, list) else []
    intent.enrollment_min = d.get("enrollment_min") if isinstance(d.get("enrollment_min"), (int, float)) else None
    intent.title_contains = d.get("title_contains") if isinstance(d.get("title_contains"), str) and d.get("title_contains") else None
    if intent.title_contains and not intent.keywords and intent.condition:
        pass
    elif intent.keywords and not intent.title_contains and not intent.condition:
        intent.title_contains = intent.keywords[0] if intent.keywords else None
    return intent


def parse_search_query(query: str, llm_extraction: dict | None = None) -> SearchIntent:
    if not query or not query.strip():
        return SearchIntent(raw_query=query or "")

    q = query.strip()

    if llm_extraction:
        intent = _intent_from_llm_extraction(llm_extraction, q)
        if intent.phase or intent.condition or intent.overall_status or intent.facility_country or intent.keywords:
            return intent

    intent = SearchIntent(raw_query=q)
    q_lower = q.lower()

    phase_match = re.search(
        r"\bphase\s*(\d|one|two|three|four|1|2|3|4)\b",
        q_lower, re.IGNORECASE
    )
    if phase_match:
        g = phase_match.group(1).lower()
        mapping = {"1": "PHASE1", "one": "PHASE1", "2": "PHASE2", "two": "PHASE2",
                   "3": "PHASE3", "three": "PHASE3", "4": "PHASE4", "four": "PHASE4"}
        intent.phase = mapping.get(
            g, "PHASE" + g.upper() if g.isdigit() else None)

    for word in ("recruiting", "open", "ongoing", "active", "completed", "closed"):
        if re.search(rf"\b{word}\b", q_lower):
            intent.overall_status = _normalize_status(word)
            break

    if re.search(r"\b(large|big)\s*(trials?|studies?)\b", q_lower) or re.search(r"\btrials?\s*(with|of)\s*(\d+)\+?\s*(participants?|enrollment)", q_lower):
        intent.enrollment_min = 500
    enroll_match = re.search(
        r"\benrollment\s*(?:>|over|at least)\s*(\d+)", q_lower)
    if enroll_match:
        intent.enrollment_min = int(enroll_match.group(1))

    usa_patterns = [
        r"\b(?:in\s+)?(?:the\s+)?(?:USA|U\.?S\.?A\.?|United States|US)\b",
        r"\b(?:trials?\s+)?(?:in|from)\s+(.+?)(?:\s+for\s+|\s+about\s+|$)",
    ]
    for pat in usa_patterns:
        m = re.search(pat, q, re.IGNORECASE)
        if m:
            loc = m.group(1).strip(
            ) if m.lastindex and m.lastindex >= 1 else "United States"
            if "usa" in loc.lower() or "united states" in loc.lower() or "u.s" in loc.lower():
                intent.facility_country = "United States"
                break
            if len(loc) < 50:
                intent.facility_country = loc
            break

    for_pattern = re.search(
        r"(?:trials?\s+)?(?:for|about|related to)\s+([^,.]+?)(?:\s+associated with|\s+with\s+\w+|\s*$|,)",
        q, re.IGNORECASE
    )
    if for_pattern:
        condition = for_pattern.group(1).strip()
        condition = re.sub(r"\s+trials?\s*$", "",
                           condition, flags=re.IGNORECASE)
        if condition and len(condition) < 100:
            intent.condition = _normalize_condition(condition)

    assoc = re.search(
        r"(?:associated with|with|containing|including)\s+([A-Za-z0-9\-]+)(?:\s+gene)?\b",
        q, re.IGNORECASE
    )
    if assoc:
        kw = assoc.group(1).strip()
        if kw.upper() not in ("TRIALS", "STUDIES", "THE", "A", "AN"):
            intent.keywords.append(kw)

    title_match = re.search(
        r"title\s+contains?\s+['\"]?([^'\"]+)['\"]?", q, re.IGNORECASE)
    if title_match:
        intent.title_contains = title_match.group(1).strip()
    elif intent.keywords and not intent.condition:
        intent.title_contains = intent.keywords[0]

    return intent