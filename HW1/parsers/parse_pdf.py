"""Parser for PDF files — manufacturer guides and technical documents."""

import re
from pathlib import Path
from datetime import date

import pdfplumber

# Known metadata keyed by filename
_PDF_META: dict[str, dict] = {
    "trek_full_suspension_assembly_guide.pdf": {
        "url": "https://media.trekbikes.com/image/upload/v1689955921/D2C-RedBarn_FullSuspension_QuickAssemblyGuide.pdf",
        "publisher": "Trek Bikes",
        "title": "Trek Full Suspension Quick Assembly Guide",
        "topic_tags": ["assembly", "full-suspension", "trek", "setup"],
    },
    "Suspension_SRAM.pdf": {
        "url": "",
        "publisher": "SRAM",
        "title": "SRAM Suspension Guide",
        "topic_tags": ["suspension", "sram", "setup", "tuning"],
    },
}

# Patterns for noise removal
_TIMESTAMP_HEADER = re.compile(
    r"^\d{1,2}/\d{1,2}/\d{2,4},?\s+\d+:\d+\s*(?:AM|PM)\s+.+$",
    re.MULTILINE | re.IGNORECASE,
)
_STANDALONE_CHAR = re.compile(r"^\s*[A-Za-z]\s*$", re.MULTILINE)
_LEGAL_SECTION = re.compile(
    r"(warranty|trademark|copyright|all rights reserved|"
    r"©|\bpatent\b|legal notice|terms of use|privacy policy)",
    re.IGNORECASE,
)


def _clean_pdf_text(text: str) -> str:
    """Remove PDF extraction noise: timestamp page headers, column artifacts, boilerplate."""
    # 1. Remove repeated timestamp page headers (e.g. "7/19/26, 10:01 PM Suspension | SRAM")
    text = _TIMESTAMP_HEADER.sub("", text)

    # 2. Remove lines that are a single stray character (two-column PDF merge artifacts)
    text = _STANDALONE_CHAR.sub("", text)

    # 3. Drop table-of-contents blocks: 5+ consecutive short lines (<60 chars, no sentence punctuation)
    lines = text.splitlines()
    cleaned: list[str] = []
    toc_run = 0
    toc_buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        is_toc_like = stripped and len(stripped) < 60 and not re.search(r"[.!?]", stripped)
        if is_toc_like:
            toc_run += 1
            toc_buffer.append(line)
        else:
            if toc_run >= 6:
                pass  # discard the TOC block
            else:
                cleaned.extend(toc_buffer)
            toc_buffer = []
            toc_run = 0
            cleaned.append(line)

    if toc_run < 6:
        cleaned.extend(toc_buffer)

    text = "\n".join(cleaned)

    # 4. Collapse 3+ consecutive blank lines to one blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_pdf(filepath: Path) -> list[dict]:
    meta = _PDF_META.get(
        filepath.name,
        {
            "url": "",
            "publisher": "Unknown",
            "title": filepath.stem.replace("_", " ").title(),
            "topic_tags": ["mountain-bike"],
        },
    )

    pages_text: list[str] = []
    with pdfplumber.open(filepath) as pdf:
        total_pages = len(pdf.pages)
        for page in pdf.pages:
            t = (page.extract_text() or "").strip()
            if t:
                pages_text.append(t)

    full_text = _clean_pdf_text("\n\n".join(pages_text))

    return [{
        "document_id": filepath.stem,
        "source_file": filepath.name,
        "source_type": "pdf",
        "title": meta["title"],
        "text": full_text,
        "metadata": {
            "url": meta["url"],
            "publisher": meta["publisher"],
            "total_pages": total_pages,
            "topic_tags": meta["topic_tags"],
            "language": "en",
            "date_accessed": str(date.today()),
        },
    }]
