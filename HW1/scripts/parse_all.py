"""Orchestrator: parse all raw files and write a single JSONL knowledge base."""

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "parsers"))

from parse_txt import parse_txt
from parse_md import parse_md
from parse_csv import parse_csv
from parse_pdf import parse_pdf
from parse_mhtml import parse_mhtml

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
OUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUT_FILE = OUT_DIR / "knowledge_base.jsonl"

PARSERS = {
    ".txt":   parse_txt,
    ".md":    parse_md,
    ".csv":   parse_csv,
    ".pdf":   parse_pdf,
    ".mhtml": parse_mhtml,
}


def run_parsing(verbose: bool = True) -> dict:
    """Parse all raw files and write knowledge_base.jsonl.

    Returns a stats dict with counts broken down by format.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_records: list[dict] = []
    by_format: dict[str, int] = defaultdict(int)
    skipped: list[str] = []
    errors: list[str] = []

    raw_files = sorted(RAW_DIR.iterdir())
    supported = [f for f in raw_files if f.suffix.lower() in PARSERS]
    unsupported = [f for f in raw_files if f.suffix.lower() not in PARSERS]

    if verbose:
        print(f"  Raw directory : {RAW_DIR}")
        print(f"  Files found   : {len(raw_files)}  "
              f"({len(supported)} supported, {len(unsupported)} skipped)")
        print()

    for filepath in sorted(RAW_DIR.iterdir()):
        ext = filepath.suffix.lower()
        parser = PARSERS.get(ext)
        if parser is None:
            skipped.append(filepath.name)
            if verbose:
                print(f"  [skip]  {filepath.name}  (no parser for '{ext}')")
            continue

        if verbose:
            size_kb = filepath.stat().st_size / 1024
            print(f"  [parse] {filepath.name:<50} ({size_kb:,.1f} KB) ... ", end="", flush=True)
        try:
            records = parser(filepath)
            all_records.extend(records)
            by_format[ext] += 1
            if verbose:
                total_chars = sum(len(r["text"]) for r in records)
                print(f"{len(records)} doc(s), {total_chars:,} chars")
        except Exception as exc:
            errors.append(f"{filepath.name}: {exc}")
            if verbose:
                print(f"ERROR -- {exc}")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    stats = {
        "total_files_processed": sum(by_format.values()),
        "total_documents": len(all_records),
        "by_format": dict(by_format),
        "skipped": skipped,
        "errors": errors,
        "output_file": str(OUT_FILE),
    }

    if verbose:
        print()
        print(f"  Output        : {OUT_FILE}")
        print(f"  Documents     : {len(all_records)}")
        if by_format:
            print(f"  By format     : " + ", ".join(f"{k} x{v}" for k, v in sorted(by_format.items())))
        if errors:
            print(f"  Errors        : {len(errors)}")

    return stats


def main() -> None:
    run_parsing(verbose=True)


if __name__ == "__main__":
    main()
