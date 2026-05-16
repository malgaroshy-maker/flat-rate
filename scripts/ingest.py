"""
Data ingestion script — parse POS Excel(s) + automotive dictionary -> ChromaDB.
Usage: python scripts/ingest.py --input "../تقرير اليد العاملة بالكامل.xlsx" [--input2 "../اليد العاملة منذ فتح المركز.xlsx"] --dictionary "...docx"
"""

import argparse
import io
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from ingestion.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest POS labor data into ChromaDB")
    parser.add_argument("--input", type=str, required=True, help="Path to primary XLSX file")
    parser.add_argument("--input2", type=str, default=None, help="Path to secondary XLSX file (merged, deduplicated)")
    parser.add_argument("--dictionary", type=str, default=None, help="Path to DOCX dictionary (optional)")
    parser.add_argument("--reset", action="store_true", help="Reset ChromaDB collection before ingest")

    args = parser.parse_args()

    xlsx_paths = [args.input]
    if args.input2:
        xlsx_paths.append(args.input2)

    result = run_pipeline(
        xlsx_paths=xlsx_paths,
        docx_path=args.dictionary,
        reset=args.reset,
    )
    print(f"\nIngestion complete: {result}")


if __name__ == "__main__":
    main()
