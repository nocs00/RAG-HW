"""
HW6 -- First agentic structure: a controlled, deterministic agent workflow for the
Mountain Bike Technical Assistant (same domain/chatbot as HW1-5).

Use case: a rider asks the assistant one question. The workflow must decide, WITHOUT
an LLM call, which of three specialist workflows to run (weather / part-manual lookup /
knowledge-base how-to), call the matching tool, and produce a final answer -- or ask the
rider to clarify if the question doesn't match any known route.

user goal -> route (rule-based) -> action (tool call) -> observation -> state update
          -> next step (answer synthesis) -> final answer

Tools are reused verbatim from HW5 (get_trail_weather, search_part_manual,
search_knowledge_base -- the latter wrapping HW4's grounded RAG pipeline). HW5 used an
LLM to pick between them; HW6's whole point is to replace that choice with a plain
keyword-based router, so no LLM is involved in routing -- only (optionally) inside the
reused search_knowledge_base tool, where HW4's grounded-answer generation step already
requires one.

Usage:
    python HW6/scripts/agent_flow.py                  # run all test cases, save outputs/agent_flow_examples.md
    python HW6/scripts/agent_flow.py --ask "..."       # run a single question through the workflow
"""

import argparse
import json
import re
import sys
from io import TextIOBase
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
EXAMPLES_FILE = OUTPUT_DIR / "agent_flow_examples.md"

sys.path.insert(0, str(REPO_ROOT / "HW5" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW4" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW3" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW2" / "scripts"))
import external_tool  # noqa: E402 -- HW5's tool implementations (weather API, web lookup, HW4 RAG wrapper)


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
# Step 1: Router -- deterministic, rule-based, no LLM involved
# ---------------------------------------------------------------------------

WEATHER_KEYWORDS = [
    "weather", "forecast", "rain", "windy", "wind", "temperature",
    "good day to ride", "ride today", "ride this weekend", "riding conditions",
]
PART_MANUAL_KEYWORDS = [
    "manual", "spec sheet", "spare parts", "parts catalog", "catalog",
    "installation instructions", "datasheet", "service manual",
]
KNOWLEDGE_BASE_KEYWORDS = [
    "how do i", "how to", "sag", "bleed", "adjust", "set up", "setup",
    "maintenance", "install", "tighten", "clean", "lube", "grease",
]

ROUTES = ("weather_workflow", "part_manual_workflow", "knowledge_base_workflow", "clarification")


def select_route(question: str) -> str:
    """Rule-based routing -- first matching category wins, no LLM call."""
    q = question.lower()
    if any(kw in q for kw in WEATHER_KEYWORDS):
        return "weather_workflow"
    if any(kw in q for kw in PART_MANUAL_KEYWORDS):
        return "part_manual_workflow"
    if any(kw in q for kw in KNOWLEDGE_BASE_KEYWORDS):
        return "knowledge_base_workflow"
    return "clarification"


# ---------------------------------------------------------------------------
# Step 2: Slot extraction -- deterministic, regex-based (no LLM)
# ---------------------------------------------------------------------------

_LOCATION_RE = re.compile(r"(?:\bin\b|\bfor\b)\s+([A-Z][a-zA-Z]+(?:\s*,\s*[A-Z][a-zA-Z ]+)?)")
_DAYS_AHEAD_RE = re.compile(r"(\d+)\s+days?\s+from\s+now")
_LOCATION_TRAILING_STOPWORDS = re.compile(
    r"\s+(today|tomorrow|tonight|this\s+weekend|this\s+week|now)\s*$", re.IGNORECASE
)


def extract_weather_slots(question: str) -> dict:
    loc_match = _LOCATION_RE.search(question)
    location = loc_match.group(1).strip() if loc_match else question.strip().rstrip("?")
    location = _LOCATION_TRAILING_STOPWORDS.sub("", location).strip()
    days_match = _DAYS_AHEAD_RE.search(question.lower())
    days_ahead = int(days_match.group(1)) if days_match else 0
    return {"location": location, "days_ahead": days_ahead}


def extract_part_manual_slots(question: str) -> dict:
    return {"query": question.strip().rstrip("?"), "max_results": 3}


def extract_knowledge_base_slots(question: str) -> dict:
    return {"query": question.strip().rstrip("?")}


# ---------------------------------------------------------------------------
# Step 3 & 4: Tool call + observation -- tools reused verbatim from HW5
# ---------------------------------------------------------------------------

TOOLS = {
    "weather_workflow": external_tool.get_trail_weather,
    "part_manual_workflow": external_tool.search_part_manual,
    "knowledge_base_workflow": external_tool.search_knowledge_base,
}

TOOL_NAMES = {
    "weather_workflow": "get_trail_weather",
    "part_manual_workflow": "search_part_manual",
    "knowledge_base_workflow": "search_knowledge_base",
}


# ---------------------------------------------------------------------------
# Step 5: Answer synthesis -- deterministic templates per route (no LLM,
# except knowledge_base_workflow's tool already returns a synthesized answer
# from HW4's grounded RAG pipeline)
# ---------------------------------------------------------------------------

def synthesize_weather_answer(observation: dict) -> str:
    if "error" in observation:
        return f"I couldn't get the weather: {observation['error']}. Could you confirm the location and try again?"
    return (
        f"Weather for {observation['resolved_place']} on {observation['date']}: "
        f"{observation['weather_description']}, high {observation['temperature_max_c']}°C / "
        f"low {observation['temperature_min_c']}°C, precipitation {observation['precipitation_mm']}mm, "
        f"max wind {observation['wind_speed_max_kmh']}km/h. {observation['riding_conditions_note']}"
    )


def synthesize_part_manual_answer(observation: dict) -> str:
    if "error" in observation:
        return f"I couldn't find a manual: {observation['error']}. Could you double check the part name/model?"
    lines = [f"- {r['title']}: {r['url']}" for r in observation["results"]]
    return "Here's what I found:\n" + "\n".join(lines)


def synthesize_knowledge_base_answer(observation: dict) -> str:
    if "error" in observation:
        return f"I couldn't find an answer in the knowledge base: {observation['error']}."
    return observation["answer"]


ANSWER_SYNTHESIZERS = {
    "weather_workflow": synthesize_weather_answer,
    "part_manual_workflow": synthesize_part_manual_answer,
    "knowledge_base_workflow": synthesize_knowledge_base_answer,
}

CLARIFICATION_MESSAGE = (
    "Could you please clarify your question? Are you asking about current/forecast "
    "weather and riding conditions, a specific part's manual or spec sheet, or a "
    "general how-to/maintenance question?"
)


# ---------------------------------------------------------------------------
# The agent workflow itself
# ---------------------------------------------------------------------------

def run_agent(question: str) -> dict:
    """
    user goal -> route -> action -> observation -> state update -> next step -> final answer
    """
    state = {
        "user_question": question,
        "selected_route": None,
        "extracted_slots": None,
        "tool_calls": [],
        "observations": [],
        "final_answer": None,
    }

    # Step 1: Route
    state["selected_route"] = select_route(question)

    # Step 2: Execute (slot extraction -> tool call -> observation -> answer synthesis)
    route = state["selected_route"]
    if route == "clarification":
        state["final_answer"] = CLARIFICATION_MESSAGE
        return state

    if route == "weather_workflow":
        slots = extract_weather_slots(question)
    elif route == "part_manual_workflow":
        slots = extract_part_manual_slots(question)
    else:
        slots = extract_knowledge_base_slots(question)
    state["extracted_slots"] = slots

    tool_fn = TOOLS[route]
    observation = tool_fn(**slots)

    state["tool_calls"].append({"tool": TOOL_NAMES[route], "input": slots})
    state["observations"].append(observation)

    state["final_answer"] = ANSWER_SYNTHESIZERS[route](observation)
    return state


# ---------------------------------------------------------------------------
# Test cases -- 5 examples covering every route (incl. clarification)
# ---------------------------------------------------------------------------

TEST_CASES = [
    "Is it a good day to ride the trails in Queenstown, New Zealand today?",
    "What's the forecast for Rotorua, New Zealand 3 days from now?",
    "How do I set sag on my mountain bike fork?",
    "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?",
    "Tell me something interesting about mountain biking.",
]


def _format_case(question: str, state: dict) -> None:
    print(f"Question: {question}\n")
    print(f"Route: {state['selected_route']}\n")
    tool_call = state["tool_calls"][0] if state["tool_calls"] else None
    print(f"Tool called: {tool_call['tool'] if tool_call else '(none — clarification)'}\n")
    observation = state["observations"][0] if state["observations"] else None
    print(f"Observation: {json.dumps(observation) if observation is not None else 'N/A'}\n")
    print(f"State after step: {json.dumps(state, indent=2)}\n")
    print(f"Final answer:\n{state['final_answer']}\n")
    print("---\n")


def run_all() -> None:
    tee = _Tee(EXAMPLES_FILE)
    sys.stdout = tee
    try:
        print("# HW6 — Agent Flow Examples\n")
        for question in TEST_CASES:
            state = run_agent(question)
            _format_case(question, state)
    finally:
        sys.stdout = sys.__stdout__
        tee.close()
        print(f"\nOutput saved -> {EXAMPLES_FILE}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="HW6 agentic workflow demo")
    parser.add_argument("--ask", type=str, help="Run a single question through the agent workflow")
    args = parser.parse_args()

    if args.ask:
        state = run_agent(args.ask)
        print(json.dumps(state, indent=2))
    else:
        run_all()


if __name__ == "__main__":
    main()
