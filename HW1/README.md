# HW1 — Mountain Bike Technical Assistant Knowledge Base

## Subject Area

**Mountain Bike Technical Assistant** — a RAG-ready knowledge base covering suspension setup and tuning, bike assembly and maintenance, component compatibility, and trail information. Designed to answer questions like *"How do I set sag on my RockShox fork?"*, *"What torque should I use for a carbon steerer?"*, or *"Which NZ trails are rated beginner?"*.

---

## Sources

| File | Type | Publisher | Description |
|------|------|-----------|-------------|
| `bicycle_suspension_wiki.txt` | Wikipedia | Wikipedia | Encyclopedia article on bicycle suspension systems |
| `mountain_bike_wiki.txt` | Wikipedia | Wikipedia | Encyclopedia article on mountain bikes |
| `Suspension_SRAM.pdf` | PDF | SRAM | Official RockShox suspension user manual (78 pages) |
| `trek_full_suspension_assembly_guide.pdf` | PDF | Trek Bikes | Full-suspension bike quick assembly guide |
| `mtb_maintenance_guide.md` | Markdown | roadmancycling.com | MTB maintenance intervals, tips, and lifehacks |
| `mtb_suspension_setup_guide.md` | Markdown | liv-cycling.com | Step-by-step suspension setup guide |
| `how_to_setup_suspension.mhtml` | MHTML | bikeradar.com | BikeRadar web article: sag, damping, rebound tuning |
| `trek_suspension_guide.mhtml` | MHTML | trekbikes.com | Trek suspension setup and tuning guide |
| `doc_mtb_tracks.csv` | CSV | NZ Dept. of Conservation | 198 New Zealand DOC mountain bike trails with difficulty, length, description |

**Total:** 9 source files → 9 normalized documents → **240 chunks**

---

## Metadata Structure

Every chunk carries two layers of metadata.

### Top-level chunk fields
| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | string | Unique ID: `{document_id}_chunk_{NNNN}` |
| `text` | string | Chunk content (500–1000 chars) |
| `metadata` | object | See below |

### `metadata` object — required fields
| Field | Type | Description |
|-------|------|-------------|
| `document_id` | string | Source document identifier (filename stem) |
| `source_file` | string | Original filename |
| `source_type` | string | `pdf` / `wikipedia` / `markdown` / `mhtml` / `csv` |
| `title` | string | Document title |
| `section` | string | Section or page the chunk belongs to |
| `chunk_index` | int | 0-based position within the document |
| `language` | string | Always `"en"` |
| `domain` | string | `knowledge` / `guide` / `manual` / `web-article` / `trail-data` |
| `document_type` | string | Human-readable type (e.g. `"technical manual"`) |

### `metadata` — additional fields (per source type)
| Field | Source types | Description |
|-------|-------------|-------------|
| `url` | all | Source URL |
| `publisher` | all | Publisher name |
| `topic_tags` | all | List of topic keywords |
| `date_accessed` | all | ISO date of data collection |
| `section_index` | wikipedia, markdown, mhtml | Section ordinal in the document |
| `all_sources` | markdown | All reference URLs cited in the guide |
| `estimated_page` | pdf | Approximate page number (from char offset ratio) |
| `total_pages` | pdf | Total pages in the PDF |
| `trail_names` | csv | Names of trails contained in the chunk |
| `difficulty_levels` | csv | Unique difficulty ratings in the chunk |

---

## Chunking Strategy

### Parameters
| Parameter | Value | Spec |
|-----------|-------|------|
| Chunk size | 500–1000 chars (fluid) | 500–1000 |
| Overlap | 150 chars | 100–200 |
| Method | Sentence-boundary aware | — |

### Method
1. **Parse** each source file into a normalized JSONL record (one record per file).
2. **Section split** (Wikipedia, Markdown, MHTML): split by headings before chunking so each chunk stays within a single section. PDFs and CSV use the full document text.
3. **Fluid chunking** (`chunkers/base.py`):
   - Scan for the **last sentence end** (`.`, `!`, `?`) in the range `[pos+500, pos+1000]` — this is the preferred cut point.
   - Fall back to **word boundary** near position 1000 if no sentence end found.
   - **Overlap**: step back 150 chars and snap to the previous sentence start; extend to 300 chars if needed; skip overlap entirely rather than start mid-sentence.
4. **Noise removal** before chunking: decorative separator lines (`---`, `===`), lone page numbers, Markdown heading markers (`## →` text kept), inline `**bold**`/`_italic_` markers, and `null`/`undefined` JSON-LD artefacts from MHTML.

---

## Chunk Examples

### 1. Wikipedia (encyclopedia article)
```json
{
  "chunk_id": "bicycle_suspension_wiki_chunk_0000",
  "text": "Bicycle suspension\nBicycle suspension is the system, or systems, used to suspend the rider and bicycle in order to insulate them from the roughness of the terrain. Bicycle suspension is used primarily on mountain bikes, but is also common on hybrid bicycles.\nBicycle suspension can be implemented in a variety of ways, and any combination thereof:\nFront suspension\nRear suspension\nSuspension seatpost\nSuspension saddle\nSuspension stem (now uncommon)\nThe suspension stem is now uncommon with the ongoing trend of short stems which limit the suspension size and the \"slacker\" head tube angle for stability. Bicycles with only front suspension are referred to as hardtail and bicycles with suspension in both the front and rear are referred to as dual or full suspension bikes.",
  "metadata": {
    "document_id": "bicycle_suspension_wiki",
    "source_file": "bicycle_suspension_wiki.txt",
    "source_type": "wikipedia",
    "title": "Bicycle suspension",
    "section": "Introduction",
    "section_index": 0,
    "chunk_index": 0,
    "language": "en",
    "domain": "knowledge",
    "document_type": "encyclopedia article",
    "url": "https://en.wikipedia.org/wiki/Bicycle_suspension",
    "publisher": "Wikipedia"
  }
}
```

### 2. PDF (technical manual)
```json
{
  "chunk_id": "Suspension_SRAM_chunk_0005",
  "text": "Confirm there are no sharp bends, kinks, or damage to the cables/housing/brake hoses. Confirm the cables, housing, and brake hoses are not making contact with the steerer tube. Confirm cables, housing, or brake hoses DO NOT contact the steerer tube. If you are unsure if your fork is compatible with your cable or brake hose routing, contact your local authorized SRAM service center.",
  "metadata": {
    "document_id": "Suspension_SRAM",
    "source_file": "Suspension_SRAM.pdf",
    "source_type": "pdf",
    "title": "SRAM Suspension Guide",
    "section": "Page ~1",
    "chunk_index": 5,
    "language": "en",
    "domain": "manual",
    "document_type": "technical manual",
    "publisher": "SRAM",
    "estimated_page": 1,
    "total_pages": 78
  }
}
```

### 3. Markdown (how-to guide)
```json
{
  "chunk_id": "mtb_maintenance_guide_chunk_0001",
  "text": "Mud, dirt, and trail debris wear down components like chains, brakes, and suspension, causing expensive repairs if neglected. Well-maintained bikes deliver reliable handling and extended component lifespan. Your MTB always signals when it needs attention — squeaks, slips, and wobbles are its language.",
  "metadata": {
    "document_id": "mtb_maintenance_guide",
    "source_file": "mtb_maintenance_guide.md",
    "source_type": "markdown",
    "title": "Mountain Bike Maintenance: Tips, Intervals & Lifehacks",
    "section": "Why Maintenance Matters",
    "section_index": 1,
    "chunk_index": 1,
    "language": "en",
    "domain": "guide",
    "document_type": "how-to guide",
    "publisher": "roadmancycling.com"
  }
}
```

### 4. MHTML (web article)
```json
{
  "chunk_id": "how_to_setup_suspension_chunk_0000",
  "text": "Our essential guide to MTB suspension setup, with simple walkthrough steps, will help your bike work at its best. Getting your mountain bike suspension setup right can make all the difference. Most modern suspension works brilliantly if adjusted correctly, but finding the optimum settings can be tricky with so many adjustments and dials. It's worth persevering, though, because getting the setup of your suspension fork or rear shock right will enable your bike to work at its best, improving handling, grip and comfort.",
  "metadata": {
    "document_id": "how_to_setup_suspension",
    "source_file": "how_to_setup_suspension.mhtml",
    "source_type": "mhtml",
    "title": "How to set up your mountain bike suspension | BikeRadar",
    "section": "Introduction",
    "section_index": 0,
    "chunk_index": 0,
    "language": "en",
    "domain": "web-article",
    "document_type": "web article",
    "publisher": "bikeradar.com"
  }
}
```

### 5. CSV (structured trail data)
```json
{
  "chunk_id": "doc_mtb_tracks_chunk_0000",
  "text": "Globe Hill Track. Difficulty: Intermediate. Estimated biking time: 3 hr. This track is for both trampers and mountain bikers. It connects the Reefton township with the Globe Progress Mine site.\nRameka Track. Difficulty: Intermediate. Estimated biking time: 1 hr. This intermediate mountain bike track can be accessed from near the Canaan Downs car park.\nGold Creek Loop. Difficulty: Easy. Estimated biking time: 30 min.",
  "metadata": {
    "document_id": "doc_mtb_tracks",
    "source_file": "doc_mtb_tracks.csv",
    "source_type": "csv",
    "title": "New Zealand DOC Mountain Bike Tracks",
    "section": "Trails 1",
    "chunk_index": 0,
    "language": "en",
    "domain": "trail-data",
    "document_type": "structured trail data",
    "publisher": "New Zealand Department of Conservation",
    "trail_names": ["Globe Hill Track", "Rameka Track", "Gold Creek Loop"],
    "difficulty_levels": ["Easy", "Intermediate"]
  }
}
```

---

## Conclusion

### What worked well
- **Multi-format coverage** — five distinct source types (PDF, Wikipedia, Markdown, MHTML, CSV) were normalized into a unified JSONL schema without information loss.
- **Section-aware chunking** — Wikipedia, Markdown, and MHTML documents are split by headings before chunking, so every chunk belongs to exactly one section. This enables precise attribution in RAG answers.
- **Fluid sentence-boundary chunking** — chunks end at sentence boundaries (500–1000 char range), making each chunk self-contained and readable without mid-word or mid-sentence cuts.
- **Rich per-type metadata** — source-specific fields (estimated page for PDFs, trail names/difficulty for CSV, all_sources for Markdown) support filtered retrieval.
- **Noise removal** — repetitive safety warnings, decorative lines, navigation menus, legal boilerplate, and JSON-LD artefacts were stripped from both parsers and the chunking layer.

### What could be improved
- **PDF section detection** — pdfplumber returns flat text with no heading structure, so PDF chunks reference only approximate page numbers rather than real section titles. A more sophisticated PDF parser (e.g., PyMuPDF with font-size heuristics) would enable section-aware PDF chunking.
- **Short trailing chunks** — a few chunks are very short (50–100 chars) because they are the last fragment of a section. A merge-with-previous strategy would eliminate these.
- **Overlap for very long sentences** — when a sentence exceeds 2× the overlap window (>300 chars), the overlap is skipped entirely. This affects a small number of PDF chunks.
- **Single language** — the knowledge base is English-only. Multilingual support would require language detection and separate embedding models.
