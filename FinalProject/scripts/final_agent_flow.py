"""
Final Project -- one meaningful technical improvement on top of HW7's LangGraph
agent (the same Mountain Bike Technical Assistant chatbot as HW1-8).

Weak point selected (found and evidenced by HW8's eval, see
HW8/outputs/quality_report.md, Problem #1): the router's keyword list is a hard
gate in front of the knowledge base. If a question doesn't contain one of a
fixed set of ~15 phrases, it never reaches `search_knowledge_base` at all --
it just gets a generic, one-size-fits-all clarification message, even when the
knowledge base actually has the answer. 3/10 of HW8's eval questions
(trail difficulty, e-MTB battery specs, fat-bike tire pressure) hit exactly
this gap; manually calling the tool on those same questions showed it would
have answered one of them correctly and given a much better, on-topic decline
on the other two.

Improvement ("better routing", per the assignment's option table): replace the
router's immediate "no keyword matched -> clarification" branch with a
"no keyword matched -> attempt knowledge_base_fallback" branch. That node
always tries `search_knowledge_base` first. Only if the tool's own answer
contains HW4's existing decline phrase ("enough information" -- the same
guardrail HW4's grounded-answering prompt already relies on) does the graph
fall through to a clarification node -- and even then, the clarification
message is now specific about having checked the knowledge base first, instead
of a blind three-way guess.

Everything else (weather_workflow, part_manual_workflow, the exact-keyword
knowledge_base_workflow, all tool implementations) is reused verbatim from
HW7/HW6/HW5/HW4 -- this file only changes the router's default branch and adds
one new node + one new conditional edge.

Usage:
    python FinalProject/scripts/final_agent_flow.py                 # run all test cases, save outputs/final_examples.md
    python FinalProject/scripts/final_agent_flow.py --ask "..."      # run a single question through the graph
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
EXAMPLES_FILE = OUTPUT_DIR / "final_examples.md"

sys.path.insert(0, str(REPO_ROOT / "HW7" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW6" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW5" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW4" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW3" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW2" / "scripts"))
import langgraph_flow as hw7  # noqa: E402 -- reuse HW7's weather/part-manual/KB nodes verbatim
import agent_flow as hw6  # noqa: E402 -- reuse HW6's router keywords, tools, answer templates verbatim


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
# State -- identical shape to HW7's AgentState
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

DECLINE_PHRASE = "enough information"  # same guardrail phrase HW4's grounded prompt already produces


def classify_request(state: AgentState) -> AgentState:
    """Router -- same 3 keyword-matched routes as HW6/HW7. The only change: the
    old immediate 'clarification' default is now 'knowledge_base_fallback' --
    an actual attempt at an answer instead of an instant non-answer."""
    q = state["user_question"].lower()
    if any(kw in q for kw in hw6.WEATHER_KEYWORDS):
        state["selected_route"] = "weather_workflow"
    elif any(kw in q for kw in hw6.PART_MANUAL_KEYWORDS):
        state["selected_route"] = "part_manual_workflow"
    elif any(kw in q for kw in hw6.KNOWLEDGE_BASE_KEYWORDS):
        state["selected_route"] = "knowledge_base_workflow"
    else:
        state["selected_route"] = "knowledge_base_fallback"
    return state


def run_knowledge_base_fallback(state: AgentState) -> AgentState:
    """Catch-all node: try the knowledge base even though no keyword matched,
    instead of assuming the question is unanswerable."""
    slots = hw6.extract_knowledge_base_slots(state["user_question"])
    observation = hw6.TOOLS["knowledge_base_workflow"](**slots)
    state["extracted_slots"] = slots
    state["tool_calls"].append({"tool": "search_knowledge_base", "input": slots})
    state["observations"].append(observation)
    state["final_answer"] = hw6.synthesize_knowledge_base_answer(observation)
    return state


def ask_clarification_after_fallback(state: AgentState) -> AgentState:
    """Only reached when the fallback KB attempt itself declined -- the
    clarification message now says a KB lookup was actually tried."""
    state["final_answer"] = (
        "I checked the knowledge base but couldn't find a grounded answer to that. "
        + hw6.CLARIFICATION_MESSAGE
    )
    return state


# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------

def route_decision(state: AgentState) -> str:
    return state["selected_route"]


def fallback_decision(state: AgentState) -> str:
    """Second conditional edge: did the fallback KB attempt actually decline?"""
    answer = (state["final_answer"] or "").lower()
    return "clarification" if DECLINE_PHRASE in answer else "done"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify_request", classify_request)
    graph.add_node("weather_workflow", hw7.run_weather_workflow)
    graph.add_node("part_manual_workflow", hw7.run_part_manual_workflow)
    graph.add_node("knowledge_base_workflow", hw7.run_knowledge_base_workflow)
    graph.add_node("knowledge_base_fallback", run_knowledge_base_fallback)
    graph.add_node("clarification", ask_clarification_after_fallback)

    graph.set_entry_point("classify_request")
    graph.add_conditional_edges(
        "classify_request",
        route_decision,
        {
            "weather_workflow": "weather_workflow",
            "part_manual_workflow": "part_manual_workflow",
            "knowledge_base_workflow": "knowledge_base_workflow",
            "knowledge_base_fallback": "knowledge_base_fallback",
        },
    )
    graph.add_conditional_edges(
        "knowledge_base_fallback",
        fallback_decision,
        {"clarification": "clarification", "done": END},
    )
    graph.add_edge("weather_workflow", END)
    graph.add_edge("part_manual_workflow", END)
    graph.add_edge("knowledge_base_workflow", END)
    graph.add_edge("clarification", END)
    return graph.compile()


APP = build_graph()


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
# Test cases -- the 3 HW8 eval questions this improvement targets, plus one
# each of the unaffected routes to confirm no regression
# ---------------------------------------------------------------------------

TEST_CASES = [
    "Which New Zealand trails are rated beginner and suitable for easy rides?",
    "What's the recommended battery voltage and charging time for an e-MTB battery?",
    "What tire pressure should I run on a fat bike in snow conditions?",
    "How do I set sag on my mountain bike fork?",
    "Is it a good day to ride the trails in Queenstown, New Zealand today?",
    "Tell me something interesting about mountain biking.",
]


def _format_case(question: str, state: AgentState) -> None:
    print(f"Question: {question}\n")
    print(f"Route: {state['selected_route']}\n")
    print(f"Final state:\n{json.dumps(state, indent=2)}\n")
    print(f"Final answer:\n{state['final_answer']}\n")
    print("---\n")


def run_all() -> None:
    tee = _Tee(EXAMPLES_FILE)
    sys.stdout = tee
    try:
        print("# Final Project — Improved Routing Examples\n")
        for question in TEST_CASES:
            state = run_agent(question)
            _format_case(question, state)
    finally:
        sys.stdout = sys.__stdout__
        tee.close()
        print(f"\nOutput saved -> {EXAMPLES_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Final Project improved-routing agent")
    parser.add_argument("--ask", type=str, help="Run a single question through the graph")
    args = parser.parse_args()

    if args.ask:
        state = run_agent(args.ask)
        print(json.dumps(state, indent=2))
    else:
        run_all()


if __name__ == "__main__":
    main()
