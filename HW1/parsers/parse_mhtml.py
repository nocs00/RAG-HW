"""Parser for MHTML (.mhtml) saved web pages."""

import email
import re
from pathlib import Path
from datetime import date

import html2text


def _extract_mhtml_meta(msg: email.message.Message) -> dict:
    """Pull source URL and title from MHTML headers."""
    url = msg.get("Snapshot-Content-Location", "")
    subject_raw = msg.get("Subject", "")
    # Decode encoded subject (=?utf-8?Q?...?=)
    from email.header import decode_header
    parts = decode_header(subject_raw)
    title = ""
    for part, enc in parts:
        if isinstance(part, bytes):
            title += part.decode(enc or "utf-8", errors="replace")
        else:
            title += part
    return {"url": url.strip(), "title": title.strip()}


def parse_mhtml(filepath: Path) -> list[dict]:
    raw = filepath.read_bytes()
    msg = email.message_from_bytes(raw)
    meta = _extract_mhtml_meta(msg)

    # Extract the first text/html part; fall back to text/plain
    html_content = ""
    plain_content = ""
    for part in msg.walk():
        ctype = part.get_content_type()
        charset = part.get_content_charset() or "utf-8"
        if ctype == "text/html" and not html_content:
            html_content = part.get_payload(decode=True).decode(charset, errors="replace")
        elif ctype == "text/plain" and not plain_content:
            plain_content = part.get_payload(decode=True).decode(charset, errors="replace")

    if html_content:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0
        text = h.handle(html_content).strip()
    elif plain_content:
        text = plain_content.strip()
    else:
        return []

    if not text:
        return []

    from urllib.parse import urlparse
    publisher = urlparse(meta["url"]).netloc.replace("www.", "") or "Unknown"

    return [{
        "document_id": filepath.stem,
        "source_file": filepath.name,
        "source_type": "mhtml",
        "title": meta["title"],
        "text": text,
        "metadata": {
            "url": meta["url"],
            "publisher": publisher,
            "topic_tags": ["mountain-bike", "suspension", "setup"],
            "language": "en",
            "date_accessed": str(date.today()),
        },
    }]
