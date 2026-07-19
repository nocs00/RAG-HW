"""Chunker for CSV trail data (source_type == 'csv').

The CSV document stores all trails as a single text blob plus a structured
`metadata.trails` list. Each chunk covers a subset of trails and includes
a summary of which trails and difficulty levels it contains.

Extra metadata per chunk:
  - trail_names      : names of trails in this chunk
  - difficulty_levels: unique difficulty values in this chunk
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DOMAIN_MAP, DOCTYPE_MAP
from chunkers.base import build_chunk_id, char_chunks


def chunk_csv(doc: dict) -> list[dict]:
    meta = doc.get("metadata", {})
    source_type = doc["source_type"]
    doc_id = doc["document_id"]
    trails: list[dict] = meta.get("trails", [])

    # Build a lookup: trail text snippet -> trail metadata
    trail_lookup: dict[str, dict] = {t["text"][:60]: t for t in trails}

    full_text = doc["text"]
    pieces = char_chunks(full_text)
    chunks: list[dict] = []

    for i, piece in enumerate(pieces):
        # Identify which trails appear in this chunk
        trail_names: list[str] = []
        difficulty_levels: set[str] = set()
        for trail in trails:
            if trail["name"] and trail["name"] in piece:
                trail_names.append(trail["name"])
                if trail.get("difficulty"):
                    difficulty_levels.add(trail["difficulty"])

        chunks.append({
            "chunk_id": build_chunk_id(doc_id, i),
            "text":     piece,
            "metadata": {
                # --- required ---
                "chunk_id":         build_chunk_id(doc_id, i),
                "document_id":      doc_id,
                "source_file":      doc["source_file"],
                "source_type":      source_type,
                "chunk_index":      i,
                # --- desired ---
                "title":            doc["title"],
                "section":          f"Trails {i + 1}",
                "language":         meta.get("language", "en"),
                "domain":           DOMAIN_MAP.get(source_type, "unknown"),
                "document_type":    DOCTYPE_MAP.get(source_type, "unknown"),
                # --- citation ---
                "url":              meta.get("url", ""),
                "publisher":        meta.get("publisher", ""),
                "topic_tags":       meta.get("topic_tags", []),
                "date_accessed":    meta.get("date_accessed", ""),
                # --- trail-specific ---
                "trail_names":      trail_names,
                "difficulty_levels": sorted(difficulty_levels),
            },
        })

    return chunks
