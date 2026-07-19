"""Shared chunking utilities used by all type-specific chunkers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHUNK_SIZE, CHUNK_OVERLAP


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
    """Split text into character-bounded chunks with overlap.

    Strategy:
      1. Split on double newlines (paragraphs) first to avoid cutting mid-sentence.
      2. Accumulate units until CHUNK_SIZE is reached, then emit with overlap carry.
      3. Paragraphs > CHUNK_SIZE are split by lines, then by words if still too large.
      4. Post-process: hard-split any chunk still exceeding CHUNK_SIZE.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Pre-flatten: ensure every unit fits within CHUNK_SIZE
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
        sep = "\n\n" if "\n" not in unit else "\n"
        candidate = (current + sep + unit).strip() if current else unit
        if len(candidate) > CHUNK_SIZE:
            if current:
                chunks.append(current.strip())
            current = current[-CHUNK_OVERLAP:].strip() + sep + unit
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())

    # Post-process: hard-split any chunk still over limit (due to overlap carry)
    final: list[str] = []
    for chunk in chunks:
        if len(chunk) <= CHUNK_SIZE:
            final.append(chunk)
        else:
            final.extend(_split_long_text(chunk))
    return final
