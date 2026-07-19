"""Shared chunking utilities used by all type-specific chunkers."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHUNK_MIN, CHUNK_MAX, CHUNK_OVERLAP


# ---------------------------------------------------------------------------
# Noise removal
# ---------------------------------------------------------------------------

_DECORATIVE_LINE = re.compile(r"^\s*[-=*_~]{3,}\s*$")
_LONE_NUMBER     = re.compile(r"^\s*\d{1,4}\s*$")
_MARKDOWN_HEADING = re.compile(r"^#+\s+")
_INLINE_MARKUP   = re.compile(r"(\*{1,3}|_{1,2})(\S.*?\S|\S)\1")


def _clean_chunk_text(text: str) -> str:
    """Remove formatting noise (decorative lines, heading markers, inline markup,
    JSON artefacts) before chunking."""
    # Remove null/undefined artefact lines first (whole-text pass)
    text = _NULL_LINE.sub("", text)
    lines = []
    for line in text.splitlines():
        if _DECORATIVE_LINE.match(line):
            continue
        if _LONE_NUMBER.match(line):
            continue
        line = _MARKDOWN_HEADING.sub("", line)
        stripped_line = line.strip()
        # Skip if heading text was empty or just a noise word (e.g. "### null" → "null")
        if not stripped_line or _NULL_LINE.match(stripped_line):
            continue
        line = _INLINE_MARKUP.sub(r"\2", line)
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Boundary helpers
# ---------------------------------------------------------------------------

_SENT_END   = re.compile(r'[.!?]["\']?(?=\s|$)', re.MULTILINE)
# Matches sentence-ending punctuation + trailing whitespace.
# m.end() is the first character of the *next* sentence.
# NOTE: deliberately excludes bare \n\n — PDF extraction often places \n\n
# mid-sentence, so only punctuation-based boundaries are used.
_SENT_SEP   = re.compile(r'[.!?]["\']?\s+', re.MULTILINE)
# Standalone "null" / "undefined" artefacts from JSON-LD / script leakage
_NULL_LINE  = re.compile(r'^\s*(?:null|undefined|NaN)\s*$', re.MULTILINE)


def _last_sentence_end(text: str, lo: int, hi: int) -> int:
    """Position just after the last sentence-ending punctuation in text[lo:hi].
    Returns -1 if none found."""
    best = -1
    for m in _SENT_END.finditer(text, lo, hi):
        best = m.end()
    return best if best > lo else -1


def _last_sentence_start(text: str, lo: int, hi: int) -> int:
    """Return the start of the last sentence that begins in text[lo:hi].
    A sentence starts right after sentence-ending punctuation+whitespace or after
    a blank line.  Returns -1 if none found."""
    best = -1
    # Search a few chars before lo to catch sentence ends whose space falls at lo
    for m in _SENT_SEP.finditer(text, max(0, lo - 3), hi):
        start = m.end()
        if lo <= start < hi:
            best = start
    return best


def _snap_word_start(text: str, pos: int, floor: int) -> int:
    """Move pos left to the start of the current word, not below floor."""
    while pos > floor and text[pos - 1] not in " \n\t":
        pos -= 1
    return pos


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_chunk_id(document_id: str, index: int) -> str:
    return f"{document_id}_chunk_{index:04d}"


def char_chunks(text: str) -> list[str]:
    """Fluid chunking in CHUNK_MIN–CHUNK_MAX chars.

    Boundary preference (highest to lowest):
      1. Sentence end  (.  !  ?)
      2. Word boundary (space / newline)
      3. Hard cut at CHUNK_MAX  (last resort)

    Overlap: CHUNK_OVERLAP chars carried back to nearest word start.
    """
    text = _clean_chunk_text(text)
    if not text:
        return []

    chunks: list[str] = []
    pos = 0
    n = len(text)

    while pos < n:
        # Everything remaining fits within max — take it all
        if n - pos <= CHUNK_MAX:
            tail = text[pos:].strip()
            if tail:
                chunks.append(tail)
            break

        lo = pos + CHUNK_MIN
        hi = pos + CHUNK_MAX

        # 1. Best cut: last sentence end in [lo, hi]
        cut = _last_sentence_end(text, lo, hi)

        # 2. Fallback: word boundary near hi
        if cut == -1:
            cut = hi
            if cut < n and text[cut] not in " \n\t":
                word_start = _snap_word_start(text, cut, lo)
                cut = word_start if word_start > pos else hi

        chunk = text[pos:cut].strip()
        if chunk:
            chunks.append(chunk)

        # Overlap: look for a sentence start within [cut-CHUNK_OVERLAP, cut).
        # If none found, extend to [cut-CHUNK_OVERLAP*2, cut).
        # If still none, skip overlap entirely (no mid-sentence starts).
        overlap_floor = max(pos + 1, cut - CHUNK_OVERLAP)
        next_pos = _last_sentence_start(text, overlap_floor, cut)
        if next_pos == -1:
            extended_floor = max(pos + 1, cut - CHUNK_OVERLAP * 2)
            next_pos = _last_sentence_start(text, extended_floor, cut)
        pos = next_pos if next_pos > pos else cut

    return [c for c in chunks if len(c.strip()) >= 30]
