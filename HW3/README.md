# HW3 — Improved Retrieval Pipeline

## Subject Area

Mountain Bike Technical Assistant — improved retrieval layer on top of the HW1/HW2 knowledge base. Goal: preserve baseline results for the same 13 queries, add metadata filtering and two additional improvements (hybrid BM25 search + cross-encoder reranking), and compare results before/after.

---

## Pipeline

```
User query
    ↓
┌─────────────────────────────────┐
│  Baseline                       │
│  FAISS top-k  (cosine, k=3)     │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Metadata filtering             │
│  Filter chunks by document_id   │
│  or source_type → search subset │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Hybrid search                  │
│  60% semantic + 40% BM25        │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Reranking                      │
│  top-12 semantic →              │
│  cross-encoder rescore → top-3  │
└─────────────────────────────────┘
```

All four sections are printed for every query in a single run. Models and index are loaded once and reused across all queries.

---

## Repository Structure

```
HW3/
├── scripts/
│   └── retrieval_improved.py    # iterative lab — all 4 sections per query
├── outputs/
│   ├── raw_output.md            # full output for all 13 queries (MD formatted)
│   └── retrieval_comparison.md  # comparison table: baseline vs improved
└── README.md
```

Index and metadata reused from HW2: `HW2/index/faiss.index`, `HW2/index/chunks_meta.json`.
Test queries reused from HW2: `HW2/scripts/test_queries.py` (extended to 13 queries).

---

## Models

| Component | Model / Method |
|-----------|---------------|
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` (384-dim, cosine) |
| Vector index | FAISS `IndexFlatIP` (reused from HW2) |
| Keyword scoring | BM25 (`rank_bm25`, `BM25Okapi`) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |

---

## Usage

### Install dependencies

```bash
pip install rank-bm25
# sentence-transformers and faiss-cpu already installed from HW2
```

### Run all 13 queries (default mode)

```bash
python HW3/scripts/retrieval_improved.py
```

Prints 4 sections per query to stdout and saves results to `HW3/outputs/raw_output.md`.

### Custom k

```bash
python HW3/scripts/retrieval_improved.py --k 5
```

### Single ad-hoc query

```bash
python HW3/scripts/retrieval_improved.py --query "How do I set sag on my fork?"
```

### Rebuild FAISS index (if needed)

```bash
python HW3/scripts/retrieval_improved.py --build
```

---

## Improvement Techniques

### 1. Metadata filtering

A metadata filter is defined per query (`document_id` or `source_type`). Before searching, only chunks matching the filter are selected. Search runs within the narrowed subset via a temporary FAISS sub-index.

Example filters:

| Query | Filter | Pool (before → after) |
|-------|--------|-----------------------|
| Q3 — chain lube | `document_id=mtb_maintenance_guide` | 240 → 11 |
| Q4 — beginner trails | `document_id=doc_mtb_tracks` | 240 → 40 |
| Q7 — hardtail vs full-sus | `source_type=wikipedia` | 240 → 87 |
| Q2 — carbon torque | `source_type=pdf` | 240 → 60 |

### 2. Hybrid search (BM25 + semantic)

Combined score formula:

```
final_score = 0.6 × semantic_score + 0.4 × bm25_normalized
```

`BM25Okapi` is built over all 240 chunks per query. Semantic scores come from a full FAISS search over all vectors. Both are normalised and combined. Top-k are taken from the combined score.

**Works best for:** queries with exact terms or difficulty labels present in the text (Q3 "wet lube", Q5 "RockShox", Q9 "Intermediate").

### 3. Reranking (cross-encoder)

1. FAISS returns top-12 candidates by semantic score
2. For each `(query, chunk_text)` pair the cross-encoder (`ms-marco-MiniLM-L-6-v2`) computes a relevance score
3. Candidates are re-sorted by cross-encoder score → top-3 returned

**Works best for:** queries where semantic search finds the right source but ranks chunks in the wrong order within it (Q6, Q8, Q11).

---

## Test Queries

13 queries — the original 10 from HW2 plus 3 new ones designed to demonstrate metadata filtering and hybrid search advantages:

| ID | Query | Target |
|----|-------|--------|
| q1 | How do I set sag on my mountain bike fork? | Suspension setup |
| q2 | What torque should I use when assembling a carbon steerer tube? | PDF manuals |
| q3 | How often should I lube my chain and what type of lube in wet conditions? | Maintenance guide |
| q4 | Which New Zealand trails are rated beginner and suitable for easy rides? | Trail CSV |
| q5 | What is rebound damping and how do I adjust it on a RockShox shock? | SRAM + MHTML |
| q6 | How do I check if my brake pads are worn and when should I replace them? | Maintenance guide |
| q7 | What is the difference between hardtail and full suspension mountain bikes? | Wikipedia |
| q8 | How do I service my fork lowers and how often should it be done? | PDF + Markdown |
| q9 | Are there any intermediate difficulty mountain bike tracks in NZ longer than 2 hours? | Trail CSV |
| q10 | What compression damping settings should I use for climbing versus descending? | Setup guides |
| q11 | How many days does it take to ride the Timber Trail in New Zealand? | Trail CSV — hybrid/reranking win |
| q12 | What grease should I use when installing headset bearings? | PDF manuals — hybrid win |
| q13 | Which New Zealand trails have difficulty rated as Easy? | Trail CSV — hybrid target |

---

## Results

Full output with all 4 sections per query: [`outputs/raw_output.md`](outputs/raw_output.md)

Comparison table baseline vs improved: [`outputs/retrieval_comparison.md`](outputs/retrieval_comparison.md)

---

## Conclusion

### What worked best

**Reranking (cross-encoder)** gave the largest accuracy gains on queries where semantic search found the right source but ranked chunks in the wrong order:

| Query | Baseline top-1 | Reranked top-1 | Score |
|-------|---------------|----------------|-------|
| Q6 — brake pads | `chunk_0003` (lube section) | **`chunk_0004`** (1–1.5 mm wear threshold) | 0.61 → **4.29** |
| Q8 — fork service | `chunk_0051` (per-ride wipe) | **`chunk_0007`** (50h service table) | 0.57 → **3.04** |
| Q11 — Timber Trail | `chunk_0021` (40-min trail) | **`chunk_0022`** (2–3 day trail) | 0.69 → **4.23** |

**Hybrid BM25** had significant impact when queries contained exact terms or labels present literally in the text:

| Query | Change |
|-------|--------|
| Q3 — chain lube | Promoted "Wet lube for wet/muddy conditions" chunk from Top-2 → **Top-1** |
| Q5 — rebound RockShox | Surfaced SRAM chunk with RockShox-specific dial steps above general BikeRadar article |
| Q9 — intermediate trails | Promoted chunk with literal "Difficulty: Intermediate, Advanced" label to **Top-1** |

**Metadata filtering** effectively narrows the search space and removes cross-source noise. It did not change top-k on queries where all baseline results already came from the target source (e.g. Q3, Q6 — all results were already from `mtb_maintenance_guide`).

### What did not improve

**Q4 and Q13** (beginner/Easy difficulty trails) — no method returned correct results. CSV chunks describe trails generically; the "Easy" label is not repeated enough in the chunk body for semantic or keyword matching to distinguish it. Fix: structured pre-filter on the `difficulty_levels` metadata field before semantic search.

**Q12** (headset bearing grease) — topic is poorly covered in the knowledge base. Hybrid provided a partial improvement but no method gives a complete answer.
