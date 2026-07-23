"""Parse Libyan automotive terms from Markdown dictionary file."""
from __future__ import annotations

import re
from pathlib import Path


# Category mapping from section headers
CATEGORY_MAP = {
    "عامة": "General",
    "إدارية": "General",
    "سمكرة": "Body & Paint",
    "طلاء": "Body & Paint",
    "الهيكل الخارجي": "Body & Paint",
    "هيكل": "Body & Paint",
    "مقصورة": "Interior",
    "المحرك": "Engine",
    "نقل الحركة": "Transmission",
    "كمبيو": "Transmission",
    "فرامل": "Brakes",
    "تعليق": "Suspension",
    "التوجيه": "Steering",
    "تبريد": "Cooling",
    "تكييف": "A/C",
    "كهرباء": "Electrical",
    "إلكترونيات": "Electrical",
    "عادم": "Exhaust",
    "وقود": "Fuel",
}


def _detect_category(section_title: str) -> str:
    section_lower = section_title.lower()
    for keyword, category in CATEGORY_MAP.items():
        if keyword in section_lower:
            return category
    return "General"


def parse_markdown(md_path: str | Path) -> list[dict]:
    """Parse a Markdown dictionary file and return term entries."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    terms: list[dict] = []
    current_category = "General"
    in_table = False
    headers: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Detect section headers (## N. Title)
        section_match = re.match(r"^##\s+\d+[\.\u2013-]\s+(.+)", stripped)
        if section_match:
            current_category = _detect_category(section_match.group(1))

        # Detect markdown table separator row
        if re.match(r"^\|[-:| ]+\|[-:| ]+\|[-:| ]+\|$", stripped):
            in_table = True
            continue

        if not stripped.startswith("|"):
            in_table = False
            continue

        if not in_table:
            continue

        # Parse table row
        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if len(cells) < 3:
            continue

        libyan = cells[0]
        arabic_meaning = cells[1]
        english = cells[2]

        # Skip header row
        if libyan in ("المصطلح الليبي", "Libyan Term", "المصطلح", "---"):
            continue

        if not libyan or len(libyan) < 2:
            continue

        # Skip pure English rows (not Arabic slang)
        if re.match(r"^[a-zA-Z\s/-]+$", libyan):
            continue

        # Flag context-dependent terms (e.g. ديسكو = wheel disc / brake disc /
        # clutch disc depending on context) so the query-time expander and the
        # LLM know not to treat the meaning as fixed.
        notes = ""
        if "حسب السياق" in arabic_meaning or "context-dependent" in english.lower():
            notes = "context-dependent — meaning varies by surrounding text"

        # Clean up English term: take first part before parentheses
        english_main = re.sub(r"\s*\(.*?\)\s*", "", english).strip()
        # Remove trailing period
        english_main = english_main.rstrip(".")

        # The Libyan term column sometimes lists variants separated by " / "
        # (e.g. "براونطي / برونطي / براولطي"). Emit one entry per variant so
        # each spelling is independently matchable at query time.
        variants = [v.strip() for v in libyan.split("/") if v.strip()]

        for variant in variants:
            terms.append({
                "source_term": english_main,
                "italian_term": "",
                "arabic_term": variant,
                "fusha_meaning": arabic_meaning.strip(),
                "category": current_category,
                "notes": notes,
            })

    return terms
