"""
prepare_knowledge_base.py
=========================
End-to-end pipeline for Homework 1:

    raw files  -->  normalized JSONL  -->  chunks JSONL

Run from the repo root:
    python HW1/prepare_knowledge_base.py
"""

import sys
import time
from pathlib import Path

HW1_DIR = Path(__file__).parent
sys.path.insert(0, str(HW1_DIR / "scripts"))

from parse_all import run_parsing
from chunk_documents import run_chunking

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LINE = "-" * 60


def section(title: str) -> None:
    print(f"\n{LINE}")
    print(f"  {title}")
    print(LINE)


def summary_line(label: str, value) -> None:
    print(f"  {label:<30} {value}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    total_start = time.time()

    # ------------------------------------------------------------------ intro
    print()
    print("=" * 60)
    print("  Welcome to Homework 1")
    print("  Mountain Bike Technical Assistant — Knowledge Base Builder")
    print("=" * 60)
    print()
    print("  This script runs the full pipeline:")
    print("    1. Parse raw source files  ->  normalized JSONL")
    print("    2. Chunk normalized docs   ->  chunks JSONL")
    print()
    print(f"  Raw data  : {HW1_DIR / 'data' / 'raw'}")
    print(f"  Output    : {HW1_DIR / 'data'}")

    # ---------------------------------------------------------- step 1: parse
    section("Step 1 / 2  |  Parsing raw documents")
    t0 = time.time()
    parse_stats = run_parsing(verbose=True)
    parse_time = time.time() - t0

    # --------------------------------------------------------- step 2: chunk
    section("Step 2 / 2  |  Chunking normalized documents")
    t0 = time.time()
    chunk_stats = run_chunking(verbose=True)
    chunk_time = time.time() - t0

    # --------------------------------------------------------- final summary
    section("Pipeline complete — Summary")

    total_time = time.time() - total_start

    print()
    print("  [ Parsing ]")
    summary_line("Files processed",       parse_stats["total_files_processed"])
    summary_line("Documents produced",    parse_stats["total_documents"])
    for ext, count in sorted(parse_stats["by_format"].items()):
        summary_line(f"  {ext} files", count)
    if parse_stats["skipped"]:
        summary_line("Skipped files",     len(parse_stats["skipped"]))
    if parse_stats["errors"]:
        summary_line("Errors",            len(parse_stats["errors"]))
        for err in parse_stats["errors"]:
            print(f"    ! {err}")
    summary_line("Time",                  f"{parse_time:.2f}s")

    print()
    print("  [ Chunking ]")
    summary_line("Chunk size (max)",      f"{chunk_stats['chunk_size_limit']} tokens")
    summary_line("Overlap",               f"{chunk_stats['overlap_tokens']} tokens  "
                                          f"({chunk_stats['overlap_tokens'] / chunk_stats['chunk_size_limit'] * 100:.0f}%)")
    summary_line("Total chunks",          chunk_stats["total_chunks"])
    summary_line("Avg chunk size",        f"{chunk_stats['avg_chunk_tokens']} tokens")
    summary_line("Min / Max chunk size",  f"{chunk_stats['min_chunk_tokens']} / {chunk_stats['max_chunk_tokens']} tokens")
    for stype, count in sorted(chunk_stats["by_source_type"].items()):
        summary_line(f"  {stype}", f"{count} chunks")
    summary_line("Time",                  f"{chunk_time:.2f}s")

    print()
    print("  [ Total ]")
    summary_line("Wall time",             f"{total_time:.2f}s")
    print()
    print(f"  knowledge_base.jsonl -> {parse_stats['output_file']}")
    print(f"  chunks.jsonl         -> {chunk_stats['output_file']}")
    print()
    print("=" * 60)
    print("  Done. Knowledge base is ready.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
