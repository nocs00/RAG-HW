"""
Split normalized documents from knowledge_base.jsonl into overlapping token chunks.

Output: HW1/data/chunks/chunks.jsonl
"""

import json
from pathlib import Path

import tiktoken

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CHUNK_SIZE = 512      # max tokens per chunk
CHUNK_OVERLAP = 64    # token overlap between consecutive chunks
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
    # First split on paragraphs to avoid cutting mid-sentence
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current_tokens: list[int] = []

    for para in paragraphs:
        para_tokens = enc.encode(para)

        # If a single paragraph exceeds chunk size, split it further by lines
        if len(para_tokens) > CHUNK_SIZE:
            sub_lines = [l.strip() for l in para.split("\n") if l.strip()]
            for line in sub_lines:
                line_tokens = enc.encode(line)
                if len(current_tokens) + len(line_tokens) > CHUNK_SIZE:
                    if current_tokens:
                        chunks.append(enc.decode(current_tokens))
                    # Start next chunk with overlap from previous
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


def main() -> None:
    enc = tiktoken.get_encoding(ENCODING)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total_chunks = 0

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

            for i, chunk_text in enumerate(text_chunks):
                chunk = {
                    "chunk_id": build_chunk_id(doc_id, i),
                    "text": chunk_text,
                    "metadata": {
                        # --- provenance (for grounded answers & citation) ---
                        "document_id":    doc_id,
                        "source_file":    doc["source_file"],
                        "source_type":    source_type,
                        "title":          doc["title"],
                        "url":            meta.get("url", ""),
                        "publisher":      meta.get("publisher", ""),
                        # --- chunk position (for precise citation) ----------
                        "chunk_index":    i,
                        "total_chunks":   n,
                        # --- content classification -------------------------
                        "domain":         _DOMAIN_MAP.get(source_type, "unknown"),
                        "document_type":  _DOCTYPE_MAP.get(source_type, "unknown"),
                        "topic_tags":     meta.get("topic_tags", []),
                        # --- language & access ------------------------------
                        "language":       meta.get("language", "en"),
                        "date_accessed":  meta.get("date_accessed", ""),
                    },
                }
                fout.write(json.dumps(chunk, ensure_ascii=False) + "\n")

            total_chunks += n
            print(f"  {doc_id:<45} {n:>3} chunks")

    print(f"\nDone: {total_chunks} total chunks -> {OUT_FILE}")


if __name__ == "__main__":
    main()
