"""Parser for Wikipedia plain-text (.txt) files exported via the Wikipedia API."""

import re
from pathlib import Path
from datetime import date


def parse_txt(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    # First line is "# Title"
    title = lines[0].lstrip("# ").strip() if lines else filepath.stem
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

    # Collect section headings for metadata (useful for chunk-level citation later)
    sections = re.findall(r"^={2,3}\s*(.+?)\s*={2,3}$", text, re.MULTILINE)

    return [{
        "document_id": filepath.stem,
        "source_file": filepath.name,
        "source_type": "wikipedia",
        "title": title,
        "text": text.strip(),
        "metadata": {
            "url": url,
            "publisher": "Wikipedia",
            "sections": sections,
            "topic_tags": ["mountain-bike", "wikipedia"],
            "language": "en",
            "date_accessed": str(date.today()),
        },
    }]
