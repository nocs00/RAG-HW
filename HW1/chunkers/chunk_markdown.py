"""Chunker for Markdown guide documents (source_type == 'markdown').

Extra metadata per chunk:
  - section     : the ## heading the chunk belongs to
  - all_sources : all referenced URLs (multi-source guides)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DOMAIN_MAP, DOCTYPE_MAP
from chunkers.base import build_chunk_id, char_chunks


def _parse_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown text into (section_name, section_text) pairs by ## headings."""
    sections: list[tuple[str, str]] = []
    current_section = "Introduction"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            content = "\n".join(current_lines).strip()
            if content:
                sections.append((current_section, content))
            current_section = line.lstrip("# ").strip()
            current_lines = []
        elif line.startswith("# "):
            pass  # skip top-level title
        else:
            current_lines.append(line)

    content = "\n".join(current_lines).strip()
    if content:
        sections.append((current_section, content))
    return sections


def chunk_markdown(doc: dict) -> list[dict]:
    meta = doc.get("metadata", {})
    source_type = doc["source_type"]
    doc_id = doc["document_id"]
    chunk_index = 0
    chunks: list[dict] = []

    for sec_idx, (section_name, section_text) in enumerate(_parse_sections(doc["text"])):
        for piece in char_chunks(section_text):
            chunks.append({
                "chunk_id": build_chunk_id(doc_id, chunk_index),
                "text":     piece,
                "metadata": {
                    # --- required ---
                    "chunk_id":      build_chunk_id(doc_id, chunk_index),
                    "document_id":   doc_id,
                    "source_file":   doc["source_file"],
                    "chunk_index":   chunk_index,
                    # --- desired ---
                    "title":         doc["title"],
                    "section":       section_name,
                    "section_index": sec_idx,
                    "language":      meta.get("language", "en"),
                    "domain":        DOMAIN_MAP.get(source_type, "unknown"),
                    "document_type": DOCTYPE_MAP.get(source_type, "unknown"),
                    # --- citation ---
                    "url":           meta.get("url", ""),
                    "publisher":     meta.get("publisher", ""),
                    "all_sources":   meta.get("all_sources", []),
                    "topic_tags":    meta.get("topic_tags", []),
                    "date_accessed": meta.get("date_accessed", ""),
                },
            })
            chunk_index += 1

    return chunks
