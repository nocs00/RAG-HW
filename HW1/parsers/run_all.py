"""Orchestrator: parse all raw files and write a single JSONL knowledge base."""

import json
import sys
from pathlib import Path

# Allow running directly from the parsers/ directory
sys.path.insert(0, str(Path(__file__).parent))

from parse_txt import parse_txt
from parse_md import parse_md
from parse_csv import parse_csv
from parse_pdf import parse_pdf
from parse_mhtml import parse_mhtml

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
OUT_DIR = Path(__file__).parent.parent / "data" / "normalized"

PARSERS = {
    ".txt": parse_txt,
    ".md": parse_md,
    ".csv": parse_csv,
    ".pdf": parse_pdf,
    ".mhtml": parse_mhtml,
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / "knowledge_base.jsonl"

    all_records: list[dict] = []

    for filepath in sorted(RAW_DIR.iterdir()):
        ext = filepath.suffix.lower()
        parser = PARSERS.get(ext)
        if parser is None:
            print(f"  skip  {filepath.name}  (no parser for '{ext}')")
            continue
        print(f"  parse {filepath.name} ...", end=" ", flush=True)
        try:
            records = parser(filepath)
            all_records.extend(records)
            print(f"{len(records)} records")
        except Exception as exc:
            print(f"ERROR — {exc}")

    with open(out_file, "w", encoding="utf-8") as f:
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nDone: {len(all_records)} total records -> {out_file}")


if __name__ == "__main__":
    main()
