"""Extract Italian→Arabic term mappings from the Libyan Automotive Dictionary."""

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Category pattern: "N. ShortName ( Arabic )" — name must be < 8 words
CATEGORY_RE = re.compile(
    r"(\d+)[\.\-]\s+(.{4,60}?)\s*\(\s*([\u0600-\u06FF][\u0600-\u06FF\s]{1,40})\s*\)"
)

# Term pattern: "English / Alternate : Italian ( Arabic )"
TERM_RE = re.compile(
    r"([A-Za-z][A-Za-z\s/\-']+?)\s*:\s*"
    r"([A-Za-z\u0219\u021B\s/'\-]+?)\s*"
    r"\(\s*([\u0600-\u06FF\u0640-\u065F\s/'\-]+?)\s*\)"
)


def _extract_text(docx_path: str | Path) -> str:
    with zipfile.ZipFile(docx_path) as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            parts: list[str] = []
            for t in root.iter(f"{{{NS}}}t"):
                if t.text:
                    parts.append(t.text)
    return " ".join(parts)


def _normalize_text(text: str) -> str:
    """Collapse multiple spaces and normalize."""
    return re.sub(r"\s{2,}", " ", text).strip()


def _is_valid_category(name: str) -> bool:
    """Category names are short, not intro sentences."""
    words = name.split()
    return 1 <= len(words) <= 8


def _parse_terms(raw_text: str) -> list[dict[str, str]]:
    terms: list[dict[str, str]] = []
    current_category = "General"

    # Find categories
    categories: list[tuple[int, str]] = []
    for m in CATEGORY_RE.finditer(raw_text):
        cat_en = _normalize_text(m.group(2))
        cat_ar = _normalize_text(m.group(3))
        if _is_valid_category(cat_en) and len(cat_ar) >= 2:
            categories.append((m.start(), cat_en))

    # Find terms with positions
    for m in TERM_RE.finditer(raw_text):
        english_term = _normalize_text(m.group(1))
        italian_term = _normalize_text(m.group(2))
        arabic_term = _normalize_text(m.group(3))

        if len(arabic_term) < 2:
            continue
        if len(english_term) < 3:
            continue

        # Find last category before this term
        for cat_start, cat_name in categories:
            if cat_start < m.start():
                current_category = cat_name

        terms.append(
            {
                "source_term": english_term,
                "italian_term": italian_term,
                "arabic_term": arabic_term,
                "category": current_category,
            }
        )

    return terms


def parse_dictionary(docx_path: str | Path) -> list[dict[str, str]]:
    raw_text = _extract_text(docx_path)
    return _parse_terms(raw_text)
