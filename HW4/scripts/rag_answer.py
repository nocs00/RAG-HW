"""
HW4 — RAG answer-generation pipeline.

Reuses the HW2 FAISS index and HW3 cross-encoder reranker for retrieval, then
calls a local LLM (Ollama) with a grounded-answering prompt template to
produce a cited, fallback-aware answer.

Pipeline:
    question -> retrieve top-k chunks (HW3 reranked search)
             -> build grounded prompt with context
             -> call local LLM (Ollama)
             -> return answer with chunk_id / source_file citations

Usage:
    python HW4/scripts/rag_answer.py                  # run all test questions, save outputs/rag_answers_examples.md
    python HW4/scripts/rag_answer.py --k 5
    python HW4/scripts/rag_answer.py --query "How do I set sag on my fork?"
    python HW4/scripts/rag_answer.py --improvements    # generate outputs/prompt_improvements.md
"""

import argparse
import sys
from io import TextIOBase
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Paths — reuse HW2 index + HW3 retrieval/reranking code
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
ANSWERS_FILE = OUTPUT_DIR / "rag_answers_examples.md"
IMPROVEMENTS_FILE = OUTPUT_DIR / "prompt_improvements.md"

sys.path.insert(0, str(REPO_ROOT / "HW3" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW2" / "scripts"))
import retrieval_improved as retrieval  # noqa: E402

# ---------------------------------------------------------------------------
# Local LLM (Ollama)
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"
RETRIEVAL_K = 3
RERANK_CANDIDATE_K = 12


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


def call_llm(system_prompt: str, user_prompt: str, model: str = MODEL_NAME) -> str:
    """Call the local Ollama server with a system + user message pair."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.0},
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

GROUNDED_SYSTEM_PROMPT = """You are a Mountain Bike Technical Assistant.
Answer the user's question using ONLY the context provided below — never use outside or general knowledge.

Rules:
1. Base your answer strictly on the retrieved context.
2. If the context does not contain enough information to answer the question, say so explicitly: "I do not have enough information in the retrieved documents to answer this question." Do not guess or fill gaps with general knowledge.
3. If the retrieved context is only weakly or tangentially related to the question, say so explicitly instead of answering as if it were a confident match.
4. Always cite the chunk_id(s) and source_file(s) you used to support your answer."""

NAIVE_SYSTEM_PROMPT = None  # no system prompt — the "before" version from the spec

USER_TEMPLATE = """Context:
{context}

Question:
{question}

Answer:"""

NAIVE_USER_TEMPLATE = """Answer the question using the context.
Context: {context}
Question: {question}"""


def build_context(metas: list, scores: list, texts: list) -> str:
    blocks = []
    for meta, score, text in zip(metas, scores, texts):
        blocks.append(
            f"[chunk_id: {meta['chunk_id']} | source_file: {meta['source_file']} | score: {score:.2f}]\n{text}"
        )
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# Test questions — 10 covering all 4 required categories
# ---------------------------------------------------------------------------

TEST_QUESTIONS = [
    {"id": "q1", "query": "How do I set sag on my mountain bike fork?",
     "category": "clear answer in context"},
    {"id": "q1-rephrased", "query": "My fork bottoms out too easily and feels harsh over bumps — how do I check if my sag is set correctly?",
     "category": "rephrased question"},
    {"id": "q5", "query": "What is rebound damping and how do I adjust it on a RockShox shock?",
     "category": "clear answer in context"},
    {"id": "q6", "query": "How do I check if my brake pads are worn and when should I replace them?",
     "category": "clear answer in context (reranking-sensitive)"},
    {"id": "q7", "query": "What is the difference between hardtail and full suspension mountain bikes?",
     "category": "clear answer in context"},
    {"id": "q8", "query": "How do I service my fork lowers and how often should it be done?",
     "category": "clear answer in context (reranking-sensitive)"},
    {"id": "q4", "query": "Which New Zealand trails are rated beginner and suitable for easy rides?",
     "category": "weak retrieval chunk (documented HW3 failure)"},
    {"id": "q12", "query": "What grease should I use when installing headset bearings?",
     "category": "weak retrieval chunk (sparse KB coverage)"},
    {"id": "oos-1", "query": "What tire pressure should I run on a fat bike in snow conditions?",
     "category": "insufficient context (fallback)"},
    {"id": "oos-2", "query": "What's the recommended battery voltage and charging time for an e-MTB battery?",
     "category": "insufficient context (fallback)"},
]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def retrieve(query: str, k: int, index, model, chunks_meta, reranker) -> tuple[list, list, list]:
    """HW3's best-performing method: semantic top-candidate_k -> cross-encoder rerank -> top-k."""
    metas, scores = retrieval._rerank_search(
        query, k, index, model, chunks_meta, reranker, candidate_k=RERANK_CANDIDATE_K
    )
    texts = [retrieval._get_full_text(m["chunk_id"]) for m in metas]
    return metas, scores, texts


def answer_question(query: str, k: int, index, model, chunks_meta, reranker) -> None:
    metas, scores, texts = retrieve(query, k, index, model, chunks_meta, reranker)
    context = build_context(metas, scores, texts)
    answer = call_llm(GROUNDED_SYSTEM_PROMPT, USER_TEMPLATE.format(context=context, question=query))

    chunk_ids = ", ".join(m["chunk_id"] for m in metas)
    sources = ", ".join(sorted(set(f"HW1/data/raw/{m['source_file']}" for m in metas)))

    print(f"Question: {query}")
    print()
    print(f"Retrieved chunks: {chunk_ids}")
    print()
    print(f"Answer:\n{answer}")
    print()
    print(f"Source: {sources}")
    print()
    print("Comment: " + _auto_comment(metas, scores, answer))
    print()
    print("---")
    print()


def _auto_comment(metas: list, scores: list, answer: str) -> str:
    top1 = scores[0]
    declined = "do not have enough information" in answer.lower() or "not enough information" in answer.lower()
    weak_flagged = "weak" in answer.lower() or "tangential" in answer.lower() or "not directly" in answer.lower()
    cited = any(m["chunk_id"] in answer for m in metas)

    parts = []
    if declined:
        parts.append("Model declined to answer (fallback triggered).")
    elif weak_flagged:
        parts.append("Model flagged the retrieved context as weakly related.")
    else:
        parts.append("Model answered directly from context.")
    parts.append("Citation present." if cited else "No chunk_id citation found in answer text.")
    parts.append(f"Top-1 rerank score: {top1:.2f}.")
    return " ".join(parts)


def run_all(k: int) -> None:
    index, model, chunks_meta = retrieval.load_resources()
    reranker = retrieval.load_reranker()

    tee = _Tee(ANSWERS_FILE)
    sys.stdout = tee
    try:
        for i, q in enumerate(TEST_QUESTIONS, start=1):
            print(f"## [{i}/{len(TEST_QUESTIONS)}] {q['id']} — {q['category']}")
            print()
            answer_question(q["query"], k, index, model, chunks_meta, reranker)
    finally:
        sys.stdout = sys.__stdout__
        tee.close()
        print(f"\nOutput saved -> {ANSWERS_FILE}")


# ---------------------------------------------------------------------------
# Prompt-improvement demo — naive vs grounded prompt, 3 cases
# ---------------------------------------------------------------------------

IMPROVEMENT_CASES = [
    {
        "id": "case-1-citation",
        "query": "How do I set sag on my mountain bike fork?",
        "problem": "The naive prompt has no instruction to cite sources, so the model answers in general terms with no reference back to the knowledge base.",
    },
    {
        "id": "case-2-fallback",
        "query": "What's the recommended battery voltage and charging time for an e-MTB battery?",
        "problem": "The naive prompt never tells the model it's allowed to say \"I don't know\" — with irrelevant context stuffed in, it reaches for general knowledge instead of admitting the KB doesn't cover it.",
    },
    {
        "id": "case-3-weak-chunk",
        "query": "Which New Zealand trails are rated beginner and suitable for easy rides?",
        "problem": "The naive prompt treats retrieved context as automatically correct — it answers confidently even when the retrieved chunk is only tangentially related (a harder trail, not a beginner one).",
    },
]


def run_improvements(k: int) -> None:
    index, model, chunks_meta = retrieval.load_resources()
    reranker = retrieval.load_reranker()

    tee = _Tee(IMPROVEMENTS_FILE)
    sys.stdout = tee
    try:
        print("# Prompt Improvements — Before / After\n")
        for i, case in enumerate(IMPROVEMENT_CASES, start=1):
            metas, scores, texts = retrieve(case["query"], k, index, model, chunks_meta, reranker)
            context = build_context(metas, scores, texts)

            naive_answer = call_llm(
                "You are a helpful assistant.",
                NAIVE_USER_TEMPLATE.format(context=context, question=case["query"]),
            )
            improved_answer = call_llm(
                GROUNDED_SYSTEM_PROMPT,
                USER_TEMPLATE.format(context=context, question=case["query"]),
            )

            print(f"## {i}. {case['id']}\n")
            print(f"**Query:** {case['query']}\n")
            print(f"**Problem:** {case['problem']}\n")
            print("### Original prompt (naive)")
            print("```")
            print(NAIVE_USER_TEMPLATE.format(context="{retrieved_context}", question="{user_question}"))
            print("```")
            print(f"**Naive answer:**\n{naive_answer}\n")
            print("### Updated prompt (grounded)")
            print("```")
            print(GROUNDED_SYSTEM_PROMPT)
            print()
            print(USER_TEMPLATE.format(context="{retrieved_context}", question="{user_question}"))
            print("```")
            print(f"**Improved answer:**\n{improved_answer}\n")
            print("### Result")
            print(_diff_comment(naive_answer, improved_answer, metas))
            print("\n---\n")
    finally:
        sys.stdout = sys.__stdout__
        tee.close()
        print(f"\nOutput saved -> {IMPROVEMENTS_FILE}")


def _diff_comment(naive: str, improved: str, metas: list) -> str:
    naive_cited = any(m["chunk_id"] in naive for m in metas)
    improved_cited = any(m["chunk_id"] in improved for m in metas)
    naive_declined = "enough information" in naive.lower()
    improved_declined = "enough information" in improved.lower()

    parts = []
    if improved_cited and not naive_cited:
        parts.append("Citation appeared only after the prompt change.")
    if improved_declined and not naive_declined:
        parts.append("Model switched from a confident (likely ungrounded) answer to an honest fallback after the prompt change.")
    if not parts:
        parts.append("Compare the two answers above for tone/grounding differences.")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="HW4 RAG answer-generation pipeline")
    parser.add_argument("--query", type=str, help="Run a single ad-hoc question")
    parser.add_argument("--k", type=int, default=RETRIEVAL_K, help=f"Top-k chunks (default: {RETRIEVAL_K})")
    parser.add_argument("--improvements", action="store_true", help="Generate outputs/prompt_improvements.md")
    args = parser.parse_args()

    if args.improvements:
        run_improvements(args.k)
    elif args.query:
        index, model, chunks_meta = retrieval.load_resources()
        reranker = retrieval.load_reranker()
        answer_question(args.query, args.k, index, model, chunks_meta, reranker)
    else:
        run_all(args.k)


if __name__ == "__main__":
    main()
