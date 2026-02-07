import json
from typing import Any

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


def _trial_to_dict(hit: Any, max_desc_len: int = 250) -> dict[str, Any]:
    desc = getattr(hit, "brief_summaries_description", None) or ""
    if len(desc) > max_desc_len:
        desc = desc[: max_desc_len - 3] + "..."
    return {
        "nct_id": getattr(hit, "nct_id", None),
        "brief_title": getattr(hit, "brief_title", None),
        "phase": getattr(hit, "phase", None),
        "overall_status": getattr(hit, "overall_status", None),
        "condition_names": getattr(hit, "condition_names", None) or [],
        "enrollment": getattr(hit, "enrollment", None),
        "brief_summary": desc,
        "relevance_score": getattr(hit, "score", None),
    }


def _build_context_json(
    user_query: str,
    interpretation: dict[str, Any],
    trials: list[Any],
    total: int,
    page: int,
    size: int,
    max_trials_in_context: int = 8,
) -> str:
    showing_from = (page - 1) * size + 1 if total > 0 else 0
    showing_to = min((page - 1) * size + len(trials),
                     total) if total > 0 else 0

    payload = {
        "user_query": user_query,
        "interpretation": {
            "phase": interpretation.get("phase"),
            "condition": interpretation.get("condition"),
            "status": interpretation.get("status"),
            "keywords": interpretation.get("keywords") or [],
            "title_contains": interpretation.get("title_contains"),
            "enrollment_min": interpretation.get("enrollment_min"),
            "location": interpretation.get("location"),
        },
        "pagination": {
            "total_matching_trials": total,
            "page": page,
            "page_size": size,
            "showing_trials": f"{showing_from}-{showing_to}" if total > 0 else "0",
        },
        "results_on_this_page": [_trial_to_dict(t) for t in trials[:max_trials_in_context]],
    }
    return json.dumps(payload, indent=2, default=str)


SYSTEM_PROMPT = """You are a clinical trials search assistant. You receive a JSON object with:
- user_query: the exact search the user ran
- interpretation: filters applied (phase, condition, status, keywords, title_contains, enrollment_min, location); null means that filter was not used
- pagination: total_matching_trials, page, page_size, showing_trials (range)
- results_on_this_page: array of trial objects (nct_id, brief_title, phase, overall_status, condition_names, enrollment, brief_summary, relevance_score)

Rules:
- Use ONLY the information in the JSON. Do not invent trials or details.
- Cover all cases below in your logic; output 2-5 clear, factual sentences.

Cases to handle:
1. total_matching_trials === 0: State that no trials were found. Mention which filters were applied (e.g. phase, condition, keywords). Suggest broadening the search (e.g. try another phase, remove a keyword, or check spelling).
2. total_matching_trials === 1: Say one trial was found; briefly state what it is (phase, condition, title) and that it matches the user's criteria.
3. total_matching_trials > 1: Summarize how many trials match. Mention the main filters that were applied (phase, condition, status, keywords, title_contains, enrollment_min, location — only the non-null ones). Highlight main themes from the results (e.g. conditions, phases, types of interventions). If keywords/genes were requested, note whether the top results mention them.
4. When interpretation.phase is set: mention the phase (e.g. Phase 2).
5. When interpretation.condition is set: mention the condition/disease.
6. When interpretation.keywords is non-empty: mention the genes/keywords and whether results are about them.
7. When interpretation.title_contains is set: mention that the search required title/summary to contain that text.
8. When interpretation.enrollment_min is set: mention "large trials" or "trials with at least N participants".
9. When interpretation.location is set: mention "trials in [location]".
10. When interpretation.status is set: mention recruitment status (e.g. recruiting, completed).

Output only the summary text, no preamble or JSON."""


def generate_summary(
    user_query: str,
    trials: list[Any],
    total: int,
    interpretation: dict[str, Any] | None = None,
    page: int = 1,
    size: int = 10,
    *,
    max_trials_in_context: int = 8,
) -> str | None:
    if not OPENAI_API_KEY:
        return None

    interpretation = interpretation or {}
    context_json = _build_context_json(
        user_query, interpretation, trials, total, page, size, max_trials_in_context
    )

    user_content = f"""Use the following JSON (search context and results) to write a short summary for the user. Apply all rules from your instructions.

{context_json}"""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY,
                        base_url=OPENAI_BASE_URL or None)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            max_tokens=320,
            temperature=0.2,
        )
        choice = resp.choices[0] if resp.choices else None
        if choice and choice.message and choice.message.content:
            return choice.message.content.strip()
    except Exception:
        pass
    return None


def correct_query_spelling(user_query: str) -> str:
    q = user_query.strip()
    if not q or not OPENAI_API_KEY:
        return q

    prompt = f"""You are a spell-checker for clinical trial search queries. Fix any spelling mistakes in the user's query by replacing misspelled words with the most likely intended word (especially for medical terms, conditions, phases, gene names, etc.). Preserve the meaning and structure of the query.

Rules:
- Output ONLY the corrected query, nothing else: no explanation, no "Corrected query:", no quotes.
- If the query has no spelling errors, output it unchanged.
- Keep phase phrases like "Phase 2", "Phase 3", status like "recruiting", condition names, gene names (e.g. BRCA1), and numbers as-is or correctly spelled.
- Preserve natural language; do not add or remove words except to fix spelling.

User query:
{q}"""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL or None)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=min(256, len(q) + 100),
            temperature=0.0,
        )
        choice = resp.choices[0] if resp.choices else None
        if choice and choice.message and choice.message.content:
            corrected = choice.message.content.strip().strip('"').strip("'")
            if corrected:
                return corrected
    except Exception:
        pass
    return q


def generate_thinking_message(user_query: str) -> str:
    """
    Generate a short "thinking" sentence from the user's search query for display while search runs.
    Returns a fallback string if LLM is not configured or the call fails.
    """
    fallback = "Searching clinical trials…"
    if not OPENAI_API_KEY or not user_query.strip():
        return fallback

    prompt = f"""The user just entered this clinical trial search: "{user_query.strip()}"

In one short sentence (under 15 words), say what you're looking for in a friendly, natural way. Examples:
- "Looking for Phase 2 Breast Cancer trials related to BRCA1."
- "Searching for recruiting Alzheimer's disease trials."
- "Finding large trials in the United States."
Reply with only that one sentence, no quotes or preamble."""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL or None)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.3,
        )
        choice = resp.choices[0] if resp.choices else None
        if choice and choice.message and choice.message.content:
            text = choice.message.content.strip().strip('"')
            if text:
                return text
    except Exception:
        pass
    return fallback