"""
config.py — global constants for the HW1 knowledge-base pipeline.

Import from any script:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))  # HW1/
    from config import CHUNK_SIZE, RAW_DIR, ...
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Directories & files
# ---------------------------------------------------------------------------

HW1_DIR = Path(__file__).parent

RAW_DIR            = HW1_DIR / "data" / "raw"
PROCESSED_DIR      = HW1_DIR / "data" / "processed"
KNOWLEDGE_BASE_FILE = PROCESSED_DIR / "knowledge_base.jsonl"
CHUNKS_FILE        = PROCESSED_DIR / "chunks.jsonl"

# ---------------------------------------------------------------------------
# Chunking  (spec: chunk_size 500–1000 chars, overlap 100–200 chars)
# ---------------------------------------------------------------------------

CHUNK_SIZE    = 800   # max characters per chunk
CHUNK_OVERLAP = 150   # overlap characters between consecutive chunks

# ---------------------------------------------------------------------------
# Source-type mappings  (used by all chunkers)
# ---------------------------------------------------------------------------

DOMAIN_MAP: dict[str, str] = {
    "wikipedia": "knowledge",
    "markdown":  "guide",
    "pdf":       "manual",
    "csv":       "trail-data",
    "mhtml":     "web-article",
}

DOCTYPE_MAP: dict[str, str] = {
    "wikipedia": "encyclopedia article",
    "markdown":  "how-to guide",
    "pdf":       "technical manual",
    "csv":       "structured trail data",
    "mhtml":     "web article",
}
