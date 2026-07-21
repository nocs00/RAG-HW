# HW2 — Semantic Retrieval Layer

## Subject Area

Mountain Bike Technical Assistant — semantic search over the knowledge base built in HW1 (240 chunks from 9 sources covering suspension setup, bike assembly, maintenance, component compatibility, and NZ trail data).

---

## Pipeline

```
HW1/data/processed/chunks.jsonl
        ↓
  Embed all chunks  (sentence-transformers/all-MiniLM-L6-v2)
        ↓
  FAISS index  (index/faiss.index)
        ↓
  Query → embed → top-k cosine search → retrieved chunks
```

---

## Repository Structure

```
HW2/
├── scripts/
│   ├── retrieval.py          # embedding + indexing + search
│   ├── test_queries.py       # 10 predefined test queries
│   └── run_tests.py          # runs all test queries through retrieval
├── index/
│   ├── faiss.index           # persisted FAISS flat index
│   └── chunks_meta.json      # chunk metadata + model name
├── outputs/
│   └── retrieval_examples.md # 10 queries with results and analysis
└── README.md
```

---

## Embedding Model

| Parameter | Value |
|-----------|-------|
| Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Dimension | 384 |
| Similarity | Cosine (L2-normalised vectors + inner product) |
| Chunks indexed | 240 |

Both document chunks and user queries are encoded with the same model.

---

## Usage

### 1. Build the index (run once)

```bash
python HW2/scripts/retrieval.py --build
```

Embeds all 240 chunks from `HW1/data/processed/chunks.jsonl` and saves `index/faiss.index`.

### 2. Search with a single query

```bash
python HW2/scripts/retrieval.py --query "How do I set sag on my fork?" --k 3
```

Example output:

```
Query: How do I set sag on my fork?

Top-1: how_to_setup_suspension_chunk_0002 | score: 0.69
  Text: The video above shows how our former resident suspension guru, Seb Stott, set up his bikes...
  Source: HW1/data/raw/how_to_setup_suspension.mhtml

Top-2: how_to_setup_suspension_chunk_0004 | score: 0.62
  Text: 50mm), then multiply that by 100 to find the sag percentage. Helpfully, this is already marked on RockShox forks...
  Source: HW1/data/raw/how_to_setup_suspension.mhtml

Top-3: bicycle_suspension_wiki_chunk_0050 | score: 0.57
  Text: Sag refers to how much a suspension moves under just the static load of the rider...
  Source: HW1/data/raw/bicycle_suspension_wiki.txt
```

### 3. Run all 10 test queries

```bash
python HW2/scripts/run_tests.py          # k=3 (default)
python HW2/scripts/run_tests.py --k 5   # k=5
```

`run_tests.py` imports queries from `test_queries.py` and calls `retrieval.search()` directly for each one, printing results and expected-source notes.

---

## Test Queries

10 queries covering different source types and topics:

| ID | Query | Expected source |
|----|-------|----------------|
| q1 | How do I set sag on my mountain bike fork? | MHTML suspension guides |
| q2 | What torque for assembling a carbon steerer tube? | SRAM PDF, Trek PDF |
| q3 | How often to lube chain, what lube for wet conditions? | mtb_maintenance_guide |
| q4 | Which NZ trails are rated beginner / easy? | doc_mtb_tracks CSV |
| q5 | What is rebound damping, how to adjust on RockShox? | MHTML guides, SRAM PDF |
| q6 | How to check if brake pads are worn, when to replace? | mtb_maintenance_guide |
| q7 | Difference between hardtail and full suspension? | Wikipedia articles |
| q8 | How to service fork lowers and how often? | SRAM PDF, maintenance guide |
| q9 | Intermediate NZ trails longer than 2 hours? | doc_mtb_tracks CSV |
| q10 | Compression damping settings for climbing vs descending? | Suspension setup guides |

---

## Results

Full output with scores and per-query comments: [`outputs/retrieval_examples.md`](outputs/retrieval_examples.md)

---

## Conclusion

### What worked well

**Conceptual suspension queries (q1, q5, q10) — scores 0.67–0.72**

Queries about sag, rebound damping, and compression settings returned highly relevant results with strong scores. The knowledge base contains multiple overlapping sources (BikeRadar MHTML, liv-cycling Markdown, Trek MHTML, SRAM PDF) that all describe the same concepts, so the model finds dense semantic signal.

Example — q5 "What is rebound damping and how do I adjust it on a RockShox shock?":
```
Top-1: how_to_setup_suspension_chunk_0007 | score: 0.72
  Text: Rebound damping controls how quickly your suspension resets after absorbing an impact...
  Source: HW1/data/raw/how_to_setup_suspension.mhtml
```
All three top results directly answered the query with RockShox-specific dial instructions.

**Wikipedia-style factual queries (q7) — scores 0.71–0.75**

"What is the difference between hardtail and full suspension?" returned the highest consistent scores across all queries. Clean encyclopedic phrasing in Wikipedia sources aligns well with how the model was trained.

```
Top-1: mountain_bike_wiki_chunk_0006 | score: 0.75
  Text: Mountain bikes can usually be divided into four broad categories based on suspension configuration: Rigid... Hardtail...
  Source: HW1/data/raw/mountain_bike_wiki.txt
```

**Cross-source retrieval (q10) — 3 different source types in top-3**

The compression damping query pulled relevant chunks from a Markdown guide, an MHTML article, and a PDF manual — demonstrating that unified embeddings work across heterogeneous source formats.

---

### What could be improved

**Attribute/filter queries fail (q4) — not relevant results despite correct source**

"Which NZ trails are rated beginner and suitable for easy rides?" correctly retrieved `doc_mtb_tracks` chunks but returned intermediate/challenging trails instead of easy ones. Semantic embeddings cannot distinguish `difficulty: Easy` from `difficulty: Intermediate` when both appear in similar trail-description text.

```
Top-1: doc_mtb_tracks_chunk_0026 | score: 0.66
  Text: Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey...
  Source: HW1/data/raw/doc_mtb_tracks.csv
```

Fix: metadata pre-filtering on `difficulty_levels` before semantic re-ranking.

**PDF technical detail queries score lower (q2, q8) — scores 0.42–0.57**

Torque values and service intervals live in PDF tables and structured sections that pdfplumber extracts as flat text. The query "What torque for a carbon steerer?" retrieved steerer installation steps (relevant topic) but not the specific Nm value (relevant answer). PDF chunks lack heading structure, so semantic distance to exact technical specs is higher.

**Direct answer displaced to Top-2 by vocabulary-rich neighbour chunk (q3, q6)**

For "How often to lube chain / wet lube type", the chunk that explicitly says "Wet lube for wet/muddy conditions" ranked Top-2. Top-1 was the Key Lifehacks section which shares maintenance vocabulary ("every ride", "service", "intervals") but answers a different question. Smaller, more focused chunks or a cross-encoder re-ranker would fix the ranking.
