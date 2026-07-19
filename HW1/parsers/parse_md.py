"""Parser for Markdown (.md) files — community guides compiled from web sources."""

import re
from pathlib import Path
from datetime import date
from urllib.parse import urlparse


def _domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "") if url else "unknown"


def parse_md(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Extract title and source URLs from the first ~10 lines
    title = filepath.stem.replace("_", " ").title()
    urls: list[str] = []

    for line in lines[:10]:
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
        urls.extend(re.findall(r"https?://[^\s\)\]]+", line))

    primary_url = urls[0] if urls else ""

    # Collect section headings for metadata
    sections = [l.lstrip("# ").strip() for l in lines if l.startswith("## ")]

    return [{
        "document_id": filepath.stem,
        "source_file": filepath.name,
        "source_type": "markdown",
        "title": title,
        "text": text.strip(),
        "metadata": {
            "url": primary_url,
            "publisher": _domain(primary_url),
            "sections": sections,
            "all_sources": urls,
            "topic_tags": ["mountain-bike"],
            "language": "en",
            "date_accessed": str(date.today()),
        },
    }]
