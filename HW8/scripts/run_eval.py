"""
HW8 -- Evaluation + Observability layer for the Mountain Bike Technical Assistant.

Runs the HW7 LangGraph agent (same chatbot as HW6/HW7 -- router -> tool/RAG ->
answer) on a fixed 10-question eval set, times each call, and dumps the raw
trace (route, tools used, retrieved chunks/sources, answer, latency) as JSON.

This script only *collects* raw traces -- it does not judge task_success,
groundedness, or answer_quality. Those columns require reading the actual
answer text against the question, so they are filled in by hand in
outputs/eval_results.md after inspecting this script's raw output.

Usage:
    python HW8/scripts/run_eval.py     # run all 10 eval questions, save outputs/eval_raw.json
"""

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
RAW_FILE = OUTPUT_DIR / "eval_raw.json"

sys.path.insert(0, str(REPO_ROOT / "HW7" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW6" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW5" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW4" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW3" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "HW2" / "scripts"))
import langgraph_flow  # noqa: E402 -- HW7's LangGraph app (run_agent)

ROUTE_TO_MODE = {
    "weather_workflow": "tool",
    "part_manual_workflow": "tool",
    "knowledge_base_workflow": "RAG",
    "clarification": "clarification",
}

EVAL_SET = [
    {"id": 1, "question": "How do I set sag on my mountain bike fork?",
     "expected_behavior": "Answer from KB with clear step-by-step procedure"},
    {"id": 2, "question": "How do I bleed my hydraulic disc brakes?",
     "expected_behavior": "Answer from KB, retrieval required (not a single obvious keyword match)"},
    {"id": 3, "question": "What is rebound damping and how do I adjust it on a RockShox shock?",
     "expected_behavior": "Answer from KB, retrieval required"},
    {"id": 4, "question": "Which New Zealand trails are rated beginner and suitable for easy rides?",
     "expected_behavior": "Answer from KB, but retrieval may return a tangentially related (harder-trail) chunk"},
    {"id": 5, "question": "What's the recommended battery voltage and charging time for an e-MTB battery?",
     "expected_behavior": "Say not enough information -- e-MTB battery specs are not in the KB"},
    {"id": 6, "question": "What tire pressure should I run on a fat bike in snow conditions?",
     "expected_behavior": "Say not enough information -- fat-bike/snow tire pressure is not in the KB"},
    {"id": 7, "question": "Is it a good day to ride the trails in Queenstown, New Zealand today?",
     "expected_behavior": "Use weather tool, return live forecast + riding-conditions note"},
    {"id": 8, "question": "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?",
     "expected_behavior": "Use web-lookup tool, return manual link(s)"},
    {"id": 9, "question": "Is my bike ready to ride in the rain today or does it need maintenance first?",
     "expected_behavior": "Ambiguous -- could plausibly route to weather or maintenance KB; system should pick one deterministically, not crash or stall"},
    {"id": 10, "question": "Tell me something interesting about mountain biking.",
     "expected_behavior": "Ask for clarification -- question matches no known route"},
]


def _extract_sources(observations: list) -> str:
    if not observations:
        return ""
    obs = observations[0]
    if "chunk_ids" in obs:
        return ", ".join(obs["chunk_ids"])
    if "sources" in obs:
        return ", ".join(obs["sources"])
    if "results" in obs:
        return ", ".join(r["url"] for r in obs["results"])
    if "resolved_place" in obs:
        return f"open-meteo:{obs['resolved_place']}"
    return json.dumps(obs)[:200]


def run_case(case: dict) -> dict:
    start = time.perf_counter()
    state = langgraph_flow.run_agent(case["question"])
    latency_ms = round((time.perf_counter() - start) * 1000)

    route = state["selected_route"]
    tool_calls = state["tool_calls"]
    return {
        "id": case["id"],
        "question": case["question"],
        "expected_behavior": case["expected_behavior"],
        "answer": state["final_answer"],
        "retrieved_chunks_or_sources": _extract_sources(state["observations"]),
        "route_or_mode": ROUTE_TO_MODE[route],
        "selected_route": route,
        "tools_used": ", ".join(tc["tool"] for tc in tool_calls) if tool_calls else "none",
        "latency_ms": latency_ms,
    }


def run_all() -> None:
    results = []
    for case in EVAL_SET:
        print(f"[{case['id']}/{len(EVAL_SET)}] running: {case['question']}")
        result = run_case(case)
        results.append(result)
        print(f"    -> route={result['route_or_mode']} tools={result['tools_used']} latency={result['latency_ms']}ms")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nRaw traces saved -> {RAW_FILE}")


if __name__ == "__main__":
    run_all()
