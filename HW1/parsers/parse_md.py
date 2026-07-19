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

    # Split into sections by ## headings
    sections: list[tuple[str, str]] = []
    current_section = "Introduction"
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_lines:
                sections.append((current_section, "\n".join(current_lines).strip()))
            current_section = line.lstrip("# ").strip()
            current_lines = []
        elif line.startswith("# "):
            continue  # skip top-level title line
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_section, "\n".join(current_lines).strip()))

    records = []
    for i, (section, content) in enumerate(sections):
        if not content.strip():
            continue
        records.append({
            "document_id": f"{filepath.stem}_{i:04d}",
            "source_file": filepath.name,
            "source_type": "markdown",
            "title": title,
            "text": content,
            "metadata": {
                "url": primary_url,
                "publisher": _domain(primary_url),
                "section": section,
                "section_index": i,
                "all_sources": urls,
                "topic_tags": ["mountain-bike"],
                "language": "en",
                "date_accessed": str(date.today()),
            },
        })

    return records
