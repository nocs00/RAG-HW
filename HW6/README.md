# HW6 — First Agentic Structure

## Subject Area

Mountain Bike Technical Assistant — same chatbot as HW1–5. HW6 replaces HW5's LLM-based
tool orchestration with a small, controlled **agentic workflow**: a deterministic,
rule-based router decides which specialist workflow handles the question, calls the
matching tool, updates a shared state object, and synthesizes a final answer — no LLM
call is used for the routing decision itself.

**Use case**: a rider sends one message to the assistant. Depending on what it's about
— live riding conditions, a specific part's official manual, or a general how-to/
maintenance question — the workflow must route to a different specialist path and end
up with a grounded answer, or ask the rider to clarify if the question matches none of
the known categories.

---

## Workflow Schema

```
User question
    ↓
Router (keyword rules, no LLM)
    ↓
    ├─ [route A] weather_workflow
    │      → extract {location, days_ahead}
    │      → tool: get_trail_weather
    │      → observation (live forecast or {"error": ...})
    │      → template answer ("Weather for X on Y: ...")
    │
    ├─ [route B] part_manual_workflow
    │      → extract {query, max_results}
    │      → tool: search_part_manual
    │      → observation (web results or {"error": ...})
    │      → template answer ("Here's what I found: ...")
    │
    ├─ [route C] knowledge_base_workflow
    │      → extract {query}
    │      → tool: search_knowledge_base (wraps HW4's grounded RAG pipeline)
    │      → observation ({"answer": ..., "chunk_ids": ..., "sources": ...})
    │      → answer = observation["answer"] (already grounded + cited)
    │
    └─ [route D] clarification
           → ask the user which category their question falls into
    ↓
state updated at every step → final answer returned
```

`user goal → route (rule-based) → action (tool call) → observation → state update →
next step (answer synthesis) → final answer`, exactly the loop this assignment asks for.

---

## Repository Structure

```
HW6/
├── scripts/
│   └── agent_flow.py            # router, slot extraction, tool dispatch, state, answer synthesis
├── outputs/
│   └── agent_flow_examples.md   # 5 examples in the required trace format
└── README.md
```

Reuses `HW5/scripts/external_tool.py`'s tool implementations (`get_trail_weather`,
`search_part_manual`, `search_knowledge_base` — the last of which wraps HW2's FAISS
index, HW3's reranker, and HW4's grounded-answer LLM call) unchanged. HW6 adds nothing
new at the tool level; the only new logic is the deterministic router, slot extraction,
state object, and answer-synthesis templates around those tools.

---

## Routes

| Route | Trigger keywords (first match wins, checked in this order) | Tool called |
|---|---|---|
| `weather_workflow` | weather, forecast, rain, wind(y), temperature, "ride today/this weekend", "riding conditions" | `get_trail_weather` |
| `part_manual_workflow` | manual, spec sheet, spare parts, parts catalog, catalog, installation instructions, datasheet, service manual | `search_part_manual` |
| `knowledge_base_workflow` | how do i / how to, sag, bleed, adjust, set up/setup, maintenance, install, tighten, clean, lube, grease | `search_knowledge_base` |
| `clarification` | none of the above matched | *(none — asks the user)* |

Routing is pure `if/elif` string matching (`select_route()` in `agent_flow.py`) — no LLM
call, no embeddings, evaluated in the fixed priority order above so an ambiguous
question (e.g. one that could sound like both weather and maintenance) resolves
deterministically every time.

---

## Tools

### 1. `get_trail_weather` (reused from HW5)
Live/forecast weather + a riding-conditions note for a location, from the free
Open-Meteo API. Returns `{"error": "..."}` on an unresolvable location or out-of-range
`days_ahead` — never a crash.

### 2. `search_part_manual` (reused from HW5)
Web lookup (DuckDuckGo via `ddgs`) for the official manual/spec sheet/spare-parts page
of a specific named part or product model. Returns `{"error": "..."}` if nothing is
found.

### 3. `search_knowledge_base` (reused from HW5, wrapping HW4)
Grounded, cited answer from the static HW1 knowledge base via HW2's FAISS retrieval,
HW3's cross-encoder reranker, and HW4's grounded-prompt LLM call. This is the one place
an LLM is involved anywhere in the workflow — inside the reused tool, generating the
grounded answer text itself, not deciding which tool to call.

All three tools satisfy the "≥2 tools with a fixed contract" requirement; none require
extra mocking since they already return a deterministic, structured result (data or a
structured error) for a given input.

---

## State

Tracked in a single dict threaded through every step of `run_agent()`:

```python
state = {
    "user_question": str,
    "selected_route": str,          # one of the 4 routes above
    "extracted_slots": dict | None, # tool input, filled after routing (None for clarification)
    "tool_calls": list[dict],       # [{"tool": name, "input": {...}}]
    "observations": list[dict],     # raw tool result(s)
    "final_answer": str,
}
```

Each step only ever *adds* to `state` — the router never re-decides once
`selected_route` is set, and the answer-synthesis step reads only from
`observations`, never re-calling a tool. This is what "the workflow remembers previous
steps" means here: by the time `final_answer` is produced, `state` is a complete,
inspectable trace of everything that happened.

---

## Usage

```bash
# Run all 5 test cases through the workflow, save outputs/agent_flow_examples.md
venv/bin/python HW6/scripts/agent_flow.py

# Run a single question and print the full state as JSON
venv/bin/python HW6/scripts/agent_flow.py --ask "What's the forecast for Rotorua, New Zealand 3 days from now?"
```

---

## Results

Full output: [`outputs/agent_flow_examples.md`](outputs/agent_flow_examples.md)

| Question | Route | What it shows |
|---|---|---|
| "Is it a good day to ride the trails in Queenstown, New Zealand today?" | `weather_workflow` | Location/day extraction + live weather tool + templated answer |
| "What's the forecast for Rotorua, New Zealand 3 days from now?" | `weather_workflow` | `days_ahead=3` slot correctly parsed from "3 days from now" |
| "How do I set sag on my mountain bike fork?" | `knowledge_base_workflow` | Router picks the KB path; HW4's grounded, cited answer is relayed as-is |
| "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?" | `part_manual_workflow` | Router correctly avoids the KB path (this exact product isn't in HW1's KB) in favor of the web-lookup tool |
| "Tell me something interesting about mountain biking." | `clarification` | No keyword matches any route → the workflow asks the user to narrow down the question instead of guessing |

---

## Conclusion

All 5 cases routed correctly and deterministically through `select_route()` with no
LLM involved in the decision — the same keyword table produces the same route for the
same input every time, unlike HW5's LLM-orchestrated tool choice. The state object
gives a complete, inspectable trace (route → slots → tool call → observation → answer)
for every question, including the clarification path where no tool is called at all.
One real limitation surfaced during testing: the regex-based location extractor
initially swallowed trailing words like "today" into the location string ("Queenstown,
New Zealand today"), breaking geocoding — fixed by stripping a fixed set of trailing
time-words after extraction. This is the expected trade-off of rule-based slot
extraction versus an LLM: fast and fully deterministic, but only as robust as the
patterns it's given.
