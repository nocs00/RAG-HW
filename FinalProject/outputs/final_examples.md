# Final Project — Improved Routing Examples

Loading model : sentence-transformers/all-MiniLM-L6-v2
Loading index : /Users/pavlodudenkov/Desktop/learning/RAG-HW/HW2/index/faiss.index
Index ready   : 240 vectors, dim=384

Loading reranker: cross-encoder/ms-marco-MiniLM-L-6-v2
Question: Which New Zealand trails are rated beginner and suitable for easy rides?

Route: knowledge_base_fallback

Final state:
{
  "user_question": "Which New Zealand trails are rated beginner and suitable for easy rides?",
  "selected_route": "knowledge_base_fallback",
  "extracted_slots": {
    "query": "Which New Zealand trails are rated beginner and suitable for easy rides"
  },
  "tool_calls": [
    {
      "tool": "search_knowledge_base",
      "input": {
        "query": "Which New Zealand trails are rated beginner and suitable for easy rides"
      }
    }
  ],
  "observations": [
    {
      "answer": "Based on the provided context, I can identify the following trails that are rated as \"Easy\" and suitable for beginner riders:\n\n* Te Ara a Waiau Walkway/Cycleway (chunk_id: doc_mtb_tracks_chunk_0026 | source_file: doc_mtb_tracks.csv | score: 3.18)\n\t+ Estimated biking time: 1 hr\n* Okahukura Loop (chunk_id: doc_mtb_tracks_chunk_0026 | source_file: doc_mtb_tracks.csv | score: 3.18)\n\t+ Difficulty: Easy\n\t+ Estimated biking time: 3 hr\n* Braemar Road to Landslip Creek (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)\n\t+ Difficulty: Easy\n\t+ Estimated biking time: 2 hr\n* Christchurch to Little River Rail Trail (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)\n\t+ Difficulty: Easiest\n\t+ The whole trail is 46 km long, but the section described here covers 20 km.\n* Butterfields Wetland Walk (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)\n\t+ Difficulty: Easy\n\nPlease note that while these trails are rated as \"Easy\", it's always a good idea to assess your own riding skills and experience before attempting any trail.",
      "chunk_ids": [
        "doc_mtb_tracks_chunk_0022",
        "doc_mtb_tracks_chunk_0026",
        "doc_mtb_tracks_chunk_0037"
      ],
      "sources": [
        "doc_mtb_tracks.csv"
      ]
    }
  ],
  "final_answer": "Based on the provided context, I can identify the following trails that are rated as \"Easy\" and suitable for beginner riders:\n\n* Te Ara a Waiau Walkway/Cycleway (chunk_id: doc_mtb_tracks_chunk_0026 | source_file: doc_mtb_tracks.csv | score: 3.18)\n\t+ Estimated biking time: 1 hr\n* Okahukura Loop (chunk_id: doc_mtb_tracks_chunk_0026 | source_file: doc_mtb_tracks.csv | score: 3.18)\n\t+ Difficulty: Easy\n\t+ Estimated biking time: 3 hr\n* Braemar Road to Landslip Creek (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)\n\t+ Difficulty: Easy\n\t+ Estimated biking time: 2 hr\n* Christchurch to Little River Rail Trail (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)\n\t+ Difficulty: Easiest\n\t+ The whole trail is 46 km long, but the section described here covers 20 km.\n* Butterfields Wetland Walk (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)\n\t+ Difficulty: Easy\n\nPlease note that while these trails are rated as \"Easy\", it's always a good idea to assess your own riding skills and experience before attempting any trail."
}

Final answer:
Based on the provided context, I can identify the following trails that are rated as "Easy" and suitable for beginner riders:

* Te Ara a Waiau Walkway/Cycleway (chunk_id: doc_mtb_tracks_chunk_0026 | source_file: doc_mtb_tracks.csv | score: 3.18)
	+ Estimated biking time: 1 hr
* Okahukura Loop (chunk_id: doc_mtb_tracks_chunk_0026 | source_file: doc_mtb_tracks.csv | score: 3.18)
	+ Difficulty: Easy
	+ Estimated biking time: 3 hr
* Braemar Road to Landslip Creek (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)
	+ Difficulty: Easy
	+ Estimated biking time: 2 hr
* Christchurch to Little River Rail Trail (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)
	+ Difficulty: Easiest
	+ The whole trail is 46 km long, but the section described here covers 20 km.
* Butterfields Wetland Walk (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: 0.99)
	+ Difficulty: Easy

Please note that while these trails are rated as "Easy", it's always a good idea to assess your own riding skills and experience before attempting any trail.

---

Question: What's the recommended battery voltage and charging time for an e-MTB battery?

Route: knowledge_base_fallback

Final state:
{
  "user_question": "What's the recommended battery voltage and charging time for an e-MTB battery?",
  "selected_route": "knowledge_base_fallback",
  "extracted_slots": {
    "query": "What's the recommended battery voltage and charging time for an e-MTB battery"
  },
  "tool_calls": [
    {
      "tool": "search_knowledge_base",
      "input": {
        "query": "What's the recommended battery voltage and charging time for an e-MTB battery"
      }
    }
  ],
  "observations": [
    {
      "answer": "I do not have enough information in the retrieved documents to answer this question.",
      "chunk_ids": [
        "Suspension_SRAM_chunk_0028",
        "mtb_maintenance_guide_chunk_0000",
        "Suspension_SRAM_chunk_0029"
      ],
      "sources": [
        "Suspension_SRAM.pdf",
        "mtb_maintenance_guide.md"
      ]
    }
  ],
  "final_answer": "I checked the knowledge base but couldn't find a grounded answer to that. Could you please clarify your question? Are you asking about current/forecast weather and riding conditions, a specific part's manual or spec sheet, or a general how-to/maintenance question?"
}

Final answer:
I checked the knowledge base but couldn't find a grounded answer to that. Could you please clarify your question? Are you asking about current/forecast weather and riding conditions, a specific part's manual or spec sheet, or a general how-to/maintenance question?

---

Question: What tire pressure should I run on a fat bike in snow conditions?

Route: knowledge_base_fallback

Final state:
{
  "user_question": "What tire pressure should I run on a fat bike in snow conditions?",
  "selected_route": "knowledge_base_fallback",
  "extracted_slots": {
    "query": "What tire pressure should I run on a fat bike in snow conditions"
  },
  "tool_calls": [
    {
      "tool": "search_knowledge_base",
      "input": {
        "query": "What tire pressure should I run on a fat bike in snow conditions"
      }
    }
  ],
  "observations": [
    {
      "answer": "I do not have enough information in the retrieved documents to answer this question.\n\nHowever, based on the context provided, it seems that the topic of tire pressure is only mentioned briefly in relation to shock pumps (which are used for pressurizing suspension components) and not specifically in relation to fat bikes or snow conditions.",
      "chunk_ids": [
        "mountain_bike_wiki_chunk_0016",
        "mountain_bike_wiki_chunk_0017",
        "mtb_suspension_setup_guide_chunk_0001"
      ],
      "sources": [
        "mountain_bike_wiki.txt",
        "mtb_suspension_setup_guide.md"
      ]
    }
  ],
  "final_answer": "I checked the knowledge base but couldn't find a grounded answer to that. Could you please clarify your question? Are you asking about current/forecast weather and riding conditions, a specific part's manual or spec sheet, or a general how-to/maintenance question?"
}

Final answer:
I checked the knowledge base but couldn't find a grounded answer to that. Could you please clarify your question? Are you asking about current/forecast weather and riding conditions, a specific part's manual or spec sheet, or a general how-to/maintenance question?

---

Question: How do I set sag on my mountain bike fork?

Route: knowledge_base_workflow

Final state:
{
  "user_question": "How do I set sag on my mountain bike fork?",
  "selected_route": "knowledge_base_workflow",
  "extracted_slots": {
    "query": "How do I set sag on my mountain bike fork"
  },
  "tool_calls": [
    {
      "tool": "search_knowledge_base",
      "input": {
        "query": "How do I set sag on my mountain bike fork"
      }
    }
  ],
  "observations": [
    {
      "answer": "To set sag on your mountain bike fork, follow these steps:\n\n1. Inflate the air spring in the fork to the recommended pressure for your weight (this can be found in the manufacturer's manual, on their website or printed on the back of one leg).\n2. Check any external compression-damping dials or levers are set fully open.\n3. Bounce on the bike to 'free up' the suspension and help balance the air pressure in the negative spring.\n4. Get a friend to hold the bike while you get into your normal standing position, holding this for about five seconds.\n5. Ensure that the rubber O-ring around the fork stanchion is pushed up against the wiper seal.\n6. Carefully dismount from the bike without disturbing the O-ring.\n\nThen, measure the distance (in millimetres) that the O-ring has moved up the stanchion, divide this by the fork's travel (e.g. 160mm), and multiply that by 100 to find the sag percentage.\n\n[chunk_id: how_to_setup_suspension_chunk_0003 | source_file: how_to_setup_suspension.mhtml | score: 5.47]\n[chunk_id: how_to_setup_suspension_chunk_0004 | source_file: how_to_setup_suspension.mhtml | score: 4.10]",
      "chunk_ids": [
        "how_to_setup_suspension_chunk_0002",
        "how_to_setup_suspension_chunk_0003",
        "how_to_setup_suspension_chunk_0004"
      ],
      "sources": [
        "how_to_setup_suspension.mhtml"
      ]
    }
  ],
  "final_answer": "To set sag on your mountain bike fork, follow these steps:\n\n1. Inflate the air spring in the fork to the recommended pressure for your weight (this can be found in the manufacturer's manual, on their website or printed on the back of one leg).\n2. Check any external compression-damping dials or levers are set fully open.\n3. Bounce on the bike to 'free up' the suspension and help balance the air pressure in the negative spring.\n4. Get a friend to hold the bike while you get into your normal standing position, holding this for about five seconds.\n5. Ensure that the rubber O-ring around the fork stanchion is pushed up against the wiper seal.\n6. Carefully dismount from the bike without disturbing the O-ring.\n\nThen, measure the distance (in millimetres) that the O-ring has moved up the stanchion, divide this by the fork's travel (e.g. 160mm), and multiply that by 100 to find the sag percentage.\n\n[chunk_id: how_to_setup_suspension_chunk_0003 | source_file: how_to_setup_suspension.mhtml | score: 5.47]\n[chunk_id: how_to_setup_suspension_chunk_0004 | source_file: how_to_setup_suspension.mhtml | score: 4.10]"
}

Final answer:
To set sag on your mountain bike fork, follow these steps:

1. Inflate the air spring in the fork to the recommended pressure for your weight (this can be found in the manufacturer's manual, on their website or printed on the back of one leg).
2. Check any external compression-damping dials or levers are set fully open.
3. Bounce on the bike to 'free up' the suspension and help balance the air pressure in the negative spring.
4. Get a friend to hold the bike while you get into your normal standing position, holding this for about five seconds.
5. Ensure that the rubber O-ring around the fork stanchion is pushed up against the wiper seal.
6. Carefully dismount from the bike without disturbing the O-ring.

Then, measure the distance (in millimetres) that the O-ring has moved up the stanchion, divide this by the fork's travel (e.g. 160mm), and multiply that by 100 to find the sag percentage.

[chunk_id: how_to_setup_suspension_chunk_0003 | source_file: how_to_setup_suspension.mhtml | score: 5.47]
[chunk_id: how_to_setup_suspension_chunk_0004 | source_file: how_to_setup_suspension.mhtml | score: 4.10]

---

Question: Is it a good day to ride the trails in Queenstown, New Zealand today?

Route: weather_workflow

Final state:
{
  "user_question": "Is it a good day to ride the trails in Queenstown, New Zealand today?",
  "selected_route": "weather_workflow",
  "extracted_slots": {
    "location": "Queenstown, New Zealand",
    "days_ahead": 0
  },
  "tool_calls": [
    {
      "tool": "get_trail_weather",
      "input": {
        "location": "Queenstown, New Zealand",
        "days_ahead": 0
      }
    }
  ],
  "observations": [
    {
      "location": "Queenstown, New Zealand",
      "resolved_place": "Queenstown, New Zealand",
      "coordinates": {
        "lat": -45.03023,
        "lon": 168.6627
      },
      "date": "2026-09-03",
      "temperature_max_c": 14.9,
      "temperature_min_c": 6.8,
      "precipitation_mm": 6.3,
      "wind_speed_max_kmh": 7.7,
      "weather_description": "Dense drizzle",
      "riding_conditions_note": "Rain expected -- trails may be muddy/slippery, consider rescheduling."
    }
  ],
  "final_answer": "Weather for Queenstown, New Zealand on 2026-09-03: Dense drizzle, high 14.9\u00b0C / low 6.8\u00b0C, precipitation 6.3mm, max wind 7.7km/h. Rain expected -- trails may be muddy/slippery, consider rescheduling."
}

Final answer:
Weather for Queenstown, New Zealand on 2026-09-03: Dense drizzle, high 14.9°C / low 6.8°C, precipitation 6.3mm, max wind 7.7km/h. Rain expected -- trails may be muddy/slippery, consider rescheduling.

---

Question: Tell me something interesting about mountain biking.

Route: knowledge_base_fallback

Final state:
{
  "user_question": "Tell me something interesting about mountain biking.",
  "selected_route": "knowledge_base_fallback",
  "extracted_slots": {
    "query": "Tell me something interesting about mountain biking."
  },
  "tool_calls": [
    {
      "tool": "search_knowledge_base",
      "input": {
        "query": "Tell me something interesting about mountain biking."
      }
    }
  ],
  "observations": [
    {
      "answer": "Mountain bikes can be used on both unpaved surfaces like trails and paved surfaces, with some riders preferring the upright position, plush ride, and stability that mountain bikes offer even on paved roads. (chunk_id: mountain_bike_wiki_chunk_0001 | source_file: mountain_bike_wiki.txt)",
      "chunk_ids": [
        "mountain_bike_wiki_chunk_0000",
        "mountain_bike_wiki_chunk_0002",
        "mountain_bike_wiki_chunk_0001"
      ],
      "sources": [
        "mountain_bike_wiki.txt"
      ]
    }
  ],
  "final_answer": "Mountain bikes can be used on both unpaved surfaces like trails and paved surfaces, with some riders preferring the upright position, plush ride, and stability that mountain bikes offer even on paved roads. (chunk_id: mountain_bike_wiki_chunk_0001 | source_file: mountain_bike_wiki.txt)"
}

Final answer:
Mountain bikes can be used on both unpaved surfaces like trails and paved surfaces, with some riders preferring the upright position, plush ride, and stability that mountain bikes offer even on paved roads. (chunk_id: mountain_bike_wiki_chunk_0001 | source_file: mountain_bike_wiki.txt)

---

