"""
HW3 — Iterative retrieval lab.

Loads the FAISS index and model once, then runs all 10 test queries from
HW2/scripts/test_queries.py sequentially. Each query prints:
  1. Question header
  2. Baseline section — plain semantic search results
  3. Auto-generated conclusion — relevance verdict + score analysis

Further improvement sections (metadata filtering, hybrid search, reranking)
will be added incrementally below the baseline.

Usage:
    python HW3/scripts/retrieval_improved.py          # all 10 queries, k=3
    python HW3/scripts/retrieval_improved.py --k 5
    python HW3/scripts/retrieval_improved.py --query "How do I bleed my brakes?"
    python HW3/scripts/retrieval_improved.py --build  # rebuild FAISS index
"""

import argparse
import json
import sys
from pathlib import Path
from io import TextIOBase

import faiss
import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

try:
    from rank_bm25 import BM25Okapi
    _HAS_BM25 = True
except ImportError:
    _HAS_BM25 = False

# Module-level chunk text cache — populated once, reused across all queries
_CHUNK_TEXTS: dict[str, str] = {}


class _Tee(TextIOBase):
    """Write to both stdout and a file simultaneously."""
    def __init__(self, file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(file_path, "w", encoding="utf-8")
        self._stdout = sys.__stdout__

    def write(self, s: str) -> int:
        self._stdout.write(s)
        self._file.write(s)
        return len(s)

    def flush(self) -> None:
        self._stdout.flush()
        self._file.flush()

    def close(self) -> None:
        self._file.close()

# ---------------------------------------------------------------------------
# Paths  (reuse the HW2 index)
# ---------------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parents[2]
CHUNKS_FILE = REPO_ROOT / "HW1" / "data" / "processed" / "chunks.jsonl"
INDEX_DIR   = REPO_ROOT / "HW2" / "index"
INDEX_FILE  = INDEX_DIR / "faiss.index"
META_FILE   = INDEX_DIR / "chunks_meta.json"

OUTPUT_FILE  = Path(__file__).resolve().parents[1] / "outputs" / "raw_output.md"
MODEL_NAME   = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ---------------------------------------------------------------------------
# Metadata filters — one per test query
# field values can be a str (exact match) or list[str] (any-of match)
# ---------------------------------------------------------------------------
METADATA_FILTERS = {
    "q1":  {
        "filter": {"source_type": "mhtml"},
        "reason": "Limit to MHTML articles (BikeRadar, Trek) — best suspension setup guides",
    },
    "q2":  {
        "filter": {"source_type": "pdf"},
        "reason": "Limit to PDF manuals — torque specs live in technical manuals (SRAM, Trek)",
    },
    "q3":  {
        "filter": {"document_id": "mtb_maintenance_guide"},
        "reason": "Limit to mtb_maintenance_guide — only source with drivetrain lube advice",
    },
    "q4":  {
        "filter": {"document_id": "doc_mtb_tracks"},
        "reason": "Limit to doc_mtb_tracks CSV — only source with NZ trail data",
    },
    "q5":  {
        "filter": {"source_type": "mhtml"},
        "reason": "Limit to MHTML articles — BikeRadar guide has RockShox-specific damping steps",
    },
    "q6":  {
        "filter": {"document_id": "mtb_maintenance_guide"},
        "reason": "Limit to mtb_maintenance_guide — brake pad wear thresholds are here",
    },
    "q7":  {
        "filter": {"source_type": "wikipedia"},
        "reason": "Limit to Wikipedia sources — encyclopedic definitions of bike types",
    },
    "q8":  {
        "filter": {"source_type": ["pdf", "markdown"]},
        "reason": "Limit to PDF manuals + Markdown guides — fork service procedures and intervals",
    },
    "q9":  {
        "filter": {"document_id": "doc_mtb_tracks"},
        "reason": "Limit to doc_mtb_tracks CSV — only source with NZ trail difficulty data",
    },
    "q10": {
        "filter": {"source_type": ["mhtml", "markdown"]},
        "reason": "Limit to MHTML articles + Markdown guides — compression damping setup content",
    },
    "q11": {
        "filter": {"document_id": "doc_mtb_tracks"},
        "reason": "Limit to doc_mtb_tracks CSV — trail duration data; 'days' in query overlaps with maintenance schedule vocabulary",
    },
    "q12": {
        "filter": {"source_type": "pdf"},
        "reason": "Limit to PDF manuals — headset bearing grease specs; 'grease/lube' overlaps with chain lube in maintenance guide",
    },
    "q13": {
        "filter": {"document_id": "doc_mtb_tracks"},
        "reason": "Limit to doc_mtb_tracks CSV — only source with NZ trail difficulty labels",
    },
}


# ---------------------------------------------------------------------------
# Index build  (identical to HW2)
# ---------------------------------------------------------------------------

def build_index() -> None:
    if not CHUNKS_FILE.exists():
        sys.exit(f"ERROR: chunks file not found at {CHUNKS_FILE}")

    chunks = []
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))

    print(f"Loaded {len(chunks)} chunks")
    texts    = [c["text"] for c in chunks]
    metadata = [
        {
            "chunk_id":    c["chunk_id"],
            "document_id": c["metadata"].get("document_id", ""),
            "source_file": c["metadata"].get("source_file", ""),
            "source_type": c["metadata"].get("source_type", ""),
            "title":       c["metadata"].get("title", ""),
            "section":     c["metadata"].get("section", ""),
        }
        for c in chunks
    ]

    model = SentenceTransformer(MODEL_NAME)
    print("Encoding chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump({"model": MODEL_NAME, "chunks": metadata}, f, indent=2)

    print(f"Index saved → {INDEX_FILE}  ({index.ntotal} vectors)")


# ---------------------------------------------------------------------------
# Load index + model  (once, shared across all queries)
# ---------------------------------------------------------------------------

def load_resources() -> tuple:
    if not INDEX_FILE.exists() or not META_FILE.exists():
        sys.exit("ERROR: Index not found. Run with --build first.")

    with open(META_FILE, encoding="utf-8") as f:
        meta_store = json.load(f)

    stored_model = meta_store.get("model", MODEL_NAME)
    chunks_meta  = meta_store["chunks"]

    print(f"Loading model : {stored_model}")
    model = SentenceTransformer(stored_model)

    print(f"Loading index : {INDEX_FILE}")
    index = faiss.read_index(str(INDEX_FILE))
    print(f"Index ready   : {index.ntotal} vectors, dim={index.d}\n")

    return index, model, chunks_meta


# ---------------------------------------------------------------------------
# Baseline search
# ---------------------------------------------------------------------------

def _baseline_search(query: str, k: int, index, model, chunks_meta: list) -> tuple[list, list]:
    """Run plain semantic search. Returns (metas, scores) for top-k results."""
    query_vec = model.encode([query], normalize_embeddings=True)
    query_vec = np.array(query_vec, dtype="float32")
    scores, indices = index.search(query_vec, k)
    result_metas  = [chunks_meta[i] for i in indices[0]]
    result_scores = list(scores[0])
    return result_metas, result_scores


def _print_results(metas: list, scores: list) -> None:
    for rank, (meta, score) in enumerate(zip(metas, scores), start=1):
        preview = _preview(meta["chunk_id"])
        print(f"**Top-{rank}:** `{meta['chunk_id']}` | score: **{score:.2f}**")
        print(f"- *Text:* {preview}")
        print(f"- *Source:* `HW1/data/raw/{meta['source_file']}`")
        print()


def _verdict(scores: list, metas: list) -> str:
    """Auto-generate a brief relevance conclusion from score data."""
    top1 = scores[0]

    if top1 >= 0.70:
        relevance = "**Highly relevant**"
    elif top1 >= 0.55:
        relevance = "**Relevant**"
    elif top1 >= 0.45:
        relevance = "**Partially relevant**"
    else:
        relevance = "**Weak** — retrieval struggles here"

    score_str  = " / ".join(f"**{s:.2f}**" for s in scores)
    sources    = list(dict.fromkeys(m["document_id"] for m in metas))
    source_str = ", ".join(f"`{s}`" for s in sources)

    if len(sources) == 1:
        source_note = f"All top-{len(scores)} from one source ({source_str})."
    else:
        source_note = f"Cross-source: {source_str}."

    return f"{relevance}. Scores: {score_str}. {source_note}"


# ---------------------------------------------------------------------------
# Metadata filtering search
# ---------------------------------------------------------------------------

def _matches_filter(meta: dict, filter_spec: dict) -> bool:
    for field, value in filter_spec.items():
        actual = meta.get(field, "")
        if isinstance(value, list):
            if actual not in value:
                return False
        else:
            if actual != value:
                return False
    return True


def _metadata_search(query: str, k: int, index, model, chunks_meta: list,
                     filter_spec: dict) -> tuple[list, list]:
    """Semantic search restricted to chunks that match filter_spec."""
    filtered_idx = [i for i, m in enumerate(chunks_meta) if _matches_filter(m, filter_spec)]

    if not filtered_idx:
        return [], []

    # Reconstruct embeddings for the filtered subset and build a temporary index
    subset_embs = np.array([index.reconstruct(i) for i in filtered_idx], dtype="float32")
    sub_index   = faiss.IndexFlatIP(subset_embs.shape[1])
    sub_index.add(subset_embs)

    query_vec = model.encode([query], normalize_embeddings=True)
    query_vec = np.array(query_vec, dtype="float32")

    actual_k        = min(k, len(filtered_idx))
    scores, sub_idx = sub_index.search(query_vec, actual_k)

    result_metas  = [chunks_meta[filtered_idx[i]] for i in sub_idx[0]]
    result_scores = list(scores[0])
    return result_metas, result_scores


def _filter_verdict(baseline_metas: list, filtered_metas: list,
                    baseline_scores: list, filtered_scores: list,
                    n_total: int, n_filtered: int) -> str:
    """Compare filtered results against baseline and describe what changed."""
    baseline_ids  = [m["chunk_id"] for m in baseline_metas]
    filtered_ids  = [m["chunk_id"] for m in filtered_metas]
    new_chunks    = [c for c in filtered_ids if c not in baseline_ids]
    kept_chunks   = [c for c in filtered_ids if c in baseline_ids]

    b_sources = list(dict.fromkeys(m["document_id"] for m in baseline_metas))
    f_sources = list(dict.fromkeys(m["document_id"] for m in filtered_metas))

    parts = [f"Search space: **{n_total} → {n_filtered}** chunks."]

    if filtered_ids == baseline_ids:
        parts.append("Results **unchanged** — filter did not affect top-k ranking.")
    else:
        if new_chunks:
            parts.append(f"**{len(new_chunks)} new chunk(s)** surfaced.")
        if len(kept_chunks) < len(baseline_ids):
            parts.append(f"**{len(baseline_ids) - len(kept_chunks)} baseline chunk(s)** replaced.")
        if filtered_scores and baseline_scores:
            delta = filtered_scores[0] - baseline_scores[0]
            sign  = "+" if delta >= 0 else ""
            parts.append(f"Top-1 score: **{baseline_scores[0]:.2f} → {filtered_scores[0]:.2f}** ({sign}{delta:.2f}).")
        if f_sources != b_sources:
            b_fmt = ", ".join(f"`{s}`" for s in b_sources)
            f_fmt = ", ".join(f"`{s}`" for s in f_sources)
            parts.append(f"Sources: [{b_fmt}] → [{f_fmt}].")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Reranking
# ---------------------------------------------------------------------------

def load_reranker() -> CrossEncoder:
    print(f"Loading reranker: {RERANK_MODEL}")
    return CrossEncoder(RERANK_MODEL)


def _ensure_texts_loaded() -> None:
    """Populate _CHUNK_TEXTS from chunks.jsonl (runs once)."""
    if _CHUNK_TEXTS:
        return
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunk = json.loads(line)
                _CHUNK_TEXTS[chunk["chunk_id"]] = chunk["text"]


def _get_full_text(chunk_id: str) -> str:
    """Return the complete chunk text (needed by cross-encoder)."""
    _ensure_texts_loaded()
    return _CHUNK_TEXTS.get(chunk_id, "")


def _rerank_search(query: str, k: int, index, model, chunks_meta: list,
                   reranker: CrossEncoder, candidate_k: int = 12) -> tuple[list, list]:
    """
    1. Fetch candidate_k results via semantic search.
    2. Score every (query, chunk_text) pair with the cross-encoder.
    3. Sort by cross-encoder score and return top-k.
    """
    query_vec = model.encode([query], normalize_embeddings=True)
    query_vec = np.array(query_vec, dtype="float32")

    actual_cand = min(candidate_k, len(chunks_meta))
    scores, indices = index.search(query_vec, actual_cand)

    candidates = [chunks_meta[i] for i in indices[0]]
    texts      = [_get_full_text(m["chunk_id"]) for m in candidates]
    pairs      = [[query, t] for t in texts]

    ce_scores = reranker.predict(pairs)

    ranked    = sorted(zip(ce_scores, candidates), key=lambda x: x[0], reverse=True)
    top_k     = ranked[:k]

    result_metas  = [m for _, m in top_k]
    result_scores = [float(s) for s, _ in top_k]
    return result_metas, result_scores


def _rerank_verdict(baseline_metas: list, reranked_metas: list,
                    candidate_k: int) -> str:
    """Describe what changed after reranking vs baseline top-k."""
    base_ids   = [m["chunk_id"] for m in baseline_metas]
    rerank_ids = [m["chunk_id"] for m in reranked_metas]

    parts = [f"Candidates rescored: **top-{candidate_k}** semantic → reranked to **top-{len(reranked_metas)}**."]

    if rerank_ids == base_ids:
        parts.append("Order **unchanged** — cross-encoder agrees with semantic ranking.")
    else:
        if rerank_ids[0] != base_ids[0]:
            parts.append(f"Top-1 changed: `{base_ids[0]}` → **`{rerank_ids[0]}`**.")
        else:
            parts.append("**Top-1 unchanged.**")

        moved = sum(
            1 for cid in rerank_ids
            if cid in base_ids and base_ids.index(cid) != rerank_ids.index(cid)
        )
        new_in_top = [cid for cid in rerank_ids if cid not in base_ids]
        if moved:
            parts.append(f"**{moved} chunk(s)** reordered.")
        if new_in_top:
            parts.append(f"**{len(new_in_top)} new chunk(s)** promoted from outside baseline top-{len(base_ids)}.")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Hybrid search  (BM25 keyword score + semantic score)
# ---------------------------------------------------------------------------

def _hybrid_search(query: str, k: int, index, model, chunks_meta: list,
                   alpha: float = 0.6) -> tuple[list, list]:
    """
    Combine normalised BM25 keyword score and cosine semantic score.
    final = alpha * semantic + (1 - alpha) * bm25_norm
    """
    if not _HAS_BM25:
        raise RuntimeError("rank_bm25 not installed. Run: pip install rank-bm25")

    _ensure_texts_loaded()

    # BM25 over all chunks
    texts_ordered = [_CHUNK_TEXTS.get(m["chunk_id"], "") for m in chunks_meta]
    tokenized     = [t.lower().split() for t in texts_ordered]
    bm25          = BM25Okapi(tokenized)
    bm25_scores   = bm25.get_scores(query.lower().split())
    bm25_max      = bm25_scores.max()
    bm25_norm     = bm25_scores / bm25_max if bm25_max > 0 else bm25_scores

    # Semantic scores for all chunks
    query_vec = model.encode([query], normalize_embeddings=True)
    query_vec = np.array(query_vec, dtype="float32")
    sem_arr   = np.zeros(len(chunks_meta), dtype="float32")
    raw_scores, raw_idx = index.search(query_vec, len(chunks_meta))
    for score, idx in zip(raw_scores[0], raw_idx[0]):
        sem_arr[idx] = score

    combined  = alpha * sem_arr + (1 - alpha) * bm25_norm
    top_k_idx = np.argsort(combined)[::-1][:k]

    result_metas  = [chunks_meta[i] for i in top_k_idx]
    result_scores = [float(combined[i]) for i in top_k_idx]
    return result_metas, result_scores


def _hybrid_verdict(baseline_metas: list, hybrid_metas: list,
                    baseline_scores: list, hybrid_scores: list,
                    alpha: float) -> str:
    """Describe what changed after hybrid vs baseline."""
    base_ids   = [m["chunk_id"] for m in baseline_metas]
    hybrid_ids = [m["chunk_id"] for m in hybrid_metas]

    parts = [f"BM25 weight: **{1 - alpha:.0%}**, semantic weight: **{alpha:.0%}**."]

    if hybrid_ids == base_ids:
        parts.append("Order **unchanged** — keyword scores aligned with semantic ranking.")
    else:
        if hybrid_ids[0] != base_ids[0]:
            parts.append(f"Top-1 changed: `{base_ids[0]}` → **`{hybrid_ids[0]}`**.")
        else:
            parts.append("**Top-1 unchanged.**")

        new_chunks = [c for c in hybrid_ids if c not in base_ids]
        moved      = sum(
            1 for cid in hybrid_ids
            if cid in base_ids and base_ids.index(cid) != hybrid_ids.index(cid)
        )
        if moved:
            parts.append(f"**{moved} chunk(s)** reordered by keyword boost.")
        if new_chunks:
            parts.append(f"**{len(new_chunks)} new chunk(s)** promoted via BM25.")

        b_sources = list(dict.fromkeys(m["document_id"] for m in baseline_metas))
        h_sources = list(dict.fromkeys(m["document_id"] for m in hybrid_metas))
        if h_sources != b_sources:
            b_fmt = ", ".join(f"`{s}`" for s in b_sources)
            h_fmt = ", ".join(f"`{s}`" for s in h_sources)
            parts.append(f"Sources: [{b_fmt}] → [{h_fmt}].")

    return " ".join(parts)


def _preview(chunk_id: str) -> str:
    _ensure_texts_loaded()
    text = _CHUNK_TEXTS.get(chunk_id, "(text not found)").replace("\n", " ")
    return text[:120] + "..." if len(text) > 120 else text


# ---------------------------------------------------------------------------
# Per-query output block
# ---------------------------------------------------------------------------

def run_query(q: dict, k: int, index, model, chunks_meta: list,
              reranker: CrossEncoder | None = None) -> None:
    alpha = 0.6

    # --- Baseline section ---
    print("### Baseline — plain semantic search")
    print()
    print(f"**Query:** {q['query']}")
    print()
    base_metas, base_scores = _baseline_search(q["query"], k, index, model, chunks_meta)
    _print_results(base_metas, base_scores)
    print(f"> **Conclusion:** {_verdict(base_scores, base_metas)}")
    print()

    # --- Metadata filtering section ---
    fspec = METADATA_FILTERS.get(q["id"])
    if fspec:
        filter_spec = fspec["filter"]
        reason      = fspec["reason"]
        filter_desc = ", ".join(
            f"{field}={'[' + ', '.join(v) + ']' if isinstance(v, list) else v}"
            for field, v in filter_spec.items()
        )
        n_filtered = sum(1 for m in chunks_meta if _matches_filter(m, filter_spec))

        print(f"### Metadata filtering — `{filter_desc}`")
        print()
        print(f"**Query:** {q['query']}")
        print()
        print(f"**Why:** {reason}  ")
        print(f"**Pool:** {len(chunks_meta)} → **{n_filtered}** chunks")
        print()

        filt_metas, filt_scores = _metadata_search(
            q["query"], k, index, model, chunks_meta, filter_spec
        )
        if filt_metas:
            _print_results(filt_metas, filt_scores)
        else:
            print("*(no chunks matched the filter)*\n")

        verdict = _filter_verdict(
            base_metas, filt_metas, base_scores, filt_scores,
            n_total=len(chunks_meta), n_filtered=n_filtered,
        )
        print(f"> **Conclusion:** {verdict}")
        print()

    # --- Hybrid search section ---
    if _HAS_BM25:
        print(f"### Hybrid search — `{alpha:.0%} semantic + {1-alpha:.0%} BM25`")
        print()
        print(f"**Query:** {q['query']}")
        print()

        hybrid_metas, hybrid_scores = _hybrid_search(
            q["query"], k, index, model, chunks_meta, alpha=alpha
        )
        _print_results(hybrid_metas, hybrid_scores)

        verdict = _hybrid_verdict(base_metas, hybrid_metas, base_scores, hybrid_scores, alpha)
        print(f"> **Conclusion:** {verdict}")
        print()
    else:
        print("### Hybrid search — *skipped: install rank-bm25*")
        print()

    # --- Reranking section ---
    if reranker is not None:
        candidate_k = max(k * 4, 12)
        print(f"### Reranking — `{RERANK_MODEL}`")
        print()
        print(f"**Query:** {q['query']}")
        print()
        print(f"**Candidates:** top-**{candidate_k}** semantic → rescored by cross-encoder → top-**{k}**")
        print()

        reranked_metas, reranked_scores = _rerank_search(
            q["query"], k, index, model, chunks_meta, reranker, candidate_k=candidate_k
        )
        _print_results(reranked_metas, reranked_scores)

        verdict = _rerank_verdict(base_metas, reranked_metas, candidate_k)
        print(f"> **Conclusion:** {verdict}")
        print()


# ---------------------------------------------------------------------------
# Iterative lab run
# ---------------------------------------------------------------------------

def run_all(k: int) -> None:
    sys.path.insert(0, str(REPO_ROOT / "HW2" / "scripts"))
    from test_queries import TEST_QUERIES  # noqa: PLC0415

    index, model, chunks_meta = load_resources()

    try:
        reranker = load_reranker()
    except Exception as exc:
        print(f"Warning: reranker could not be loaded ({exc}). Reranking section will be skipped.\n")
        reranker = None

    tee = _Tee(OUTPUT_FILE)
    sys.stdout = tee
    try:
        total = len(TEST_QUERIES)
        for i, q in enumerate(TEST_QUERIES, start=1):
            print(f"## [{i}/{total}] {q['id'].upper()} — {q['note']}")
            print()
            run_query(q, k, index, model, chunks_meta, reranker=reranker)
            print("---")
            print()
    finally:
        sys.stdout = sys.__stdout__
        tee.close()
        print(f"\nOutput saved → {OUTPUT_FILE}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="HW3 iterative retrieval lab")
    group  = parser.add_mutually_exclusive_group()
    group.add_argument("--build", action="store_true",
                       help="Embed chunks and build FAISS index")
    group.add_argument("--query", type=str,
                       help="Run a single ad-hoc query")
    parser.add_argument("--k", type=int, default=3,
                        help="Top-k results per query (default: 3)")
    args = parser.parse_args()

    if args.build:
        build_index()
    elif args.query:
        index, model, chunks_meta = load_resources()
        reranker = load_reranker()
        q = {"id": "adhoc", "query": args.query, "note": "ad-hoc query"}
        run_query(q, args.k, index, model, chunks_meta, reranker=reranker)
    else:
        run_all(args.k)


if __name__ == "__main__":
    main()
