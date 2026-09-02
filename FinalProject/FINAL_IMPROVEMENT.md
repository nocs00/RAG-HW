# Final Technical Improvement

## 1. Selected weak point

HW8's eval (`HW8/outputs/quality_report.md`, Problem #1) found that the
router's keyword list is a hard gate in front of the knowledge base: if a
question doesn't contain one of a fixed set of ~15 phrases, it never reaches
`search_knowledge_base` at all — it just returns a generic, one-size-fits-all
clarification message. 3 of HW8's 10 eval questions (trail difficulty, e-MTB
battery specs, fat-bike tire pressure) hit exactly this gap. Manually calling
`search_knowledge_base` on those same questions showed the tool would have
answered one of them correctly (a real, cited list of easy-rated NZ trails)
and given a specific, on-topic decline on the other two — strictly better than
the generic non-answer the router actually produced.

## 2. Improvement implemented

"Better routing", per the assignment's option table. Changed the router's
default branch and added one new node + one new conditional edge to the
LangGraph app (`FinalProject/scripts/final_agent_flow.py`, built from HW7's
graph):

- Old: no keyword matched → `clarification` (dead end, no tool call, no
  attempt at an answer).
- New: no keyword matched → `knowledge_base_fallback` → always calls
  `search_knowledge_base` first. Only if *that* tool's own answer contains
  HW4's existing decline phrase ("enough information" — the guardrail HW4's
  grounded-answering prompt already produces) does the graph fall through to
  a clarification node, and even then the message now says a knowledge-base
  lookup was actually tried, instead of a blind three-way guess.

The 3 keyword-matched routes (`weather_workflow`, `part_manual_workflow`, the
exact-keyword `knowledge_base_workflow`) and every tool implementation are
unchanged — reused verbatim from HW5/HW6/HW7.

## 3. Why this improvement matters

A chatbot that silently refuses to even try answering a question it could
actually answer is worse than one that occasionally gives a wrong answer with
a citation the user can check — the failure mode here isn't hallucination
(the retrieval/generation layers built in HW2–HW4 were already reliable, see
HW8's summary), it's the router giving up before the rest of the pipeline
gets a chance to run at all.

## 4. Before / after behavior

### Before
```
Question: Which New Zealand trails are rated beginner and suitable for easy rides?
Answer: Could you please clarify your question? Are you asking about current/forecast
weather and riding conditions, a specific part's manual or spec sheet, or a general
how-to/maintenance question?
```

### After
```
Question: Which New Zealand trails are rated beginner and suitable for easy rides?
Answer: Based on the provided context, I can identify the following trails that are
rated as "Easy" and suitable for beginner riders:
* Te Ara a Waiau Walkway/Cycleway (chunk_id: doc_mtb_tracks_chunk_0026 |
  source_file: doc_mtb_tracks.csv | score: 3.18) — Estimated biking time: 1 hr
* Okahukura Loop (chunk_id: doc_mtb_tracks_chunk_0026 | source_file:
  doc_mtb_tracks.csv | score: 3.18) — Difficulty: Easy, 3 hr
* Braemar Road to Landslip Creek (chunk_id: doc_mtb_tracks_chunk_0037 |
  source_file: doc_mtb_tracks.csv | score: 0.99) — Difficulty: Easy, 2 hr
...
```

---

### Before
```
Question: What's the recommended battery voltage and charging time for an e-MTB battery?
Answer: Could you please clarify your question? Are you asking about current/forecast
weather and riding conditions, a specific part's manual or spec sheet, or a general
how-to/maintenance question?
```

### After
```
Question: What's the recommended battery voltage and charging time for an e-MTB battery?
Answer: I checked the knowledge base but couldn't find a grounded answer to that.
Could you please clarify your question? Are you asking about current/forecast weather
and riding conditions, a specific part's manual or spec sheet, or a general
how-to/maintenance question?
```

---

### Before
```
Question: What tire pressure should I run on a fat bike in snow conditions?
Answer: Could you please clarify your question? Are you asking about current/forecast
weather and riding conditions, a specific part's manual or spec sheet, or a general
how-to/maintenance question?
```

### After
```
Question: What tire pressure should I run on a fat bike in snow conditions?
Answer: I checked the knowledge base but couldn't find a grounded answer to that.
Could you please clarify your question? Are you asking about current/forecast weather
and riding conditions, a specific part's manual or spec sheet, or a general
how-to/maintenance question?
```

Full raw traces for all 3 before/after pairs (plus 2 unaffected-route
regression checks): [`outputs/final_examples.md`](outputs/final_examples.md).

## 5. How it was tested

Re-ran the exact 3 questions HW8 flagged (ids 4, 5, 6) plus 2 questions from
unaffected routes (a keyword-matched KB question, a weather question) through
`final_agent_flow.py` to confirm no regression.

- Before (HW7, HW8 eval): 3/3 flagged questions got the generic clarification
  message, 0/3 attempted retrieval.
- After (Final Project): 3/3 attempt retrieval; 1/3 (trail difficulty) now
  returns a correct, cited answer instead of a non-answer; 2/3 (battery
  voltage, tire pressure) still end in clarification, but now specific to
  having actually checked the KB rather than a blind guess.
- Unaffected routes (sag question → `knowledge_base_workflow`, weather
  question → `weather_workflow`): identical output to HW7, confirming the
  change is additive, not a regression.

## 6. Remaining limitations

- The decline check is a brittle string match (`"enough information" in
  answer.lower()`) — it depends entirely on the LLM's grounded-answering
  prompt continuing to phrase its refusal that way; a proper fix would use a
  numeric retrieval-score threshold (as sketched in the assignment's own
  example) rather than string-matching the model's own output.
- Two of the three fixed questions (battery voltage, tire pressure) still end
  in a clarification message — the improvement makes the router *try*
  the KB before giving up, but it doesn't make the KB contain information it
  never had. That's a content-coverage gap, not something routing can fix.
- HW8's other two findings — no slot-extraction failure mode in the weather
  tool (id 9) and the 21.7s cold-start latency spike (id 1) — are unaddressed;
  this improvement scoped to the single highest-impact problem (3/10 eval
  cases) rather than fixing all three.
- The fallback now runs a full retrieval + LLM call for every unmatched
  question, including open-ended chit-chat (e.g. "tell me something
  interesting about mountain biking" — tested manually, see
  `outputs/final_examples.md`). In that specific case the result was actually
  a real, cited fact rather than a worse outcome, but it's still strictly more
  latency and Ollama load per unmatched question than the old
  instant-clarification path, and a genuinely nonsensical or adversarial input
  would pay that same cost for no benefit.
