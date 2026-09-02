# Final Project — Technical Improvement Before Defense

## Subject Area

Mountain Bike Technical Assistant — same chatbot as HW1–8. This is the final
technical pass before defense: one real weak point, found and evidenced by
HW8's evaluation, fixed with one focused, measurable improvement — not a
feature dump.

See [`FINAL_IMPROVEMENT.md`](FINAL_IMPROVEMENT.md) for the full write-up:
weak point, improvement, before/after, changelog, and honestly-stated
remaining limitations.

---

## The weak point (found via HW8's eval)

HW8 ran 10 questions live through HW7's LangGraph agent and found that its
router's keyword list is a hard gate in front of the knowledge base: 3 of 10
questions never reached `search_knowledge_base` at all because none of their
words matched the router's fixed keyword list — they just got a generic,
one-size-fits-all clarification message. Manually calling the tool on those
same questions showed it would have answered one of them correctly (a real
list of easy-rated NZ trails) and given a much better, on-topic decline on the
other two. Full detail: [`HW8/outputs/quality_report.md`](../HW8/outputs/quality_report.md).

## The improvement

"Better routing" (per the assignment's option table): the router's "no
keyword matched" branch no longer dead-ends at an immediate clarification
message. It now routes to a new `knowledge_base_fallback` node that always
attempts a real knowledge-base lookup first, and only falls through to
clarification if *that* lookup itself declines — one new node, one new
conditional edge, on top of HW7's otherwise-unchanged LangGraph app.

---

## Repository Structure

```
FinalProject/
├── Final_Project.md            # assignment spec
├── FINAL_IMPROVEMENT.md         # weak point, improvement, before/after, changelog, limitations
├── scripts/
│   └── final_agent_flow.py      # HW7's graph + the routing fix (2 new nodes/edges, everything else reused verbatim)
├── outputs/
│   └── final_examples.md        # full traces: the 3 fixed questions + 2 unaffected-route regression checks + 1 chit-chat check
└── README.md
```

Reuses `HW7/scripts/langgraph_flow.py`'s `weather_workflow` /
`part_manual_workflow` / `knowledge_base_workflow` nodes and
`HW6/scripts/agent_flow.py`'s keyword tables, tools, and answer templates
unchanged — only the router's default branch and the new fallback/
clarification nodes are new code.

---

## Usage

```bash
# Run the 3 fixed questions + 2 unaffected-route + 1 chit-chat check, save outputs/final_examples.md
venv/bin/python FinalProject/scripts/final_agent_flow.py

# Run a single question and print the full final state as JSON
venv/bin/python FinalProject/scripts/final_agent_flow.py --ask "Which New Zealand trails are rated beginner and suitable for easy rides?"
```

---

## Result

| Question | Before (HW7/HW8) | After (Final Project) |
|---|---|---|
| "Which New Zealand trails are rated beginner..." | Generic clarification, no retrieval attempted | Correct, cited answer (`doc_mtb_tracks.csv`) |
| "...battery voltage and charging time for an e-MTB battery?" | Generic clarification | Specific decline: "I checked the knowledge base but couldn't find a grounded answer..." |
| "What tire pressure...fat bike in snow conditions?" | Generic clarification | Specific decline, same as above |
| "How do I set sag..." (keyword-matched, unaffected route) | Correct KB answer | Identical — no regression |
| "Is it a good day to ride...Queenstown..." (unaffected route) | Correct weather answer | Identical — no regression |

Full traces: [`outputs/final_examples.md`](outputs/final_examples.md). Remaining
limitations (brittle decline-detection via string match, unresolved
content-coverage gaps, unaddressed slot-extraction and latency findings from
HW8) are stated in [`FINAL_IMPROVEMENT.md`](FINAL_IMPROVEMENT.md).
