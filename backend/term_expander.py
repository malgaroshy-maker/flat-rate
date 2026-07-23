"""Expand Libyan-dialect terms in a user query with their fusha/English
equivalents before embedding, so dialect queries retrieve as well as
queries phrased in standard Arabic (the historical POS descriptions were
normalized toward fusha during ingestion — see ingestion/normalizer.py).
"""

from __future__ import annotations

import re
import unicodedata

from dictionary_store import dictionary_store

_TASHKEEL = re.compile(r"[ً-ٰٟ]")


def normalize_arabic(text: str) -> str:
    """Strip diacritics and unify common letter variants for matching."""
    text = unicodedata.normalize("NFKC", text)
    text = _TASHKEEL.sub("", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي").replace("ة", "ه")
    return text


def find_matched_terms(query: str) -> list[dict]:
    """Return dictionary entries whose arabic_term appears in the query,
    longest terms first so multi-word terms win over single-word substrings.
    """
    normalized_query = normalize_arabic(query.lower())
    candidates = dictionary_store.list_terms()
    matched: list[dict] = []
    for term in candidates:
        arabic = term.get("arabic_term", "").strip()
        if not arabic or len(arabic) < 2:
            continue
        if normalize_arabic(arabic.lower()) in normalized_query:
            matched.append(term)
    matched.sort(key=lambda t: len(t.get("arabic_term", "")), reverse=True)
    return matched


def expand_query(query: str) -> tuple[str, list[dict]]:
    """Return (expanded_query_for_embedding, matched_dictionary_terms).

    The expansion appends the fusha meaning and English equivalent of each
    matched dialect term so the embedding model — which was trained mostly
    on fusha/English text and whose historical corpus was fusha-normalized
    — can match dialect queries against fusha-phrased records.
    """
    matched = find_matched_terms(query)
    if not matched:
        return query, []

    additions = []
    seen_arabic = set()
    for term in matched:
        arabic = term["arabic_term"]
        if arabic in seen_arabic:
            continue
        seen_arabic.add(arabic)
        fusha = term.get("fusha_meaning", "")
        english = term.get("english_term", "")
        parts = [p for p in (fusha, english) if p]
        if parts:
            additions.append(f"{arabic} ({' / '.join(parts)})")

    if not additions:
        return query, matched

    expanded = query + " | " + " | ".join(additions)
    return expanded, matched
