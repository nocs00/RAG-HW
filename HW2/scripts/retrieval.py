"""
Semantic retrieval over the MTB knowledge base (HW1 chunks).

Usage:
    # Build FAISS index from chunks.jsonl (run once):
    python retrieval.py --build

    # Search with a query:
    python retrieval.py --query "How do I set sag on my fork?"

    # Search with custom k:
    python retrieval.py --query "..." --k 5
"""

import argparse
import json
import os
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parents[2]
CHUNKS_FILE = REPO_ROOT / "HW1" / "data" / "processed" / "chunks.jsonl"
INDEX_DIR   = Path(__file__).resolve().parents[1] / "index"
INDEX_FILE  = INDEX_DIR / "faiss.index"
META_FILE   = INDEX_DIR / "chunks_meta.json"

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_model() -> SentenceTransformer:
    print(f"Loading model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)


# ---------------------------------------------------------------------------
# Build index
# ---------------------------------------------------------------------------

def build_index() -> None:
    print(f"Reading chunks from: {CHUNKS_FILE}")
    if not CHUNKS_FILE.exists():
        sys.exit(f"ERROR: chunks file not found at {CHUNKS_FILE}")

    chunks = []
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))

    print(f"Loaded {len(chunks)} chunks")

    texts = [c["text"] for c in chunks]
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

    model = load_model()
    print("Encoding chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    print(f"Embedding dimension: {dim}")

    # Inner-product index (cosine similarity because vectors are L2-normalised)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"FAISS index built: {index.ntotal} vectors")

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump({"model": MODEL_NAME, "chunks": metadata}, f, indent=2)

    print(f"Index saved to:    {INDEX_FILE}")
    print(f"Metadata saved to: {META_FILE}")


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(query: str, k: int = 3) -> None:
    if not INDEX_FILE.exists() or not META_FILE.exists():
        sys.exit("ERROR: Index not found. Run with --build first.")

    with open(META_FILE, encoding="utf-8") as f:
        meta_store = json.load(f)

    stored_model = meta_store.get("model", MODEL_NAME)
    chunks_meta  = meta_store["chunks"]

    index = faiss.read_index(str(INDEX_FILE))
    model = SentenceTransformer(stored_model)

    query_vec = model.encode([query], normalize_embeddings=True)
    query_vec = np.array(query_vec, dtype="float32")

    scores, indices = index.search(query_vec, k)

    print(f"\nQuery: {query}\n")
    for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
        meta = chunks_meta[idx]
        preview = _preview(meta, idx)
        source_path = f"HW1/data/raw/{meta['source_file']}"
        print(f"Top-{rank}: {meta['chunk_id']} | score: {score:.2f}")
        print(f"  Text: {preview}")
        print(f"  Source: {source_path}")
        print()


def _preview(meta: dict, idx: int) -> str:
    """Return a short text preview. Reload from chunks.jsonl by chunk_id."""
    target_id = meta["chunk_id"]
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunk = json.loads(line)
            if chunk["chunk_id"] == target_id:
                text = chunk["text"].replace("\n", " ")
                return text[:120] + "..." if len(text) > 120 else text
    return "(text not found)"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="MTB semantic retrieval")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true", help="Embed chunks and build FAISS index")
    group.add_argument("--query", type=str, help="Query string to search")
    parser.add_argument("--k", type=int, default=3, help="Number of results to return (default: 3)")
    args = parser.parse_args()

    if args.build:
        build_index()
    else:
        search(args.query, k=args.k)


if __name__ == "__main__":
    main()
