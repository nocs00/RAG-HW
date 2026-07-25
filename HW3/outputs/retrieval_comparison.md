# Retrieval Comparison — Baseline vs Improved

Model: `sentence-transformers/all-MiniLM-L6-v2` (semantic) + `cross-encoder/ms-marco-MiniLM-L-6-v2` (reranking) + BM25 (hybrid)
k = 3 per query

---

## Summary table

| Query | Baseline top-1 | Best improved top-1 | Method | What changed |
|-------|---------------|---------------------|--------|--------------|
| Q1 — sag setup | `how_to_setup_suspension_chunk_0002` 0.69 | same chunk, hybrid score **0.75** | Hybrid | Top-1 unchanged across all methods; hybrid raised combined score. Filter removed Wikipedia noise from top-3. |
| Q2 — carbon steerer torque | `Suspension_SRAM_chunk_0016` 0.51 | same chunk, hybrid score **0.71** | Hybrid | Top-1 stable. Reranking promoted table-of-contents chunk (chunk_0000) — minor regression. Hybrid kept the better chunk with a higher score. |
| Q3 — chain lube wet | `mtb_maintenance_guide_chunk_0008` 0.47 *(service schedule — off-topic)* | **`mtb_maintenance_guide_chunk_0003`** 0.64 | Hybrid + Reranking | **Significant improvement.** BM25 boosted the chunk containing "Wet lube for wet/muddy conditions" from Top-2 → **Top-1**. Both hybrid and reranking fixed the displacement. |
| Q4 — beginner NZ trails | `doc_mtb_tracks_chunk_0026` 0.66 *(challenging Pakihi Track)* | `doc_mtb_tracks_chunk_0022` 2.51 | Reranking | Top-1 changed but still not an Easy-difficulty trail. **Fundamental limitation** — difficulty filtering requires metadata pre-filtering, not semantic or keyword techniques. |
| Q5 — rebound damping RockShox | `how_to_setup_suspension_chunk_0007` 0.72 | **`Suspension_SRAM_chunk_0037`** 0.78 | Hybrid + Reranking | **Significant improvement.** BM25 surfaced SRAM manual chunk with RockShox-specific rebound dial settings — more precise than the general BikeRadar article. Cross-source improvement. |
| Q6 — brake pad wear | `mtb_maintenance_guide_chunk_0003` 0.61 *(lube section — off-topic)* | **`mtb_maintenance_guide_chunk_0004`** 4.29 | Reranking | **Significant improvement.** Cross-encoder correctly promoted the chunk with "Replace when worn to 1–1.5 mm remaining" to Top-1. Semantic search was misled by shared maintenance vocabulary. |
| Q7 — hardtail vs full suspension | `mountain_bike_wiki_chunk_0006` 0.75 | same chunk confirmed at score **8.84** | Reranking | Top-1 unchanged. Reranking confirmed baseline with high confidence. Filter narrowed pool to Wikipedia only (87 chunks). Reranking added `mtb_suspension_setup_guide_chunk_0001` to top-3. |
| Q8 — fork service interval | `Suspension_SRAM_chunk_0051` 0.57 *(per-ride cleaning)* | **`mtb_maintenance_guide_chunk_0007`** 3.04 | Reranking | **Significant improvement.** Cross-encoder promoted the maintenance schedule table (with 50h fork service interval) to Top-1. Hybrid actually degraded — BM25 pulled in unrelated setup content. |
| Q9 — intermediate NZ trails >2h | `doc_mtb_tracks_chunk_0026` 0.74 *(challenging, not intermediate)* | **`doc_mtb_tracks_chunk_0015`** 0.80 | Hybrid | **Improvement.** BM25 promoted the chunk with literal "Difficulty: Intermediate, Advanced" label from Top-2 → **Top-1**. Semantic search ranked the longer-duration trail first regardless of difficulty label. |
| Q10 — compression climb/descend | `mtb_suspension_setup_guide_chunk_0006` 0.69 | same chunk, hybrid score **0.81** | Hybrid | Top-1 stable across all methods. Hybrid raised combined score. Filter and reranking both confirmed the baseline chunk is correct. |
| Q11 — Timber Trail days | `doc_mtb_tracks_chunk_0021` 0.69 *(40-min trail — wrong)* | **`doc_mtb_tracks_chunk_0022`** 4.23 | Reranking | **Significant improvement.** Reranking identified the multi-day trail description ("Full trail: 2-3 days, historic bush tramways") as the best answer. Semantic and hybrid both failed — "Timber Trail" as a keyword did not match the chunk text. |
| Q12 — headset bearing grease | `Suspension_SRAM_chunk_0015` 0.37 *(steerer damage — off-topic)* | **`Suspension_SRAM_chunk_0017`** 0.52 | Hybrid | Partial improvement. Hybrid promoted a more relevant grease-application chunk. All reranking scores are negative — topic is poorly covered in the knowledge base. No method fully answers the question. |
| Q13 — Easy difficulty NZ trails | `doc_mtb_tracks_chunk_0026` 0.64 *(challenging Pakihi Track)* | `doc_mtb_tracks_chunk_0015` 0.61 *(Intermediate/Advanced — still wrong)* | Hybrid | **No meaningful improvement.** CSV chunks with "Difficulty: Easy" label either don't exist or rank very low. Hybrid promoted an Intermediate chunk. All methods fail — requires a structured metadata filter on the `difficulty_levels` field. |

---

## Highlights

### Biggest gains — reranking

| Query | Baseline top-1 | Reranked top-1 | Score jump |
|-------|---------------|----------------|------------|
| Q6 — brake pads | `chunk_0003` *(lube section)* | **`chunk_0004`** *(1–1.5 mm wear threshold)* | 0.61 → **4.29** |
| Q8 — fork service | `chunk_0051` *(per-ride wipe)* | **`chunk_0007`** *(50h service table)* | 0.57 → **3.04** |
| Q11 — Timber Trail | `chunk_0021` *(40-min trail)* | **`chunk_0022`** *(2–3 day trail)* | 0.69 → **4.23** |

Cross-encoder rescoring consistently corrects the "vocabulary-rich neighbour" problem — chunks that share topic vocabulary with the query but do not actually answer it.

### Biggest gains — hybrid BM25

| Query | Baseline top-1 | Hybrid top-1 | Why BM25 helped |
|-------|---------------|--------------|-----------------|
| Q3 — chain lube | `chunk_0008` *(service schedule)* | **`chunk_0003`** *(wet lube advice)* | Exact match on "wet" + "lube" |
| Q5 — rebound RockShox | *(general BikeRadar article)* | **SRAM `chunk_0037`** *(RockShox dial steps)* | High term frequency of "RockShox" + "rebound" |
| Q9 — intermediate trails | *(challenging trail)* | **`chunk_0015`** *("Difficulty: Intermediate")* | Exact match on "intermediate" + "difficulty" label |

### Where improvements did not work

| Query | Problem | Recommendation |
|-------|---------|----------------|
| Q4 — beginner trails | CSV chunks describe trails generically; "Easy" label not repeated in the text body | Structured filter on the `difficulty_levels` metadata field |
| Q13 — Easy difficulty | Same issue — semantic + BM25 both match trail-description vocabulary, not the difficulty label | Same: structured pre-filter before semantic search |
| Q12 — headset grease | Topic simply not well covered in the knowledge base | Add a headset assembly source to the knowledge base |

---

## Conclusion

**Reranking** (cross-encoder) has the largest impact on queries where semantic search finds the right source but ranks chunks within it incorrectly (Q6, Q8, Q11).

**Hybrid BM25** works best when the query contains specific terms or labels that appear literally in the text — exact keyword matches that semantic embeddings treat as synonyms or dilute across neighbours (Q3 "wet lube", Q5 "RockShox", Q9 "Intermediate").

**Metadata filtering** narrows the search space and removes cross-source noise, but does not solve attribute-level filtering (difficulty=Easy) — that requires a structured pre-filter on metadata fields, not semantic search.
