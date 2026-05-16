"""Normalize Arabic labor descriptions using the dictionary."""

import re
from typing import Optional


class Normalizer:
    def __init__(self, dictionary: list[dict[str, str]]):
        self.dictionary = dictionary
        self._arabic_to_category: dict[str, str] = {}
        self._term_index: dict[str, dict[str, str]] = {}
        self._build_index()

    def _build_index(self) -> None:
        for entry in self.dictionary:
            arabic = entry["arabic_term"].strip()
            category = entry["category"]
            if arabic:
                self._arabic_to_category[arabic] = category
                self._term_index[arabic.lower()] = entry

    def find_terms_in_text(self, text: str) -> list[dict[str, str]]:
        """Find known dictionary terms in the given Arabic text."""
        found: list[dict[str, str]] = []
        text_lower = text.lower()
        for arabic_term, entry in self._term_index.items():
            if arabic_term.lower() in text_lower:
                found.append(entry)
        return found

    def get_dominant_category(self, text: str) -> str:
        """Return the most likely standard category for a description."""
        found = self.find_terms_in_text(text)
        if not found:
            return "General"
        categories = [t["category"] for t in found]
        return max(set(categories), key=categories.count)

    def normalize_description(self, text: str) -> str:
        """Produce a normalized version of the description for embedding.

        Joins known terms with their categories to improve embedding quality.
        """
        terms = self.find_terms_in_text(text)
        if not terms:
            return text

        unique_terms = {t["source_term"]: t for t in terms}
        normalized_parts = [text]
        for term in unique_terms.values():
            normalized_parts.append(f"[{term['category']}] {term['source_term']}")
        return " | ".join(normalized_parts)

    @property
    def known_arabic_terms(self) -> set[str]:
        return set(self._arabic_to_category.keys())

    def is_known(self, arabic_term: str) -> bool:
        return arabic_term.strip().lower() in self._term_index
