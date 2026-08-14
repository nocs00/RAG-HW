# HW4 — RAG Answer Generation

## Subject Area

Mountain Bike Technical Assistant — first grounded QA pipeline on top of the HW1–HW3 knowledge base. Goal: answer only from retrieved context, cite the source, and say "I don't know" honestly when the context doesn't support an answer.

---

## Pipeline

```
User question
    ↓
┌─────────────────────────────────────┐
│  Retrieval (reused from HW2 + HW3)  │
│  FAISS top-12 semantic → cross-     │
│  encoder rerank → top-3 chunks      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Prompt assembly                    │
│  Grounded-answering system prompt   │
│  + context blocks (chunk_id,        │
│  source_file, score, text)          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  LLM call — local (Ollama)          │
│  llama3.1:8b, temperature 0         │
└─────────────────────────────────────┘
    ↓
Grounded answer + chunk_id / source_file citation
```

Retrieval is not reimplemented — it directly reuses `HW2/index/faiss.index` and `HW3/scripts/retrieval_improved.py`'s cross-encoder reranking (the method HW3 found most effective at fixing "right source, wrong chunk" errors).

---

## Repository Structure

```
HW4/
├── scripts/
│   └── rag_answer.py            # retrieval (HW2/HW3 reuse) → prompt → LLM → grounded answer
├── outputs/
│   ├── rag_answers_examples.md  # 10 test questions with answers, citations, comments
│   └── prompt_improvements.md   # 3 before/after prompt-improvement cases
└── README.md
```

---

## Model

| Component | Model / Method |
|-----------|-----------------|
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` (reused from HW2) |
| Vector index | FAISS `IndexFlatIP`, 240 chunks (reused from HW2) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` (reused from HW3) |
| Answer generation | **`llama3.1:8b` via [Ollama](https://ollama.com), running locally** |

**Why a local model:** this pipeline runs entirely offline/free via Ollama instead of a paid API — no API key or billing required. `temperature=0` for deterministic, reproducible answers.

---

## Usage

### Install & start Ollama (one-time)

```bash
brew install ollama
brew services start ollama
ollama pull llama3.1:8b
```

> **Note:** if your shell has a `python` alias/shim that doesn't point at this repo's `venv` (check with `alias python` — a stray `alias python=/opt/homebrew/bin/python3.11` in `~/.zshrc` is a common cause), use `venv/bin/python` explicitly instead of `python` in the commands below, or the script will fail with `ModuleNotFoundError` since the retrieval dependencies (`sentence-transformers`, `faiss-cpu`, `rank-bm25`) only live in `venv/`.

### Run all 10 test questions

```bash
venv/bin/python HW4/scripts/rag_answer.py
```

Saves `outputs/rag_answers_examples.md`.

### Single ad-hoc question

```bash
venv/bin/python HW4/scripts/rag_answer.py --query "How do I set sag on my fork?"
```

### Generate the prompt-improvement comparison

```bash
venv/bin/python HW4/scripts/rag_answer.py --improvements
```

Saves `outputs/prompt_improvements.md`.

---

## Prompt Template

```
You are a Mountain Bike Technical Assistant.
Answer the user's question using ONLY the context provided below — never use outside or general knowledge.

Rules:
1. Base your answer strictly on the retrieved context.
2. If the context does not contain enough information to answer the question, say so explicitly: "I do not have enough information in the retrieved documents to answer this question." Do not guess or fill gaps with general knowledge.
3. If the retrieved context is only weakly or tangentially related to the question, say so explicitly instead of answering as if it were a confident match.
4. Always cite the chunk_id(s) and source_file(s) you used to support your answer.

Context:
{retrieved_context}

Question:
{user_question}

Answer:
```

---

## Test Questions

10 questions covering all 4 required categories:

| ID | Query | Category |
|----|-------|----------|
| q1 | How do I set sag on my mountain bike fork? | Clear answer in context |
| q1-rephrased | My fork bottoms out too easily and feels harsh over bumps — how do I check if my sag is set correctly? | Rephrased question |
| q5 | What is rebound damping and how do I adjust it on a RockShox shock? | Clear answer in context |
| q6 | How do I check if my brake pads are worn and when should I replace them? | Clear answer (reranking-sensitive) |
| q7 | What is the difference between hardtail and full suspension mountain bikes? | Clear answer in context |
| q8 | How do I service my fork lowers and how often should it be done? | Clear answer (reranking-sensitive) |
| q4 | Which New Zealand trails are rated beginner and suitable for easy rides? | Weak retrieval chunk (documented HW3 failure) |
| q12 | What grease should I use when installing headset bearings? | Weak retrieval chunk (sparse KB coverage) |
| oos-1 | What tire pressure should I run on a fat bike in snow conditions? | Insufficient context (fallback) |
| oos-2 | What's the recommended battery voltage and charging time for an e-MTB battery? | Insufficient context (fallback) |

---

## Results

Full output: [`outputs/rag_answers_examples.md`](outputs/rag_answers_examples.md)

### What worked well

**Clear-context questions (q1, q5, q6, q7, q8)** all returned grounded, correctly cited answers with the right `chunk_id`/`source_file`. Q5 and q7 pulled and correctly synthesized chunks from **two different sources** (SRAM PDF + MHTML guide; Wikipedia + Markdown guide) without conflating them.

**Both out-of-KB fallback questions (oos-1, oos-2)** triggered the fallback rule correctly — the model explicitly stated it did not have enough information, rather than answering from general knowledge about fat bike tire pressure or e-MTB batteries (topics Llama 3.1 clearly "knows" from pretraining but which aren't in this KB).

**q12 (headset grease)** — sparse KB coverage — also triggered a partial fallback: the model declined the specific question but still surfaced the one tangentially related fact it found (Maxle axle grease), correctly citing it rather than inventing headset-specific advice.

### What was more mixed

**q1-rephrased** — the rephrased sag question retrieved a different (worse) top chunk than the original q1 phrasing (SRAM's "Bottomless Tokens" section instead of the actual sag-checking procedure), because "bottoms out" and "harsh" pulled toward bottom-out-tuning content instead of sag measurement. The model correctly recognized the mismatch and declined rather than forcing an answer from the wrong section — the fallback rule did its job, but the underlying retrieval mismatch on rephrasing is a real limitation carried over from HW2/HW3.

**q4 (beginner trails)** — the documented HW3 weakness (semantic/keyword retrieval can't reliably isolate "Easy"-difficulty trails) is still present at the retrieval layer: one of the three chunks returned (score −0.77) is a poor match. The LLM still answered fairly confidently rather than flagging the weak chunk explicitly, though it did list trail names correctly rather than fabricating new ones — grounding held even though relevance-flagging (rule 3) didn't fully kick in here. See prompt-improvement case 3 below for a closer look.

---

## Prompt Improvements

Full comparison: [`outputs/prompt_improvements.md`](outputs/prompt_improvements.md)

### 1. Citation enforcement
**Problem:** the naive prompt (`"Answer the question using the context..."`) produced a perfectly reasonable answer with zero reference back to the source — no way to verify it against the KB.
**Result:** adding the explicit "always cite chunk_id/source_file" rule made every subsequent answer traceable, with no loss in answer quality.

### 2. Fallback honesty
**Problem:** on the e-MTB battery question, the naive prompt produced a *vague deflection* ("I'd be happy to help you find it elsewhere!") rather than a clean, structured refusal — it noticed the mismatch but had no instructed format for saying so.
**Result:** the grounded prompt produced the exact required fallback sentence ("I do not have enough information in the retrieved documents..."), consistent and machine-checkable across all fallback cases.

### 3. Weak-context flagging
**Problem:** on the beginner-trails question, the naive prompt treated a low-relevance chunk (rerank score −0.77) as equally trustworthy as a strong match, listing it alongside good results with no distinction.
**Result:** the grounded prompt didn't fully solve this — the model still didn't explicitly call out the weak chunk — but it did become more precise, quoting the literal `Difficulty:` field from the chunk text instead of paraphrasing/inferring difficulty labels, which subtly reduces (but doesn't eliminate) the risk of a wrong classification. This is the one improvement area rule 3 ("flag weakly related context") only partially achieved — the underlying fix is still the retrieval-layer one HW3 already identified (structured metadata pre-filter on `difficulty_levels`), not a prompt fix.

---

## Conclusion

The grounded-answering prompt (rules 1, 2, 4) worked reliably across all 10 test questions — every answer was either correctly grounded-and-cited or correctly declined. Rule 3 (explicitly flagging weak/tangential context) is the weakest link: the model tends to answer confidently from whatever it's given unless the context is *completely* irrelevant, rather than distinguishing "somewhat relevant" from "clearly on-topic." Combining this prompt layer with HW3's still-unsolved retrieval-layer issues (difficulty-label filtering, sparse-topic coverage) would be the natural next improvement.
