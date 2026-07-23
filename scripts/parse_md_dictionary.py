"""Seed the dictionary store from the curated Markdown dictionary.

Thin CLI wrapper over ingestion.md_parser (the canonical parser also used
by the full ingestion pipeline) so there is a single source of truth for
how Libyan terms, their fusha meaning, and English equivalents are parsed.
"""
import io
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from dictionary_store import dictionary_store
from ingestion.md_parser import parse_markdown


if __name__ == "__main__":
    md_path = Path(__file__).resolve().parent.parent / "قاموس_مصطلحات_صيانة_السيارات_الليبية.md"
    terms = parse_markdown(str(md_path))
    print(f"Total term variants extracted: {len(terms)}")
    for t in terms[:5]:
        print(f"  {t['arabic_term']} -> {t['fusha_meaning']} / {t['source_term']}")

    result = dictionary_store.seed_or_update_terms(terms)
    print(f"\nAdded {result['added']} new terms, updated {result['updated']} existing terms")
    print(f"Total terms in store: {dictionary_store.count}")
