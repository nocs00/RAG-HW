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

    records = []
    with pdfplumber.open(filepath) as pdf:
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            records.append({
                "document_id": f"{filepath.stem}_p{i + 1:04d}",
                "source_file": filepath.name,
                "source_type": "pdf",
                "title": meta["title"],
                "text": text,
                "metadata": {
                    "url": meta["url"],
                    "publisher": meta["publisher"],
                    "page_number": i + 1,
                    "total_pages": total_pages,
                    "topic_tags": meta["topic_tags"],
                    "language": "en",
                    "date_accessed": str(date.today()),
                },
            })

    return records
