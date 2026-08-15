"""
HW5 — External tool integration.

Graded tool: get_trail_weather — an API tool that fetches live/forecast weather
conditions from Open-Meteo (free, no API key) to support ride-day decisions.
Weather is dynamic data that changes hour to hour: it can never be pre-indexed
into a static knowledge base the way HW1-4's chunks are, which is exactly the
case where a tool beats retrieval.

A second, minimal tool (search_knowledge_base) wraps HW4's grounded RAG
pipeline. It exists only as a side-by-side comparison so the orchestration
layer's tool-vs-retrieval routing decision is demonstrated concretely, not
just asserted in prose — it is not the graded external tool.

Pipeline: chatbot -> tool request -> validation -> external source -> normalized result -> answer

Usage:
    python HW5/scripts/external_tool.py                 # run all test cases, save outputs/tool_examples.md
    python HW5/scripts/external_tool.py --ask "..."      # ask a single question through the orchestration layer
    python HW5/scripts/external_tool.py --direct '{"location": "Queenstown, New Zealand"}'  # call the tool directly, no LLM
"""

import argparse
import json
import re
import sys
from io import TextIOBase
from pathlib import Path
from typing import Optional

import requests
from pydantic import BaseModel, ValidationError, field_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
EXAMPLES_FILE = OUTPUT_DIR / "tool_examples.md"

sys.path.insert(0, str(REPO_ROOT / "HW4" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW3" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW2" / "scripts"))
import rag_answer  # noqa: E402 — HW4's retrieval + grounded prompt + local LLM call

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


class _Tee(TextIOBase):
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


# ---------------------------------------------------------------------------
# Input / Output contracts
# ---------------------------------------------------------------------------

class TrailWeatherInput(BaseModel):
    """Input contract for get_trail_weather."""
    location: str
    days_ahead: int = 0

    @field_validator("location")
    @classmethod
    def location_must_be_reasonable(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("location is required and cannot be empty")
        if len(v) > 100:
            raise ValueError("location must be under 100 characters")
        if not re.match(r"^[A-Za-z0-9\s,.\-']+$", v):
            raise ValueError("location contains invalid characters")
        return v

    @field_validator("days_ahead")
    @classmethod
    def days_ahead_in_range(cls, v: int) -> int:
        if not (0 <= v <= 7):
            raise ValueError("days_ahead must be between 0 and 7 (Open-Meteo daily forecast horizon used here)")
        return v


class SearchKnowledgeBaseInput(BaseModel):
    """Input contract for the comparison tool, search_knowledge_base."""
    query: str

    @field_validator("query")
    @classmethod
    def query_must_be_reasonable(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("query is required and cannot be empty")
        if len(v) > 300:
            raise ValueError("query must be under 300 characters")
        return v


class SearchPartManualInput(BaseModel):
    """Input contract for search_part_manual."""
    query: str
    max_results: int = 3

    @field_validator("query")
    @classmethod
    def query_must_be_reasonable(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("query is required and cannot be empty")
        if len(v) > 200:
            raise ValueError("query must be under 200 characters")
        return v

    @field_validator("max_results")
    @classmethod
    def max_results_in_range(cls, v: int) -> int:
        if not (1 <= v <= 5):
            raise ValueError("max_results must be between 1 and 5")
        return v


VALIDATORS = {
    "get_trail_weather": TrailWeatherInput,
    "search_knowledge_base": SearchKnowledgeBaseInput,
    "search_part_manual": SearchPartManualInput,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_trail_weather",
            "description": (
                "Get current or forecast weather conditions (temperature, precipitation, wind) for a "
                "location, to help decide whether trail/riding conditions are safe today or on an "
                "upcoming day. Use this for ANY question about current weather, forecast, rain, wind, "
                "or 'is it good to ride today/this weekend'. Do NOT use this for static how-to or "
                "maintenance questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City/region name, ideally with country, e.g. 'Queenstown, New Zealand'",
                    },
                    "days_ahead": {
                        "type": "integer",
                        "description": "0 for today, 1-7 for a forecast day that many days ahead",
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Search the static mountain-bike knowledge base (suspension setup, maintenance, "
                "assembly, component specs, trail catalogue) for a grounded, cited answer. Use this "
                "for general how-to, maintenance, setup, or 'what is X' questions covered by common "
                "MTB knowledge. Do NOT use this for weather/forecast questions, and do NOT use this "
                "for a SPECIFIC part/product model's official manual or spec sheet -- use "
                "search_part_manual for that instead."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The user's question, verbatim or lightly cleaned up"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_part_manual",
            "description": (
                "Search the public web for the official manual, spec sheet, or documentation page "
                "for a SPECIFIC named part/product model (e.g. 'RockShox Pike Ultimate 2023 service "
                "manual', 'SRAM GX Eagle rear derailleur spare parts catalog'). Use this when the user "
                "names a specific brand + model that is unlikely to be in the static knowledge base -- "
                "new/different products, exact service manuals, spare parts catalogs. Do NOT use this "
                "for general MTB concepts already covered by search_knowledge_base, and do NOT use this "
                "for weather questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The part/product model and what's needed, e.g. 'Fox 36 Factory 2024 service manual PDF'",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of web results to return, 1-5 (default 3)",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_input(tool_name: str, raw_args: dict) -> tuple[Optional[BaseModel], Optional[str]]:
    """
    Validate raw tool-call arguments against the tool's contract before touching any
    external source. Returns (validated_input, None) on success, (None, error) on failure.

    Checks performed:
    - the tool name is known (reject anything the model hallucinates)
    - all required fields are present
    - field formats/ranges are correct (Pydantic validators above)
    - no raw SQL, shell command, or file path is ever built from model input -- both
      tools only ever pass validated, typed fields to `requests` as query parameters
      (auto URL-encoded) or to the existing HW4 retrieval function; nothing is
      interpolated into a command string or executed
    - both tools are read-only (no writes/side effects), so no write-confirmation
      step is required -- this is a deliberate N/A, not a skipped check
    """
    model_cls = VALIDATORS.get(tool_name)
    if model_cls is None:
        return None, f"Unknown tool: {tool_name}"
    try:
        return model_cls(**raw_args), None
    except ValidationError as e:
        return None, "; ".join(err["msg"] for err in e.errors())


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def get_trail_weather(location: str, days_ahead: int = 0) -> dict:
    """
    Tool: get_trail_weather
    Type: read tool (no side effects)
    Source: Open-Meteo geocoding + forecast API (free, no key required)
    Purpose: returns live/forecast weather for a location to support ride-day decisions.
    When useful: current conditions, forecast, "is it safe to ride today/this weekend".
    When NOT useful: static how-to/maintenance questions -- use search_knowledge_base instead.
    """
    validated, error = validate_input("get_trail_weather", {"location": location, "days_ahead": days_ahead})
    if error:
        return {"error": error}

    try:
        geo_resp = requests.get(
            GEOCODE_URL,
            params={"name": validated.location, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        geo_resp.raise_for_status()
        results = geo_resp.json().get("results")
        if not results:
            return {"error": f"Could not resolve location: '{validated.location}'"}

        place = results[0]
        lat, lon = place["latitude"], place["longitude"]

        forecast_resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weather_code",
                "timezone": "auto",
                "forecast_days": max(validated.days_ahead + 1, 1),
            },
            timeout=10,
        )
        forecast_resp.raise_for_status()
        daily = forecast_resp.json()["daily"]
        idx = validated.days_ahead

        code = daily["weather_code"][idx]
        precip = daily["precipitation_sum"][idx]
        wind = daily["wind_speed_10m_max"][idx]

        note = "Good riding conditions expected."
        if precip > 5:
            note = "Rain expected -- trails may be muddy/slippery, consider rescheduling."
        elif precip > 0:
            note = "Light rain possible -- trails may be damp."
        if wind > 40:
            note += " High wind -- use caution on exposed sections."

        return {
            "location": validated.location,
            "resolved_place": f"{place['name']}, {place.get('country', 'unknown')}",
            "coordinates": {"lat": lat, "lon": lon},
            "date": daily["time"][idx],
            "temperature_max_c": daily["temperature_2m_max"][idx],
            "temperature_min_c": daily["temperature_2m_min"][idx],
            "precipitation_mm": precip,
            "wind_speed_max_kmh": wind,
            "weather_description": WMO_CODES.get(code, f"Unknown code {code}"),
            "riding_conditions_note": note,
        }
    except requests.RequestException as e:
        return {"error": f"Weather service unavailable: {e}"}


_HW4_RESOURCES = {}


def _hw4_resources():
    if not _HW4_RESOURCES:
        index, model, chunks_meta = rag_answer.retrieval.load_resources()
        reranker = rag_answer.retrieval.load_reranker()
        _HW4_RESOURCES.update(index=index, model=model, chunks_meta=chunks_meta, reranker=reranker)
    return _HW4_RESOURCES


def search_knowledge_base(query: str) -> dict:
    """
    Tool: search_knowledge_base (comparison baseline, not the graded HW5 tool)
    Type: read tool
    Purpose: grounded, cited answer from the static HW1-4 knowledge base.
    """
    validated, error = validate_input("search_knowledge_base", {"query": query})
    if error:
        return {"error": error}

    res = _hw4_resources()
    metas, scores, texts = rag_answer.retrieve(
        validated.query, rag_answer.RETRIEVAL_K, res["index"], res["model"], res["chunks_meta"], res["reranker"]
    )
    context = rag_answer.build_context(metas, scores, texts)
    answer = rag_answer.call_llm(
        rag_answer.GROUNDED_SYSTEM_PROMPT,
        rag_answer.USER_TEMPLATE.format(context=context, question=validated.query),
    )
    return {
        "answer": answer,
        "chunk_ids": [m["chunk_id"] for m in metas],
        "sources": sorted(set(m["source_file"] for m in metas)),
    }


def search_part_manual(query: str, max_results: int = 3) -> dict:
    """
    Tool: search_part_manual
    Type: read tool (web lookup)
    Source: DuckDuckGo web search (free, no API key, via the `ddgs` package)
    Purpose: find the official manual/spec sheet/spare-parts page for a specific named
             part or product model -- something the static knowledge base was never
             chunked to contain, and that changes as manufacturers release new models.
    When useful: user names a specific brand + model (e.g. "RockShox Pike Ultimate 2023
                 service manual", "SRAM GX Eagle rear derailleur spare parts catalog").
    When NOT useful: general MTB concepts -> search_knowledge_base; weather -> get_trail_weather.
    """
    validated, error = validate_input("search_part_manual", {"query": query, "max_results": max_results})
    if error:
        return {"error": error}

    try:
        from ddgs import DDGS

        raw_results = DDGS().text(validated.query, max_results=validated.max_results)
        results = [
            {"title": r.get("title"), "url": r.get("href"), "snippet": r.get("body")}
            for r in raw_results
        ]
        if not results:
            return {"error": f"No web results found for '{validated.query}'"}
        return {"query": validated.query, "results": results}
    except Exception as e:
        return {"error": f"Web search failed: {e}"}


TOOLS = {
    "get_trail_weather": get_trail_weather,
    "search_knowledge_base": search_knowledge_base,
    "search_part_manual": search_part_manual,
}


# ---------------------------------------------------------------------------
# Orchestration layer -- local LLM decides whether/which tool to call
# ---------------------------------------------------------------------------

ORCHESTRATOR_SYSTEM_PROMPT = (
    "You are a Mountain Bike Technical Assistant with three tools available: "
    "get_trail_weather (live/forecast weather), search_knowledge_base (static general MTB "
    "how-to/maintenance knowledge), and search_part_manual (web lookup for a SPECIFIC named "
    "part/product model's official manual or spec sheet). Pick the right tool for the "
    "question, or answer directly if none applies. Never invent tool arguments the user "
    "didn't imply."
)


def call_llm_raw(messages: list, tools: list | None = None) -> dict:
    payload = {"model": MODEL_NAME, "messages": messages, "stream": False, "options": {"temperature": 0.0}}
    if tools:
        payload["tools"] = tools
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]


def answer_with_tools(user_question: str) -> dict:
    """chatbot -> tool request -> validation -> external source -> normalized result -> answer"""
    messages = [
        {"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
    ]
    first = call_llm_raw(messages, tools=TOOL_SCHEMAS)

    tool_calls = first.get("tool_calls") or []
    if not tool_calls:
        return {
            "tool_called": None,
            "tool_input": None,
            "tool_result": None,
            "final_answer": (first.get("content") or "").strip(),
        }

    call = tool_calls[0]["function"]
    tool_name = call["name"]
    tool_args = call["arguments"]

    validated, error = validate_input(tool_name, tool_args)
    if error:
        tool_result = {"error": error}
    else:
        tool_fn = TOOLS.get(tool_name)
        tool_result = tool_fn(**tool_args) if tool_fn else {"error": f"Unknown tool: {tool_name}"}

    # search_knowledge_base already runs HW4's full grounded-answer pipeline internally
    # (retrieval -> grounded prompt -> LLM), so its "answer" field IS the final answer.
    # Re-synthesizing it through a second orchestrator call only risks the model
    # summarizing/describing the tool call instead of relaying the actual content.
    if tool_name == "search_knowledge_base" and "error" not in tool_result:
        return {
            "tool_called": tool_name,
            "tool_input": tool_args,
            "tool_result": tool_result,
            "final_answer": tool_result["answer"],
        }

    messages.append({"role": "assistant", "content": "", "tool_calls": tool_calls})
    messages.append({"role": "tool", "content": json.dumps(tool_result)})
    final = call_llm_raw(messages)

    return {
        "tool_called": tool_name,
        "tool_input": tool_args,
        "tool_result": tool_result,
        "final_answer": (final.get("content") or "").strip(),
    }


# ---------------------------------------------------------------------------
# Test cases -- 5 examples covering the required scenarios
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "id": "case-1-current-weather",
        "question": "Is it a good day to ride the trails in Queenstown, New Zealand today?",
        "why": (
            "Weather is live, hourly-changing data. A static knowledge base snapshot would go "
            "stale within hours and could never answer 'today' correctly -- a tool that queries "
            "a live source is the only correct approach."
        ),
    },
    {
        "id": "case-2-forecast",
        "question": "What's the forecast for Rotorua, New Zealand 3 days from now -- should I plan a ride?",
        "why": (
            "This requires a specific future forecast date. Retrieval over static documents has "
            "no concept of 'in 3 days' at all -- there is nothing to retrieve; only a live "
            "forecast API can answer this."
        ),
    },
    {
        "id": "case-3-static-question",
        "question": "How do I set sag on my mountain bike fork?",
        "why": (
            "This is a static how-to question already covered by the HW1-4 knowledge base. "
            "Demonstrates the orchestration layer correctly choosing search_knowledge_base "
            "over get_trail_weather -- the tool is available but not the right one here."
        ),
    },
    {
        "id": "case-4-out-of-range-forecast",
        "question": "What will the weather be like in Queenstown, New Zealand in 2 weeks?",
        "why": (
            "Demonstrates validation rejecting an out-of-contract value: the model naturally "
            "asks for a ~14-day-ahead forecast, which violates the days_ahead <= 7 rule enforced "
            "before any network call is made, rather than silently returning wrong data or crashing "
            "on an out-of-bounds array index."
        ),
    },
    {
        "id": "case-5-unresolvable-location",
        "question": "What's the current weather in Xyzzyplaceville?",
        "why": (
            "Demonstrates graceful handling of a genuine external-source failure (the geocoding "
            "API can't resolve a nonexistent place) -- the tool returns a structured error instead "
            "of crashing, and the model relays that honestly instead of inventing a forecast."
        ),
    },
    {
        "id": "case-6-part-manual-lookup",
        "question": "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?",
        "why": (
            "The knowledge base's suspension chunks are generic setup/maintenance guides -- they "
            "don't (and can't) contain the official per-model service manual for every fork SRAM has "
            "ever sold. A specific product model is exactly the kind of long-tail, ever-growing catalog "
            "that a live web lookup handles and a fixed KB snapshot never will."
        ),
    },
    {
        "id": "case-7-part-manual-different-model",
        "question": "I need the spare parts catalog for a SRAM GX Eagle rear derailleur.",
        "why": (
            "Another specific product model not covered by the ingested documents (HW1's KB has no "
            "drivetrain/derailleur source at all) -- demonstrates the router picking the web-lookup "
            "tool over both other tools for a product the KB was never built to contain."
        ),
    },
    {
        "id": "case-8-part-manual-validation",
        "question": "Find me the installation instructions for a Shimano XT M8100 crankset, just give me 1 result.",
        "why": (
            "Demonstrates the max_results contract in practice: the user's '1 result' phrasing maps "
            "to max_results=1 within the tool's 1-5 range, so validation passes through cleanly and "
            "the search runs with the requested limit instead of a hardcoded default."
        ),
    },
]


def _format_case(case: dict, result: dict) -> None:
    print(f"## {case['id']}\n")
    print(f"User question: {case['question']}\n")
    print(f"Tool called: {result['tool_called'] or '(none — answered directly)'}\n")
    print(f"Input: {json.dumps(result['tool_input']) if result['tool_input'] else 'N/A'}\n")
    print(f"Result: {json.dumps(result['tool_result']) if result['tool_result'] else 'N/A'}\n")
    print(f"Final answer:\n{result['final_answer']}\n")
    print(f"Why tool is better than retrieval:\n{case['why']}\n")
    print("---\n")


def run_all() -> None:
    tee = _Tee(EXAMPLES_FILE)
    sys.stdout = tee
    try:
        print("# HW5 — External Tool Examples\n")
        for case in TEST_CASES:
            result = answer_with_tools(case["question"])
            _format_case(case, result)
    finally:
        sys.stdout = sys.__stdout__
        tee.close()
        print(f"\nOutput saved -> {EXAMPLES_FILE}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="HW5 external tool integration demo")
    parser.add_argument("--ask", type=str, help="Ask a single question through the orchestration layer")
    parser.add_argument("--direct", type=str, help="Call a tool directly with a JSON args string, bypassing the LLM")
    parser.add_argument("--tool", type=str, default="get_trail_weather",
                         help="Tool name for --direct (default: get_trail_weather)")
    args = parser.parse_args()

    if args.direct:
        raw_args = json.loads(args.direct)
        validated, error = validate_input(args.tool, raw_args)
        if error:
            print(json.dumps({"error": error}, indent=2))
            return
        tool_fn = TOOLS.get(args.tool)
        if tool_fn is None:
            print(json.dumps({"error": f"Unknown tool: {args.tool}"}, indent=2))
            return
        print(json.dumps(tool_fn(**raw_args), indent=2))
    elif args.ask:
        result = answer_with_tools(args.ask)
        print(json.dumps(result, indent=2))
    else:
        run_all()


if __name__ == "__main__":
    main()
