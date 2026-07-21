"""
Run all test queries from test_queries.py through retrieval.py and print results.

Usage:
    python run_tests.py          # k=3 (default)
    python run_tests.py --k 5
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from test_queries import TEST_QUERIES
from retrieval import search


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all test queries through retrieval")
    parser.add_argument("--k", type=int, default=3, help="Top-k results per query (default: 3)")
    args = parser.parse_args()

    print(f"Running {len(TEST_QUERIES)} test queries  (k={args.k})\n")
    print("=" * 70)

    for q in TEST_QUERIES:
        search(q["query"], k=args.k)
        print(f"  Note: {q['note']}")
        print("=" * 70)


if __name__ == "__main__":
    main()
