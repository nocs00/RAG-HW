"""Orchestrator: load knowledge_base.jsonl, dispatch to per-type chunkers, write chunks.jsonl."""

import json
import sys
from collections import defaultdict
from pathlib import Path

HW1_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(HW1_DIR))
sys.path.insert(0, str(HW1_DIR / "chunkers"))

from config import CHUNK_SIZE, CHUNK_OVERLAP, KNOWLEDGE_BASE_FILE, CHUNKS_FILE
from chunkers.chunk_wikipedia import chunk_wikipedia
from chunkers.chunk_markdown import chunk_markdown
from chunkers.chunk_pdf import chunk_pdf
from chunkers.chunk_csv import chunk_csv
from chunkers.chunk_mhtml import chunk_mhtml

CHUNKERS = {
    "wikipedia": chunk_wikipedia,
    "markdown":  chunk_markdown,
    "pdf":       chunk_pdf,
    "csv":       chunk_csv,
    "mhtml":     chunk_mhtml,
}


def run_chunking(verbose: bool = True) -> dict:
    """Chunk all documents and write chunks.jsonl. Returns stats dict."""
    CHUNKS_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_chunk_sizes: list[int] = []
    by_source_type: dict[str, int] = defaultdict(int)
    errors: list[str] = []

    if verbose:
        print(f"  Input         : {KNOWLEDGE_BASE_FILE}")
        print(f"  Chunk size    : {CHUNK_SIZE} chars  (spec: 500–1000)")
        print(f"  Overlap       : {CHUNK_OVERLAP} chars  (spec: 100–200, {CHUNK_OVERLAP / CHUNK_SIZE * 100:.0f}%)")
        print()

    with (
        open(KNOWLEDGE_BASE_FILE, encoding="utf-8") as fin,
        open(CHUNKS_FILE, "w", encoding="utf-8") as fout,
    ):
        for line in fin:
            doc = json.loads(line)
            source_type = doc["source_type"]
            chunker = CHUNKERS.get(source_type)
            if chunker is None:
                msg = f"{doc['document_id']}: no chunker for source_type '{source_type}'"
                errors.append(msg)
                if verbose:
                    print(f"  [skip]  {msg}")
                continue

            try:
                chunks = chunker(doc)
            except Exception as exc:
                msg = f"{doc['document_id']}: {exc}"
                errors.append(msg)
                if verbose:
                    print(f"  [error] {msg}")
                continue

            for chunk in chunks:
                fout.write(json.dumps(chunk, ensure_ascii=False) + "\n")

            sizes = [len(c["text"]) for c in chunks]
            all_chunk_sizes.extend(sizes)
            by_source_type[source_type] += len(chunks)

            if verbose:
                avg = sum(sizes) / len(sizes) if sizes else 0
                print(f"  [{source_type:<10}] {doc['document_id']:<45}  "
                      f"{len(chunks):>3} chunks  (avg {avg:.0f} chars)")

    total = len(all_chunk_sizes)
    avg_size = sum(all_chunk_sizes) / total if total else 0

    stats = {
        "total_chunks":    total,
        "avg_chunk_chars": round(avg_size, 1),
        "min_chunk_chars": min(all_chunk_sizes) if all_chunk_sizes else 0,
        "max_chunk_chars": max(all_chunk_sizes) if all_chunk_sizes else 0,
        "chunk_size_limit": CHUNK_SIZE,
        "overlap_chars":   CHUNK_OVERLAP,
        "by_source_type":  dict(by_source_type),
        "errors":          errors,
        "output_file":     str(CHUNKS_FILE),
    }

    if verbose:
        print()
        print(f"  Output        : {CHUNKS_FILE}")
        print(f"  Total chunks  : {total}")
        print(f"  Avg size      : {avg_size:.1f} chars")
        print(f"  Min / Max     : {stats['min_chunk_chars']} / {stats['max_chunk_chars']} chars")
        print(f"  By type       : " + ", ".join(f"{k} {v}" for k, v in sorted(by_source_type.items())))
        if errors:
            print(f"  Errors        : {len(errors)}")

    return stats


def main() -> None:
    run_chunking(verbose=True)


if __name__ == "__main__":
    main()
