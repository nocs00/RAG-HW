# HW5 — External Tool Integration

## Subject Area

Mountain Bike Technical Assistant — extends the HW1–4 pipeline with **two external tools**: a **live weather/trail-conditions API tool** and a **web-lookup tool for specific part/product manuals**, so the assistant can answer questions a static knowledge base can never cover — either because the data is inherently live (weather), or because it's an ever-growing long-tail catalog (every part model any manufacturer has ever released).

---

## Pipeline

```
User question
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Orchestration layer (local LLM, native tool-use)            │
│  Decides which of three tools to call, or answers directly   │
└─────────────────────────────────────────────────────────────┘
    ↓                        ↓                        ↓
get_trail_weather      search_part_manual       search_knowledge_base
(API tool —            (web lookup tool —       (HW4 RAG pipeline —
graded)                graded)                  comparison baseline,
Open-Meteo API         DuckDuckGo web search     not a graded tool)
    ↓                        ↓                        ↓
┌─────────────────────────────────────────────────────────────┐
│  Validation (Pydantic contract)                               │
│  required fields, format/range, unknown-tool rejection,       │
│  no raw SQL/shell from model input                             │
└─────────────────────────────────────────────────────────────┘
    ↓
External source (Open-Meteo / DuckDuckGo) or HW1-4 index
    ↓
Normalized result (dict) → back to LLM → final answer
```

`chatbot → tool request → validation → external source → normalized result → answer`, exactly as required.

---

## Repository Structure

```
HW5/
├── scripts/
│   └── external_tool.py        # tool impls, Pydantic contracts, validation, orchestration
├── outputs/
│   └── tool_examples.md        # 8 examples in the required format
└── README.md
```

Reuses `HW2/index/faiss.index`, `HW3/scripts/retrieval_improved.py`, and `HW4/scripts/rag_answer.py` for the comparison tool — no retrieval logic is reimplemented.

---

## Tools

### 1. `get_trail_weather` — API tool

| | |
|---|---|
| **Type** | Read tool (API tool variant) — no side effects, no confirmation step needed |
| **Source** | [Open-Meteo](https://open-meteo.com) — free geocoding + forecast API, no API key required |
| **Purpose** | Returns current or forecast weather (temperature, precipitation, wind, a plain-language riding-conditions note) for a location |
| **When to call** | Any question about current weather, forecast, rain, wind, or "is it good to ride today/this weekend" |
| **When NOT to call** | Static how-to/maintenance questions, or specific part-model lookups |

### 2. `search_part_manual` — Web lookup tool

| | |
|---|---|
| **Type** | Read tool (web lookup variant) — no side effects |
| **Source** | DuckDuckGo web search via the free `ddgs` package, no API key required |
| **Purpose** | Finds the official manual, spec sheet, or spare-parts catalog page for a **specific named part/product model** |
| **When to call** | User names a specific brand + model (e.g. "RockShox Pike Ultimate 2023 service manual", "SRAM GX Eagle spare parts catalog") that is very unlikely to be pre-chunked in the KB |
| **When NOT to call** | General MTB concepts already in the KB, or weather questions |

### 3. `search_knowledge_base` — comparison baseline (not graded)

Wraps HW4's grounded RAG pipeline unchanged. Included only so the orchestrator's tool-choice can be demonstrated concretely across three real options instead of two, and so "when a tool beats retrieval" can be shown by contrast (case-3 below: the router correctly picks *this* over the other two for a generic how-to question).

---

## Input / Output Contracts

### `get_trail_weather`

```python
class TrailWeatherInput(BaseModel):
    location: str        # required — city/region, ideally with country, e.g. "Queenstown, New Zealand"
    days_ahead: int = 0  # 0 = today, 1-7 = forecast day N days ahead
```

```json
{
  "location": "Queenstown, New Zealand",
  "resolved_place": "Queenstown, New Zealand",
  "coordinates": {"lat": -45.03023, "lon": 168.6627},
  "date": "2026-08-16",
  "temperature_max_c": 7.4,
  "temperature_min_c": 0.3,
  "precipitation_mm": 0.0,
  "wind_speed_max_kmh": 2.6,
  "weather_description": "Overcast",
  "riding_conditions_note": "Good riding conditions expected."
}
```

```bash
venv/bin/python HW5/scripts/external_tool.py --direct '{"location": "Queenstown, New Zealand", "days_ahead": 0}'
```

### `search_part_manual`

```python
class SearchPartManualInput(BaseModel):
    query: str            # required — part/product model + what's needed, e.g. "Fox 36 Factory 2024 service manual"
    max_results: int = 3  # 1-5
```

```json
{
  "query": "RockShox Pike Ultimate 2023 service manual",
  "results": [
    {"title": "Pike Ultimate | FS-PIKE-ULT-C1 | RockShox | Service - SRAM",
     "url": "https://www.sram.com/en/service/models/fs-pike-ult-c1",
     "snippet": "Manuals & Documents · User Manual · Service Manuals · Spare Parts Catalog..."}
  ]
}
```

```bash
venv/bin/python HW5/scripts/external_tool.py --tool search_part_manual --direct '{"query": "RockShox Pike Ultimate 2023 service manual", "max_results": 2}'
```

On any failure (bad input, unresolvable location, no web results, network error): `{"error": "<message>"}` — never a crash or a partial/malformed result, for either tool.

---

## Validation

Implemented in `validate_input()`, run **before** any network call, for both graded tools:

| Check | How |
|---|---|
| Required fields present | Pydantic raises `Field required` if `location`/`query` is missing |
| Format/range correct | `location`: non-empty, ≤100 chars, restricted character set (rejects e.g. `Queenstown; DROP TABLE trails;--`) · `days_ahead`: `0–7` · `query` (web lookup): non-empty, ≤200 chars · `max_results`: `1–5` |
| Unknown tool name rejected | `validate_input` looks up the tool in a fixed registry — a hallucinated tool name fails validation instead of being called |
| No raw SQL / shell / file path from model input | N/A by design — all string fields are only ever passed as `requests`/`ddgs` query parameters (auto-escaped) or into the existing HW4 retrieval function; nothing is interpolated into a command, path, or query string |
| Write-action confirmation | N/A — all three tools are read-only; documented explicitly rather than silently skipped |

Direct validation tests (no LLM, no network needed):

```bash
venv/bin/python HW5/scripts/external_tool.py --direct '{}'
# {"error": "Field required"}

venv/bin/python HW5/scripts/external_tool.py --direct '{"location": "Queenstown, New Zealand", "days_ahead": 14}'
# {"error": "Value error, days_ahead must be between 0 and 7 ..."}

venv/bin/python HW5/scripts/external_tool.py --direct '{"location": "Queenstown; DROP TABLE trails;--"}'
# {"error": "Value error, location contains invalid characters"}

venv/bin/python HW5/scripts/external_tool.py --tool search_part_manual --direct '{"query": "test", "max_results": 10}'
# {"error": "Value error, max_results must be between 1 and 5"}

venv/bin/python HW5/scripts/external_tool.py --tool search_part_manual --direct '{"query": ""}'
# {"error": "Value error, query is required and cannot be empty"}
```

---

## Model / Orchestration

| Component | Model / Method |
|-----------|-----------------|
| Orchestration LLM | `llama3.1:8b` via [Ollama](https://ollama.com), local, free — native tool-calling (`tools` param on `/api/chat`) |
| Weather source | Open-Meteo geocoding + forecast API (free, no key) |
| Web lookup source | DuckDuckGo web search via `ddgs` (free, no key) |
| Comparison tool | HW4's grounded RAG pipeline (FAISS + cross-encoder reranker + local LLM) |

The orchestrator is given all three tool schemas and picks between them per question (see `ORCHESTRATOR_SYSTEM_PROMPT` in the script) — this is what satisfies "demonstrate the call through the orchestration layer": the routing decision is made by the model across three real options, not hardcoded per question.

---

## Usage

```bash
# Run all 8 test cases through the orchestration layer, save outputs/tool_examples.md
venv/bin/python HW5/scripts/external_tool.py

# Ask a single question through the orchestrator
venv/bin/python HW5/scripts/external_tool.py --ask "Where can I find the manual for a SRAM GX Eagle derailleur?"

# Call a tool directly, bypassing the LLM entirely (for validation testing)
venv/bin/python HW5/scripts/external_tool.py --tool get_trail_weather --direct '{"location": "Rotorua, New Zealand", "days_ahead": 2}'
venv/bin/python HW5/scripts/external_tool.py --tool search_part_manual --direct '{"query": "Shimano XT M8100 crankset manual"}'
```

---

## Results

Full output: [`outputs/tool_examples.md`](outputs/tool_examples.md)

| Case | What it shows |
|---|---|
| case-1-current-weather | Correct `get_trail_weather` call for "today", accurate live conditions relayed |
| case-2-forecast | Correct call with `days_ahead=3`, demonstrates forecast (not just current) capability |
| case-3-static-question | Orchestrator correctly picks `search_knowledge_base` over both other tools — the HW4 grounded answer is relayed verbatim, citations intact |
| case-4-out-of-range-forecast | Model asks for a 14-day forecast → validation rejects `days_ahead=14` before any network call → model relays the limitation honestly |
| case-5-unresolvable-location | Geocoding fails for a nonexistent place → tool returns a structured error → model relays it honestly instead of inventing a forecast |
| case-6-part-manual-lookup | Correct `search_part_manual` call for a specific fork model → real official SRAM manual URLs returned and relayed |
| case-7-part-manual-different-model | Same tool, different product category (derailleur) — the KB has zero drivetrain source documents at all, making this an unambiguous "must use web lookup" case |
| case-8-part-manual-validation | User's "just give me 1 result" phrasing maps to `max_results=1` inside the `1–5` contract — validation passes and the search runs with the requested limit |

### Why the tools are better than retrieval (summary)

**Weather** is live, hourly-changing data with no fixed "true" value to index — the opposite of everything HW1's knowledge base contains (suspension manuals, maintenance guides, trail descriptions), which are static and correct indefinitely once chunked. No amount of re-embedding or reranking (HW2/HW3) or better prompting (HW4) can make a snapshot answer "is it raining right now."

**Specific part manuals** fail retrieval for a different reason: it's not that the data changes fast, it's that the *catalog is unbounded*. HW1's KB was chunked from a handful of documents about specific components; a real assistant will get asked about parts that were never in it, and manufacturers keep releasing new ones. Re-indexing the entire internet's worth of SRAM/Shimano/Fox manuals into a vector store isn't a retrieval fix — a live web search is the only approach that scales.

Case-3 shows the reverse also holds: a general how-to question is answered *better* by the existing grounded RAG pipeline than by either external tool — which is exactly why the orchestrator's job is to route between three options, not prefer one path universally.

---

## Conclusion

All 8 cases behaved correctly: the three tools are cleanly separated by purpose and the model's routing choice matched the intended one in every case, including correctly distinguishing "generic MTB knowledge" from "specific product model" — two categories that sound similar but need different tools. Both graded tools' validation paths were exercised for real: an out-of-contract `days_ahead=14` and an out-of-contract `max_results=10`/empty `query` were all rejected before any network call, and a genuine external-source failure (unresolvable location) was handled gracefully. The one real fragility observed: `llama3.1:8b`'s tool-argument extraction occasionally emits numeric fields as strings (e.g. `"days_ahead": "3"`, `"max_results": "1"`) rather than integers — Pydantic's default coercion absorbed this without issue here, but a stricter schema (`strict=True`) would surface it as a validation error instead, worth knowing if swapping to a smaller/less capable local model.
