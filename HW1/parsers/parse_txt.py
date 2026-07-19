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

    # Split into sections by == Heading == or === Heading ===
    sections: list[tuple[str, str]] = []
    current_section = "Introduction"
    current_lines: list[str] = []

    for line in lines[1:]:
        m = re.match(r"^={2,3}\s*(.+?)\s*={2,3}$", line)
        if m:
            if current_lines:
                sections.append((current_section, "\n".join(current_lines).strip()))
            current_section = m.group(1)
            current_lines = []
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
            "source_type": "wikipedia",
            "title": title,
            "text": content,
            "metadata": {
                "url": url,
                "publisher": "Wikipedia",
                "section": section,
                "section_index": i,
                "topic_tags": ["mountain-bike", "wikipedia"],
                "language": "en",
                "date_accessed": str(date.today()),
            },
        })

    return records
