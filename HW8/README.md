# HW8 — Evaluation + Observability Layer

## Subject Area

Mountain Bike Technical Assistant — same chatbot as HW1–7. HW8 adds no new
features; it adds a minimal **eval + observability layer** on top of HW7's
LangGraph agent: a fixed 10-question eval set, a script that runs every
question through the live system and records a structured trace (route, tools
used, retrieved chunks/sources, answer, latency), a hand-annotated eval table
(task success / groundedness / answer quality / errors), rolled-up
observability metrics, and a quality report naming the 3 biggest real problems
the eval surfaced.

---

## Repository Structure

```
HW8/
├── scripts/
│   └── run_eval.py            # runs the 10-question eval set through HW7's agent, dumps eval_raw.json
├── outputs/
│   ├── eval_raw.json          # unedited machine trace per case (route, tools, answer, latency)
│   ├── eval_results.md        # full eval table, all required columns, hand-annotated
│   ├── eval_summary.md        # observability metrics (success/groundedness rate, latency, error types)
│   └── quality_report.md      # what was tested, what works, 3 main problems, next steps
└── README.md
```

`run_eval.py` only *collects* raw traces by calling `HW7/scripts/langgraph_flow.py`'s
`run_agent()` on each question and timing it — it does not judge quality. The
judgment columns (`task_success`, `groundedness`, `answer_quality`, `errors`,
`notes`) in `eval_results.md` were filled in by hand after reading each actual
answer against its question and, where the router's behavior looked suspicious,
by calling the underlying tool directly to check what it *would* have answered.

---

## Eval Set

10 questions, covering every required category:

| # | Category | Question(s) |
|---|---|---|
| 1 | Simple KB question | "How do I set sag on my mountain bike fork?" |
| 2–3 | Retrieval required | "How do I bleed my hydraulic disc brakes?", "What is rebound damping..." |
| 4 | Retrieval may return a weak/tangential chunk | "Which New Zealand trails are rated beginner..." |
| 5–6 | System should say "not enough information" | e-MTB battery voltage/charging, fat-bike tire pressure in snow |
| 7–8 | Tool required | Live weather forecast (Queenstown), official part-manual web lookup (RockShox Pike Ultimate) |
| 9 | Complex/ambiguous | "Is my bike ready to ride in the rain today or does it need maintenance first?" |
| 10 | Out-of-scope / clarification | "Tell me something interesting about mountain biking." |

---

## Usage

```bash
# Run all 10 eval questions through the live HW7 agent, save outputs/eval_raw.json
venv/bin/python HW8/scripts/run_eval.py
```

Requires the same runtime dependencies as HW7 (FAISS index + reranker from
HW2/HW3, a running local Ollama server for HW4's grounded-answer LLM call) plus
network access for the live weather and web-lookup tools.

---

## Results

Full table: [`outputs/eval_results.md`](outputs/eval_results.md)
Metrics: [`outputs/eval_summary.md`](outputs/eval_summary.md)
Quality report: [`outputs/quality_report.md`](outputs/quality_report.md)

```
Total cases: 10
Task success:  yes 6/10 (60%) · partial 2/10 (20%) · no 2/10 (20%)
Groundedness:  good 3/3 of the cases that actually ran retrieval (100%)
Latency:       avg 3,241 ms · median 1,282 ms · max 21,679 ms (cold-start outlier)
Error types:   none 6 · wrong_routing 3 · slot_extraction_error 1
```

---

## Conclusion

Every tool call that actually executed (weather, part-manual lookup, all 3
direct knowledge-base retrievals) produced a correct or honestly-declined
answer — the retrieval and generation layers built in HW2–HW4 hold up well.
100% of this eval's failures and partials instead trace back to the **router**:
3 of 10 questions never reached the knowledge base at all because the router's
fixed keyword list didn't match, and manually calling `search_knowledge_base`
on those same questions showed the tool would have answered at least one of
them correctly and given a better, more specific decline on the other two. The
3 main problems (narrow router keyword gate, no failure mode for slot
extraction, no model warm-up) are detailed in
[`quality_report.md`](outputs/quality_report.md); the first of these — the
routing gap — is the weak point the Final Project's technical improvement
addresses directly.
