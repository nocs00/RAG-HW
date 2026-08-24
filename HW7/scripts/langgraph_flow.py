"""
HW7 -- Porting HW6's custom agentic workflow onto LangGraph.

Same Mountain Bike Technical Assistant use case as HW6: a rider asks one question,
a deterministic (no-LLM) router picks one of three specialist tool workflows --
weather / part-manual lookup / knowledge-base how-to -- or asks the rider to
clarify. HW6 implemented this as a single Python function threading a dict
through if/elif branches; HW7 re-implements the exact same routing rules, tools,
and answer-synthesis templates as a LangGraph StateGraph: explicit nodes, a typed
State, and a conditional edge instead of if/elif.

Nothing about the *behavior* changes -- routing keywords, slot extraction, tools,
and answer templates are imported verbatim from HW6/scripts/agent_flow.py. Only
the control-flow representation changes (function calls -> graph nodes + edges).

Usage:
    python HW7/scripts/langgraph_flow.py                  # run all test cases, save outputs/langgraph_examples.md
    python HW7/scripts/langgraph_flow.py --ask "..."        # run a single question through the graph
"""

import argparse
import json
import sys
from io import TextIOBase
from pathlib import Path
from typing import List, Optional, TypedDict

from langgraph.graph import END, StateGraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
EXAMPLES_FILE = OUTPUT_DIR / "langgraph_examples.md"

sys.path.insert(0, str(REPO_ROOT / "HW6" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW5" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW4" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW3" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW2" / "scripts"))
import agent_flow as hw6  # noqa: E402 -- reuse HW6's router, slot extraction, tools, answer templates verbatim


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
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    user_question: str
    selected_route: Optional[str]
    extracted_slots: Optional[dict]
    tool_calls: List[dict]
    observations: List[dict]
    final_answer: Optional[str]


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def classify_request(state: AgentState) -> AgentState:
    """Router node -- same keyword rules as HW6's select_route(), no LLM call."""
    state["selected_route"] = hw6.select_route(state["user_question"])
    return state


def _run_tool_route(state: AgentState, route: str, extract_slots) -> AgentState:
    slots = extract_slots(state["user_question"])
    observation = hw6.TOOLS[route](**slots)
    state["extracted_slots"] = slots
    state["tool_calls"].append({"tool": hw6.TOOL_NAMES[route], "input": slots})
    state["observations"].append(observation)
    state["final_answer"] = hw6.ANSWER_SYNTHESIZERS[route](observation)
    return state


def run_weather_workflow(state: AgentState) -> AgentState:
    return _run_tool_route(state, "weather_workflow", hw6.extract_weather_slots)


def run_part_manual_workflow(state: AgentState) -> AgentState:
    return _run_tool_route(state, "part_manual_workflow", hw6.extract_part_manual_slots)


def run_knowledge_base_workflow(state: AgentState) -> AgentState:
    return _run_tool_route(state, "knowledge_base_workflow", hw6.extract_knowledge_base_slots)


def ask_clarification(state: AgentState) -> AgentState:
    state["final_answer"] = hw6.CLARIFICATION_MESSAGE
    return state


# ---------------------------------------------------------------------------
# Edges -- one conditional edge after classify_request, fanning out to the
# matching route node; every route node then goes straight to END.
# ---------------------------------------------------------------------------

def route_decision(state: AgentState) -> str:
    return state["selected_route"]


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify_request", classify_request)
    graph.add_node("weather_workflow", run_weather_workflow)
    graph.add_node("part_manual_workflow", run_part_manual_workflow)
    graph.add_node("knowledge_base_workflow", run_knowledge_base_workflow)
    graph.add_node("clarification", ask_clarification)

    graph.set_entry_point("classify_request")
    graph.add_conditional_edges(
        "classify_request",
        route_decision,
        {
            "weather_workflow": "weather_workflow",
            "part_manual_workflow": "part_manual_workflow",
            "knowledge_base_workflow": "knowledge_base_workflow",
            "clarification": "clarification",
        },
    )
    graph.add_edge("weather_workflow", END)
    graph.add_edge("part_manual_workflow", END)
    graph.add_edge("knowledge_base_workflow", END)
    graph.add_edge("clarification", END)
    return graph.compile()


APP = build_graph()

NODES_EXECUTED = {
    "weather_workflow": "classify_request -> weather_workflow",
    "part_manual_workflow": "classify_request -> part_manual_workflow",
    "knowledge_base_workflow": "classify_request -> knowledge_base_workflow",
    "clarification": "classify_request -> clarification",
}


def run_agent(question: str) -> AgentState:
    initial_state: AgentState = {
        "user_question": question,
        "selected_route": None,
        "extracted_slots": None,
        "tool_calls": [],
        "observations": [],
        "final_answer": None,
    }
    return APP.invoke(initial_state)


# ---------------------------------------------------------------------------
# Test cases -- 4 examples, one per route (mirrors HW6's route coverage)
# ---------------------------------------------------------------------------

TEST_CASES = [
    "Is it a good day to ride the trails in Queenstown, New Zealand today?",
    "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?",
    "How do I set sag on my mountain bike fork?",
    "Tell me something interesting about mountain biking.",
]


def _format_case(question: str, state: AgentState) -> None:
    route = state["selected_route"]
    print(f"Question: {question}\n")
    print(f"Route: {route}\n")
    print(f"Nodes executed: {NODES_EXECUTED[route]}\n")
    print(f"Final state:\n{json.dumps(state, indent=2)}\n")
    print(f"Final answer:\n{state['final_answer']}\n")
    print("---\n")


def run_all() -> None:
    tee = _Tee(EXAMPLES_FILE)
    sys.stdout = tee
    try:
        print("# HW7 — LangGraph Flow Examples\n")
        for question in TEST_CASES:
            state = run_agent(question)
            _format_case(question, state)
    finally:
        sys.stdout = sys.__stdout__
        tee.close()
        print(f"\nOutput saved -> {EXAMPLES_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="HW7 LangGraph workflow demo")
    parser.add_argument("--ask", type=str, help="Run a single question through the graph")
    args = parser.parse_args()

    if args.ask:
        state = run_agent(args.ask)
        print(json.dumps(state, indent=2))
    else:
        run_all()


if __name__ == "__main__":
    main()
