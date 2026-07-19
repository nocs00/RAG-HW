"""
Split normalized documents from knowledge_base.jsonl into overlapping token chunks.

Output: HW1/data/chunks/chunks.jsonl
"""

import json
from collections import defaultdict
from pathlib import Path

import tiktoken

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CHUNK_SIZE = 512       # max tokens per chunk
CHUNK_OVERLAP = 64     # token overlap between consecutive chunks
ENCODING = "cl100k_base"

IN_FILE = Path(__file__).parent.parent / "data" / "normalized" / "knowledge_base.jsonl"
OUT_FILE = Path(__file__).parent.parent / "data" / "chunks" / "chunks.jsonl"

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


def token_chunks(text: str, enc: tiktoken.Encoding) -> list[str]:
    """Split text into token-bounded chunks with overlap, preserving paragraph boundaries."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current_tokens: list[int] = []

    for para in paragraphs:
        para_tokens = enc.encode(para)

        if len(para_tokens) > CHUNK_SIZE:
            sub_lines = [l.strip() for l in para.split("\n") if l.strip()]
            for line in sub_lines:
                line_tokens = enc.encode(line)
                if len(current_tokens) + len(line_tokens) > CHUNK_SIZE:
                    if current_tokens:
                        chunks.append(enc.decode(current_tokens))
                    current_tokens = current_tokens[-CHUNK_OVERLAP:] + line_tokens
                else:
                    current_tokens += line_tokens
        else:
            if len(current_tokens) + len(para_tokens) > CHUNK_SIZE:
                if current_tokens:
                    chunks.append(enc.decode(current_tokens))
                current_tokens = current_tokens[-CHUNK_OVERLAP:] + para_tokens
            else:
                current_tokens += para_tokens

    if current_tokens:
        chunks.append(enc.decode(current_tokens))

    return chunks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_chunking(verbose: bool = True) -> dict:
    """Chunk all documents from knowledge_base.jsonl and write chunks.jsonl.

    Returns a stats dict.
    """
    enc = tiktoken.get_encoding(ENCODING)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_chunk_sizes: list[int] = []
    by_source_type: dict[str, int] = defaultdict(int)

    if verbose:
        print(f"  Input         : {IN_FILE}")
        print(f"  Chunk size    : {CHUNK_SIZE} tokens")
        print(f"  Overlap       : {CHUNK_OVERLAP} tokens  ({CHUNK_OVERLAP / CHUNK_SIZE * 100:.0f}%)")
        print(f"  Encoding      : {ENCODING}")
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

            text_chunks = token_chunks(doc["text"], enc)
            n = len(text_chunks)
            chunk_token_sizes = [len(enc.encode(c)) for c in text_chunks]
            all_chunk_sizes.extend(chunk_token_sizes)
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
                avg = sum(chunk_token_sizes) / n if n else 0
                print(f"  {doc_id:<45}  {n:>3} chunks  (avg {avg:.0f} tok)")

    total = len(all_chunk_sizes)
    avg_size = sum(all_chunk_sizes) / total if total else 0
    min_size = min(all_chunk_sizes) if all_chunk_sizes else 0
    max_size = max(all_chunk_sizes) if all_chunk_sizes else 0

    stats = {
        "total_chunks": total,
        "avg_chunk_tokens": round(avg_size, 1),
        "min_chunk_tokens": min_size,
        "max_chunk_tokens": max_size,
        "chunk_size_limit": CHUNK_SIZE,
        "overlap_tokens": CHUNK_OVERLAP,
        "by_source_type": dict(by_source_type),
        "output_file": str(OUT_FILE),
    }

    if verbose:
        print()
        print(f"  Output        : {OUT_FILE}")
        print(f"  Total chunks  : {total}")
        print(f"  Avg size      : {avg_size:.1f} tokens")
        print(f"  Min / Max     : {min_size} / {max_size} tokens")
        print(f"  By type       : " + ", ".join(f"{k} {v}" for k, v in sorted(by_source_type.items())))

    return stats


def main() -> None:
    run_chunking(verbose=True)


if __name__ == "__main__":
    main()
