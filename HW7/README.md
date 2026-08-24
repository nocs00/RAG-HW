# HW7 — Porting the Agentic Workflow to a Framework

## Subject Area

Mountain Bike Technical Assistant — same chatbot as HW1–6. HW7 takes HW6's custom,
hand-rolled agentic workflow (a Python function threading a dict through if/elif
branches) and re-implements it, **unchanged in behavior**, on top of **LangGraph**:
explicit `State`, `Nodes`, and `Edges` instead of a single function body.

**Framework chosen: LangGraph.**
Reasons:
- HW6's workflow is already, conceptually, a small state machine (`route → tool
  call → observation → answer`) — LangGraph models exactly that: a typed `State`
  passed between named `Nodes`, connected by `Edges`, with `conditional_edges` for
  branching. The mapping from HW6's code to a LangGraph graph is close to 1:1.
- It's already installed in this project's `venv` (`langgraph==1.2.9`), needs no
  new service or account (unlike CrewAI/LlamaIndex Workflow's heavier
  dependency footprints for a graph this small).
- It keeps routing deterministic and inspectable (`app.get_graph()` /
  `state["selected_route"]`) rather than delegating routing to an LLM-driven
  agent loop, which matches HW6's explicit "no LLM in routing" requirement.

---

## What changed vs. HW6

Nothing at the **behavior** level. `scripts/langgraph_flow.py` imports HW6's
`select_route`, `extract_*_slots`, `TOOLS`, `TOOL_NAMES`, `ANSWER_SYNTHESIZERS`,
and `CLARIFICATION_MESSAGE` **verbatim** (`import agent_flow as hw6`) — same
keyword tables, same tools (`get_trail_weather`, `search_part_manual`,
`search_knowledge_base`, reused unchanged from HW5/HW4), same answer templates.
Only the **control-flow representation** changes: HW6's `if route == "...":`
branches become LangGraph nodes wired with one conditional edge.

---

## State

```python
class AgentState(TypedDict):
    user_question: str
    selected_route: Optional[str]
    extracted_slots: Optional[dict]
    tool_calls: List[dict]
    observations: List[dict]
    final_answer: Optional[str]
```

Identical fields to HW6's plain dict, now given a `TypedDict` shape so LangGraph
can validate and thread it between nodes.

---

## Nodes

| Node | Behavior |
|---|---|
| `classify_request` | Router — calls HW6's `select_route()`, sets `selected_route`. No LLM. |
| `weather_workflow` | Extracts `{location, days_ahead}`, calls `get_trail_weather`, synthesizes a templated weather answer. |
| `part_manual_workflow` | Extracts `{query, max_results}`, calls `search_part_manual`, synthesizes a "here's what I found" answer. |
| `knowledge_base_workflow` | Extracts `{query}`, calls `search_knowledge_base` (wraps HW4's grounded RAG pipeline), relays its already-cited answer. |
| `clarification` | No tool call — asks the rider to pick a category. |

That's 5 nodes total (1 router + 4 terminal workflow nodes) — above the
assignment's 2–4 minimum.

---

## Edges

```
classify_request
    ├─[conditional, on selected_route]─→ weather_workflow          → END
    ├─[conditional, on selected_route]─→ part_manual_workflow       → END
    ├─[conditional, on selected_route]─→ knowledge_base_workflow    → END
    └─[conditional, on selected_route]─→ clarification              → END
```

One `add_conditional_edges("classify_request", route_decision, {...})` call
fans out to all four route nodes based on `state["selected_route"]`; each route
node has a plain edge straight to `END`.

---

## Repository Structure

```
HW7/
├── HW7_Framework_Workflow.md      # assignment spec
├── scripts/
│   └── langgraph_flow.py          # State, Nodes, Edges, graph build + CLI
├── outputs/
│   └── langgraph_examples.md      # 4 traced examples (route → nodes → state → answer)
└── README.md
```

Reuses `HW6/scripts/agent_flow.py` (router, slot extraction, tools, answer
templates) and, transitively, `HW5/scripts/external_tool.py`'s tool
implementations and HW4's grounded-RAG `search_knowledge_base` wrapper —
unchanged.

---

## Usage

```bash
# Run all 4 test cases through the LangGraph app, save outputs/langgraph_examples.md
venv/bin/python HW7/scripts/langgraph_flow.py

# Run a single question and print the full final state as JSON
venv/bin/python HW7/scripts/langgraph_flow.py --ask "How do I set sag on my mountain bike fork?"
```

---

## Test Examples

Full trace: [`outputs/langgraph_examples.md`](outputs/langgraph_examples.md)

| Question | Route | Nodes executed |
|---|---|---|
| "Is it a good day to ride the trails in Queenstown, New Zealand today?" | `weather_workflow` | `classify_request → weather_workflow` |
| "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?" | `part_manual_workflow` | `classify_request → part_manual_workflow` |
| "How do I set sag on my mountain bike fork?" | `knowledge_base_workflow` | `classify_request → knowledge_base_workflow` |
| "Tell me something interesting about mountain biking." | `clarification` | `classify_request → clarification` |

All 4 ran live against the real tools (Open-Meteo weather API, DuckDuckGo web
lookup, HW2's FAISS index + HW3's reranker + HW4's local-LLM grounded answer)
and produced the same routes and answers HW6's custom flow would produce for
the same inputs, confirming the port preserved behavior exactly.

---

## Comparison: custom flow (HW6) vs. LangGraph (HW7)

| Aspect | Custom flow (HW6) | LangGraph (HW7) |
|---|---|---|
| Code volume | ~1 function, compact | More boilerplate: `TypedDict`, node functions, explicit graph wiring — roughly 2x the lines for the same logic |
| Workflow visibility | Implicit — have to read the `if/elif` chain to see the shape | Explicit — the node/edge wiring in `build_graph()` *is* a readable diagram of the workflow |
| State handling | Plain dict, mutated by convention | `TypedDict` gives a typed contract per field, though LangGraph still just merges whatever a node returns — no extra runtime safety over HW6's dict for a graph this simple |
| Conditional routing | One `if/elif` in `run_agent()` | `add_conditional_edges` + a `route_decision` function — same logic, one more layer of indirection |
| Debugging | `print`/`json.dumps(state)` at any point | Same, plus LangGraph's `app.get_graph()` can render/introspect the compiled graph structure itself |
| Extending with new routes | Add an `elif` branch | Add a node + one dict entry in the conditional-edges mapping — slightly more ceremony but harder to break existing routes by accident |
| Verdict for *this* workflow's size (1 router + 4 terminal branches, no loops, no parallel branches) | Sufficient on its own | Framework overhead isn't "paid for" yet at this scale — it would start winning if branches needed to loop back, run in parallel, or share checkpointing/persistence across turns |

**Conclusion**: for a workflow this small — one router, no cycles, no
parallel branches — LangGraph adds structure and self-documentation
(the graph wiring literally states the shape of the workflow) at the cost of
more boilerplate than HW6's plain function needed. The framework would start
paying for itself if the workflow grew multi-turn state, retries/loops, or
concurrent tool calls — none of which this use case currently needs.
