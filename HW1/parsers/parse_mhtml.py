"""Parser for MHTML (.mhtml) saved web pages."""

import email
import email.policy
import quopri
import re
from pathlib import Path
from datetime import date
from urllib.parse import urlparse

import html2text


# ---------------------------------------------------------------------------
# Noise patterns for post-html2text cleanup
# ---------------------------------------------------------------------------

# Navigation bullet links:  "  * [Label](url)"  or  "  * [](url)"
_NAV_LINK_LINE   = re.compile(r"^\s*\*\s*\[.*?\]\(.*?\)\s*$")
# Bare image/anchor links with no text: "[](url)"
_EMPTY_LINK      = re.compile(r"\[]\([^)]+\)")
# "Home" breadcrumb standalone line
_BREADCRUMB      = re.compile(r"^\s*(Home|Skip to content)\s*$", re.IGNORECASE)
# Horizontal rule produced by html2text from <hr>
_HR_LINE         = re.compile(r"^\s*\*\s*\*\s*\*\s*$")
# Author / published-date lines: "Published: ..."  "By Author Name"
_BYLINE          = re.compile(r"^\s*(Published|Updated|Written|By)\b.*$", re.IGNORECASE)
# Cookie / GDPR notice keywords
_COOKIE_NOTICE   = re.compile(
    r"(cookie|gdpr|we use cookies|accept all|privacy settings)", re.IGNORECASE
)
# Quoted-printable encoding artifacts left in HTML attributes: "=3D", "3D\"", "=E2"
_QP_ARTIFACT     = re.compile(r"(=[\dA-F]{2}|=\n|\b3D[\"'])", re.IGNORECASE)


def _extract_mhtml_meta(raw_text: str) -> dict:
    """Pull source URL and title from MHTML header lines."""
    url = ""
    title = ""
    for line in raw_text.splitlines()[:20]:
        if line.startswith("Snapshot-Content-Location:"):
            url = line.split(":", 1)[1].strip()
        if line.startswith("Subject:") and not line.startswith("Subject: =?"):
            title = line.split(":", 1)[1].strip()
    if not title:
        from email.header import decode_header
        msg = email.message_from_bytes(raw_text.encode("utf-8", errors="replace"))
        parts = decode_header(msg.get("Subject", ""))
        for part, enc in parts:
            if isinstance(part, bytes):
                title += part.decode(enc or "utf-8", errors="replace")
            else:
                title += str(part)
    return {"url": url.strip(), "title": title.strip()}


def _decode_qp_html(html: str) -> str:
    """Fix quoted-printable artifacts in HTML that wasn't fully decoded."""
    if not _QP_ARTIFACT.search(html):
        return html
    try:
        return quopri.decodestring(html.encode("utf-8", errors="replace")).decode(
            "utf-8", errors="replace"
        )
    except Exception:
        return html


def _html_from_mhtml(raw: bytes) -> str:
    """Extract the first text/html payload from MHTML bytes.

    Falls back to regex extraction for large multipart files the email parser
    cannot walk correctly.
    """
    msg = email.message_from_bytes(raw, policy=email.policy.compat32)

    for part in msg.walk():
        if part.get_content_type() == "text/html":
            charset = part.get_content_charset() or "utf-8"
            return part.get_payload(decode=True).decode(charset, errors="replace")

    # Fallback: extract first <html>…</html> block via regex
    text = raw.decode("utf-8", errors="replace")
    m = re.search(r"(<html[\s\S]*?</html>)", text, re.IGNORECASE)
    if m:
        return _decode_qp_html(m.group(1))

    # Last resort: non-MHTML plain text
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            payload = part.get_payload(decode=True)
            if payload:
                decoded = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                if not decoded.lstrip().startswith("From:"):
                    return decoded

    return ""


def _is_nav_bullet(line: str) -> bool:
    """True if this line looks like a navigation bullet item (short, no prose)."""
    stripped = line.strip()
    # Plain bullet:  "  * Short Label"  with no sentence punctuation and short
    if re.match(r"^\s*\*\s+\S", line) and len(stripped) < 50 and not re.search(r"[.!?]", stripped):
        return True
    # Linked bullet: "  * [Label](url)"
    if _NAV_LINK_LINE.match(line):
        return True
    return False


def _strip_nav_blocks(lines: list[str]) -> list[str]:
    """Remove consecutive navigation bullet blocks (4+ nav lines in a row)."""
    result: list[str] = []
    buf: list[str] = []

    for line in lines:
        if _is_nav_bullet(line):
            buf.append(line)
        else:
            if len(buf) < 4:
                result.extend(buf)  # small list — keep (e.g. article sub-items)
            # else discard the nav block
            buf = []
            result.append(line)

    if len(buf) < 4:
        result.extend(buf)
    return result


def _clean_html_text(text: str) -> str:
    """Remove navigation, menus, breadcrumbs, footers and other boilerplate
    from html2text-converted content."""
    lines = text.splitlines()

    # Step 1: find the first content heading — a heading followed by prose (not nav bullets).
    # "Prose" = a non-empty, non-bullet line with >60 chars within the next 6 lines.
    # This skips navigation menus like "## Shop our brands" whose body is all bullets.
    def _heading_has_prose(idx: int) -> bool:
        lookahead = [l for l in lines[idx + 1: idx + 7] if l.strip()]
        return any(
            len(l.strip()) > 60 and not _is_nav_bullet(l) for l in lookahead
        )

    content_start = None
    for i, line in enumerate(lines):
        if re.match(r"^#{1,3} \S", line.strip()) and _heading_has_prose(i):
            content_start = i
            break

    if content_start is not None and content_start > 4:
        lines = lines[content_start:]

    # Step 2: remove nav bullet blocks
    lines = _strip_nav_blocks(lines)

    # Step 3: line-by-line noise removal
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()

        if _QP_ARTIFACT.search(stripped) and len(stripped) < 80:
            continue
        if _BREADCRUMB.match(stripped):
            continue
        if _HR_LINE.match(stripped):
            continue
        if _BYLINE.match(stripped):
            continue
        if _COOKIE_NOTICE.search(stripped) and len(stripped) < 200:
            continue
        line = _EMPTY_LINK.sub("", line)
        cleaned.append(line)

    text = re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned))
    return text.strip()


def parse_mhtml(filepath: Path) -> list[dict]:
    raw = filepath.read_bytes()
    raw_text = raw.decode("utf-8", errors="replace")
    meta = _extract_mhtml_meta(raw_text)

    html_content = _html_from_mhtml(raw)
    if not html_content:
        return []

    h = html2text.HTML2Text()
    h.ignore_links = True    # drop inline markdown links — reduces noise
    h.ignore_images = True
    h.body_width = 0
    h.skip_internal_links = True
    text = _clean_html_text(h.handle(html_content))

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
