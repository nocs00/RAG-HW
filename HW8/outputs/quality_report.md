# Quality Report — Mountain Bike Technical Assistant

## What was tested
10 questions run live against the HW7 LangGraph agent, covering: a simple
knowledge-base question, two questions needing real retrieval, one question
where retrieval could plausibly return a weak/tangential chunk, two questions
the knowledge base genuinely doesn't cover, two tool-driven questions (live
weather, web manual lookup), one deliberately ambiguous/compound question, and
one out-of-scope chit-chat question that should trigger clarification.

## Results
- 60% full success, 20% partial, 20% failure (see `eval_summary.md`)
- Every tool call that actually executed (weather, part-manual web lookup, all
  3 direct knowledge-base retrievals) produced a correct or honestly-declined
  answer — 0 hallucinations among the 5 cases that reached a tool
- 4 of 10 cases never reached a tool at all, even though 2 of those 4
  (verified manually by calling `search_knowledge_base` directly) had a real,
  useful, grounded answer sitting in the knowledge base the whole time

## Where the system works well
- Direct knowledge-base questions with router-recognized keywords ("sag",
  "rebound damping", "bleed") — retrieval, grounding, and citation all correct
- Weather tool and part-manual web-lookup tool — both returned accurate,
  on-topic results with no errors
- Recognizing genuinely out-of-scope chit-chat ("tell me something
  interesting...") and asking for clarification

## Where the system fails
- The router's keyword list is a hard gate in front of the knowledge base:
  if a question doesn't contain one of ~15 hardcoded phrases, it never reaches
  `search_knowledge_base` at all — it just gets a generic, one-size-fits-all
  clarification message, even when the KB actually has the answer
- The weather tool's location extractor has no failure mode: if it can't find
  an `in X` / `for X` pattern, it silently hands the *entire question* to the
  geocoder as a "location" instead of recognizing extraction failed
- Latency is inconsistent for the identical route (21.7s cold vs. 3–5s warm
  for knowledge-base calls) because models/index are lazily loaded on first
  use with no warm-up step

## 3 Main Problems
1. **Router keyword coverage gate blocks legitimate KB questions.** 3 of 10
   questions (ids 4, 5, 6 — trail difficulty, e-MTB battery specs, fat-bike
   tire pressure) never triggered retrieval because none of their words match
   the router's fixed keyword list, even though one of them (id 4) had a
   genuinely correct answer in the KB and the other two would have produced a
   more specific, better decline than the generic clarification message the
   user actually received.
2. **No fallback when slot extraction fails.** id 9's ambiguous, longer
   sentence caused the weather tool's regex-based location extractor to treat
   the whole question as a location string, producing an opaque geocoding
   error instead of asking the user to specify a location or recognizing
   extraction had failed.
3. **No warm-up / caching strategy causes a 40x latency spike on the first
   call.** id 1 took 21.7s vs. 3–5s for subsequent knowledge-base calls in the
   same run — acceptable in a benchmark script, but this would be the first
   thing a real user experiences in a live chat session.

## Next Steps
- Change the router's "no keyword matched" branch to attempt a
  knowledge-base lookup first, and only fall back to asking for clarification
  if that lookup itself declines (ties directly into the Final Project's
  routing improvement)
- Add a location-extraction success check to the weather tool's slot
  extractor: if no `in X`/`for X` pattern is found, skip the tool call and ask
  the user for a location instead of guessing
- Warm up the FAISS index, reranker, and Ollama connection once at process
  startup instead of lazily on the first request
