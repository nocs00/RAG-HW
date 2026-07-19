"""Parser for PDF files — manufacturer guides and technical documents."""

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

    full_text = "\n\n".join(pages_text)

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
