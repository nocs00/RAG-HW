"""Parser for MHTML (.mhtml) saved web pages."""

import email
import email.policy
import re
from pathlib import Path
from datetime import date
from urllib.parse import urlparse

import html2text


def _extract_mhtml_meta(raw_text: str) -> dict:
    """Pull source URL and title from MHTML header lines."""
    url = ""
    title = ""
    for line in raw_text.splitlines()[:20]:
        if line.startswith("Snapshot-Content-Location:"):
            url = line.split(":", 1)[1].strip()
        if line.startswith("Subject:") and not line.startswith("Subject: =?"):
            title = line.split(":", 1)[1].strip()
    # Decode encoded subject via email module
    if not title:
        from email.header import decode_header
        raw_bytes = raw_text.encode("utf-8", errors="replace")
        msg = email.message_from_bytes(raw_bytes)
        subject_raw = msg.get("Subject", "")
        parts = decode_header(subject_raw)
        for part, enc in parts:
            if isinstance(part, bytes):
                title += part.decode(enc or "utf-8", errors="replace")
            else:
                title += str(part)
    return {"url": url.strip(), "title": title.strip()}


def _html_from_mhtml(raw: bytes) -> str:
    """Extract the first text/html payload from MHTML bytes.

    Tries the stdlib email parser first; falls back to a regex boundary split
    for files that the email parser fails to walk correctly (e.g. large multipart).
    """
    msg = email.message_from_bytes(raw, policy=email.policy.compat32)

    # Walk MIME parts looking for text/html
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            charset = part.get_content_charset() or "utf-8"
            return part.get_payload(decode=True).decode(charset, errors="replace")

    # Fallback: extract HTML between the multipart boundary manually
    text = raw.decode("utf-8", errors="replace")
    # Find the first <html> ... </html> block
    m = re.search(r"(<html[\s\S]*?</html>)", text, re.IGNORECASE)
    if m:
        return m.group(1)

    # Last resort: return a non-MHTML plain-text payload if present
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            payload = part.get_payload(decode=True)
            if payload:
                decoded = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                # Discard if it looks like raw MHTML source
                if not decoded.lstrip().startswith("From:"):
                    return decoded

    return ""


def parse_mhtml(filepath: Path) -> list[dict]:
    raw = filepath.read_bytes()
    raw_text = raw.decode("utf-8", errors="replace")
    meta = _extract_mhtml_meta(raw_text)

    html_content = _html_from_mhtml(raw)
    if not html_content:
        return []

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    text = h.handle(html_content).strip()

    if not text:
        return []

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
