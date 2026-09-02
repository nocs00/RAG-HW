# HW8 — Observability Metrics Summary

Computed from [`eval_results.md`](eval_results.md) (10 cases, ids 1–10).

```
Total cases: 10

Task success:
  yes:     6/10 = 60%   (ids 1, 2, 3, 7, 8, 10)
  partial: 2/10 = 20%   (ids 5, 6)
  no:      2/10 = 20%   (ids 4, 9)

Groundedness (only meaningful for the 3 cases that actually ran retrieval):
  good:           3/3 applicable = 100%   (ids 1, 2, 3)
  not_applicable: 7/10 total             (ids 4, 5, 6, 7, 8, 9, 10 — tool calls
                                           or no retrieval attempted at all)

Latency:
  average: 3,241 ms   (mean of all 10 calls)
  median:  1,282 ms   (less skewed by the cold-start outlier below)
  max:     21,679 ms  (id 1 — first call in the process; pays full
                       FAISS + reranker + Ollama cold-start cost once)
  max (warm calls only): 4,773 ms (id 3)
  min:     0 ms       (id 10 — clarification, no retrieval/tool call at all)

Error types:
  none:                   6   (ids 1, 2, 3, 7, 8, 10)
  wrong_routing:          3   (ids 4, 5, 6 — router never attempted retrieval
                                for a question the KB could plausibly answer)
  slot_extraction_error:  1   (id 9 — whole sentence fed to geocoder as "location")
```

**Reading the numbers**: the 60% raw success rate understates how the *tools*
performed — every tool call that actually ran (weather, part-manual lookup, and
all 3 knowledge-base retrievals) either answered correctly or declined honestly.
100% of the failures and partials (ids 4, 5, 6, 9 — 4/10 cases) trace back to two
router-level bugs, not to retrieval or generation quality: an incomplete keyword
list that never gives the KB a chance on 3/10 questions, and a slot extractor with
no failure mode for un-parseable input on the 4th. See the Quality Report for the
detailed breakdown.
