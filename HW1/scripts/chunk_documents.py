"""
Split normalized documents from knowledge_base.jsonl into overlapping character chunks.

Chunk size : 800 chars  (range 500–1000)
Overlap    : 150 chars  (range 100–200)

Output: HW1/data/processed/chunks.jsonl
"""

import json
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CHUNK_SIZE = 800       # max characters per chunk  (500–1000 per spec)
CHUNK_OVERLAP = 150    # character overlap between consecutive chunks  (100–200 per spec)

IN_FILE = Path(__file__).parent.parent / "data" / "processed" / "knowledge_base.jsonl"
OUT_FILE = Path(__file__).parent.parent / "data" / "processed" / "chunks.jsonl"

# ---------------------------------------------------------------------------
# Mappings
# ---------------------------------------------------------------------------

_DOMAIN_MAP = {
    "wikipedia": "knowledge",
    "markdown":  "guide",
    "pdf":       "manual",
    "csv":       "trail-data",
    "mhtml":     "web-article",
}

_DOCTYPE_MAP = {
    "wikipedia": "encyclopedia article",
    "markdown":  "how-to guide",
    "pdf":       "technical manual",
    "csv":       "structured trail data",
    "mhtml":     "web article",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def build_chunk_id(document_id: str, index: int) -> str:
    return f"{document_id}_chunk_{index:04d}"


def _split_long_text(text: str) -> list[str]:
    """Hard-split a text that exceeds CHUNK_SIZE at word boundaries."""
    words = text.split()
    parts: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > CHUNK_SIZE:
            if current:
                parts.append(current.strip())
            current = current[-CHUNK_OVERLAP:].strip() + " " + word
        else:
            current = (current + " " + word).strip() if current else word
    if current.strip():
        parts.append(current.strip())
    return parts


def char_chunks(text: str) -> list[str]:
    """Split text into character-bounded chunks with overlap, preserving paragraph boundaries.

    Each chunk is self-contained and contains enough context to be read independently.
    Strategy:
      1. Split on double newlines (paragraphs) to avoid cutting mid-sentence.
      2. Accumulate paragraphs until CHUNK_SIZE is reached, then emit.
      3. Each new chunk starts with the last CHUNK_OVERLAP chars of the previous one.
      4. Paragraphs exceeding CHUNK_SIZE are split by lines, then by words if needed.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Flatten: break oversized paragraphs down to atomic units <= CHUNK_SIZE
    units: list[str] = []
    for para in paragraphs:
        if len(para) <= CHUNK_SIZE:
            units.append(para)
        else:
            lines = [l.strip() for l in para.split("\n") if l.strip()]
            for line in lines:
                if len(line) <= CHUNK_SIZE:
                    units.append(line)
                else:
                    units.extend(_split_long_text(line))

    chunks: list[str] = []
    current = ""

    for unit in units:
        separator = "\n\n" if "\n" not in unit else "\n"
        candidate = (current + separator + unit).strip() if current else unit
        if len(candidate) > CHUNK_SIZE:
            if current:
                chunks.append(current.strip())
            current = current[-CHUNK_OVERLAP:].strip() + separator + unit
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())

    # Post-process: hard-split any chunk still exceeding CHUNK_SIZE
    final: list[str] = []
    for chunk in chunks:
        if len(chunk) <= CHUNK_SIZE:
            final.append(chunk)
        else:
            final.extend(_split_long_text(chunk))
    return final


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_chunking(verbose: bool = True) -> dict:
    """Chunk all documents from knowledge_base.jsonl and write chunks.jsonl."""
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_chunk_sizes: list[int] = []
    by_source_type: dict[str, int] = defaultdict(int)

    if verbose:
        print(f"  Input         : {IN_FILE}")
        print(f"  Chunk size    : {CHUNK_SIZE} chars  (spec: 500–1000)")
        print(f"  Overlap       : {CHUNK_OVERLAP} chars  (spec: 100–200, {CHUNK_OVERLAP / CHUNK_SIZE * 100:.0f}%)")
        print()

    with (
        open(IN_FILE, encoding="utf-8") as fin,
        open(OUT_FILE, "w", encoding="utf-8") as fout,
    ):
        for line in fin:
            doc = json.loads(line)
            doc_id = doc["document_id"]
            source_type = doc["source_type"]
            meta = doc.get("metadata", {})

            text_chunks = char_chunks(doc["text"])
            n = len(text_chunks)
            chunk_char_sizes = [len(c) for c in text_chunks]
            all_chunk_sizes.extend(chunk_char_sizes)
            by_source_type[source_type] += n

            for i, chunk_text in enumerate(text_chunks):
                chunk = {
                    "chunk_id": build_chunk_id(doc_id, i),
                    "text": chunk_text,
                    "metadata": {
                        "document_id":   doc_id,
                        "source_file":   doc["source_file"],
                        "source_type":   source_type,
                        "title":         doc["title"],
                        "url":           meta.get("url", ""),
                        "publisher":     meta.get("publisher", ""),
                        "chunk_index":   i,
                        "total_chunks":  n,
                        "domain":        _DOMAIN_MAP.get(source_type, "unknown"),
                        "document_type": _DOCTYPE_MAP.get(source_type, "unknown"),
                        "topic_tags":    meta.get("topic_tags", []),
                        "language":      meta.get("language", "en"),
                        "date_accessed": meta.get("date_accessed", ""),
                    },
                }
                fout.write(json.dumps(chunk, ensure_ascii=False) + "\n")

            if verbose:
                avg = sum(chunk_char_sizes) / n if n else 0
                print(f"  {doc_id:<45}  {n:>3} chunks  (avg {avg:.0f} chars)")

    total = len(all_chunk_sizes)
    avg_size = sum(all_chunk_sizes) / total if total else 0
    min_size = min(all_chunk_sizes) if all_chunk_sizes else 0
    max_size = max(all_chunk_sizes) if all_chunk_sizes else 0

    stats = {
        "total_chunks": total,
        "avg_chunk_chars": round(avg_size, 1),
        "min_chunk_chars": min_size,
        "max_chunk_chars": max_size,
        "chunk_size_limit": CHUNK_SIZE,
        "overlap_chars": CHUNK_OVERLAP,
        "by_source_type": dict(by_source_type),
        "output_file": str(OUT_FILE),
    }

    if verbose:
        print()
        print(f"  Output        : {OUT_FILE}")
        print(f"  Total chunks  : {total}")
        print(f"  Avg size      : {avg_size:.1f} chars")
        print(f"  Min / Max     : {min_size} / {max_size} chars")
        print(f"  By type       : " + ", ".join(f"{k} {v}" for k, v in sorted(by_source_type.items())))

    return stats


def main() -> None:
    run_chunking(verbose=True)


if __name__ == "__main__":
    main()
