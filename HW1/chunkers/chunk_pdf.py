"""Chunker for PDF documents (source_type == 'pdf').

Extra metadata per chunk:
  - estimated_page : approximate page number based on character offset
  - total_pages    : total pages in the source PDF
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DOMAIN_MAP, DOCTYPE_MAP
from chunkers.base import build_chunk_id, char_chunks


def chunk_pdf(doc: dict) -> list[dict]:
    meta = doc.get("metadata", {})
    source_type = doc["source_type"]
    doc_id = doc["document_id"]
    total_pages = meta.get("total_pages", 1)
    full_text = doc["text"]
    total_chars = len(full_text) or 1

    chunks: list[dict] = []
    pieces = char_chunks(full_text)

    # Track approximate character offset to estimate page number
    char_offset = 0

    for i, piece in enumerate(pieces):
        # Estimate page: find the piece in the text from current offset
        pos = full_text.find(piece[:50], char_offset)
        if pos == -1:
            pos = char_offset
        estimated_page = max(1, round((pos / total_chars) * total_pages))
        char_offset = pos + len(piece)

        chunks.append({
            "chunk_id": build_chunk_id(doc_id, i),
            "text":     piece,
            "metadata": {
                # --- required ---
                "chunk_id":       build_chunk_id(doc_id, i),
                "document_id":    doc_id,
                "source_file":    doc["source_file"],
                "source_type":    source_type,
                "chunk_index":    i,
                # --- desired ---
                "title":          doc["title"],
                "section":        f"Page ~{estimated_page}",
                "language":       meta.get("language", "en"),
                "domain":         DOMAIN_MAP.get(source_type, "unknown"),
                "document_type":  DOCTYPE_MAP.get(source_type, "unknown"),
                # --- citation ---
                "url":            meta.get("url", ""),
                "publisher":      meta.get("publisher", ""),
                "estimated_page": estimated_page,
                "total_pages":    total_pages,
                "topic_tags":     meta.get("topic_tags", []),
                "date_accessed":  meta.get("date_accessed", ""),
            },
        })

    return chunks
