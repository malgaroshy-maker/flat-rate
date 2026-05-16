"""Dictionary store — persistent term mappings with JSON file storage."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

STORAGE_DIR = Path(__file__).resolve().parent / "data"
STORAGE_FILE = STORAGE_DIR / "dictionary.json"


class DictionaryStore:
    def __init__(self) -> None:
        self._terms: dict[str, dict] = {}
        self._pending: dict[str, dict] = {}
        self._lock = Lock()
        self._load()

    def _load(self) -> None:
        if not STORAGE_FILE.exists():
            return
        try:
            with open(STORAGE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            self._terms = data.get("terms", {})
            self._pending = data.get("pending", {})
        except Exception:
            pass

    def _save(self) -> None:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with self._lock:
                with open(STORAGE_FILE, "w", encoding="utf-8") as f:
                    json.dump({"terms": self._terms, "pending": self._pending}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def seed_terms(self, entries: list[dict]) -> int:
        added = 0
        for entry in entries:
            arabic = entry.get("arabic_term", "").strip()
            if not arabic or self._find_by_arabic(arabic):
                continue
            category = entry.get("standard_category") or entry.get("category", "General")
            english = entry.get("english_term") or entry.get("source_term", "")
            self._add_internal(arabic, category, english)
            added += 1
        if added:
            self._save()
        return added

    def _find_by_arabic(self, arabic: str) -> Optional[dict]:
        term = arabic.strip().lower()
        for t in self._terms.values():
            if t["arabic_term"].strip().lower() == term:
                return t
        return None

    def _add_internal(self, arabic_term: str, standard_category: str, english_term: str = "") -> str:
        term_id = str(uuid.uuid4())[:8]
        self._terms[term_id] = {
            "id": term_id,
            "arabic_term": arabic_term.strip(),
            "standard_category": standard_category.strip(),
            "english_term": english_term.strip(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return term_id

    def add_term(self, arabic_term: str, standard_category: str, english_term: str = "") -> str:
        term_id = self._add_internal(arabic_term, standard_category, english_term)
        self._save()
        return term_id

    def update_term(self, term_id: str, arabic_term: Optional[str] = None,
                    standard_category: Optional[str] = None, english_term: Optional[str] = None) -> bool:
        if term_id not in self._terms:
            return False
        if arabic_term is not None:
            self._terms[term_id]["arabic_term"] = arabic_term.strip()
        if standard_category is not None:
            self._terms[term_id]["standard_category"] = standard_category.strip()
        if english_term is not None:
            self._terms[term_id]["english_term"] = english_term.strip()
        self._terms[term_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return True

    def delete_term(self, term_id: str) -> bool:
        if term_id not in self._terms:
            return False
        del self._terms[term_id]
        self._save()
        return True

    def get_term(self, term_id: str) -> Optional[dict]:
        return self._terms.get(term_id)

    def list_terms(self, search: Optional[str] = None, category: Optional[str] = None) -> list[dict]:
        results = list(self._terms.values())
        if search:
            s = search.lower()
            results = [t for t in results if
                       s in t.get("arabic_term", "").lower()
                       or s in t.get("english_term", "").lower()
                       or s in t.get("standard_category", "").lower()]
        if category:
            results = [t for t in results if t.get("standard_category") == category]
        return sorted(results, key=lambda t: t.get("arabic_term", ""))

    def add_pending(self, term_text: str, query_text: str) -> str:
        pending_id = str(uuid.uuid4())[:8]
        self._pending[pending_id] = {
            "id": pending_id,
            "term_text": term_text.strip(),
            "query_text": query_text.strip(),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save()
        return pending_id

    def list_pending(self) -> list[dict]:
        return [p for p in self._pending.values() if p.get("status") == "pending"]

    def resolve_pending(self, pending_id: str, arabic_term: str,
                        standard_category: str, english_term: str = "") -> Optional[str]:
        entry = self._pending.get(pending_id)
        if not entry:
            return None
        term_id = self.add_term(arabic_term, standard_category, english_term)
        entry["status"] = "resolved"
        entry["resolved_term_id"] = term_id
        self._save()
        return term_id

    @property
    def count(self) -> int:
        return len(self._terms)

    @property
    def pending_count(self) -> int:
        return len(self.list_pending())


dictionary_store = DictionaryStore()
