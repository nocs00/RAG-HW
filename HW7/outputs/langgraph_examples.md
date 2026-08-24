# HW7 — LangGraph Flow Examples

Question: Is it a good day to ride the trails in Queenstown, New Zealand today?

Route: weather_workflow

Nodes executed: classify_request -> weather_workflow

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
      "date": "2026-08-25",
      "temperature_max_c": 13.0,
      "temperature_min_c": 6.1,
      "precipitation_mm": 9.1,
      "wind_speed_max_kmh": 11.4,
      "weather_description": "Unknown code 85",
      "riding_conditions_note": "Rain expected -- trails may be muddy/slippery, consider rescheduling."
    }
  ],
  "final_answer": "Weather for Queenstown, New Zealand on 2026-08-25: Unknown code 85, high 13.0\u00b0C / low 6.1\u00b0C, precipitation 9.1mm, max wind 11.4km/h. Rain expected -- trails may be muddy/slippery, consider rescheduling."
}

Final answer:
Weather for Queenstown, New Zealand on 2026-08-25: Unknown code 85, high 13.0°C / low 6.1°C, precipitation 9.1mm, max wind 11.4km/h. Rain expected -- trails may be muddy/slippery, consider rescheduling.

---

Question: Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?

Route: part_manual_workflow

Nodes executed: classify_request -> part_manual_workflow

Final state:
{
  "user_question": "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?",
  "selected_route": "part_manual_workflow",
  "extracted_slots": {
    "query": "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork",
    "max_results": 3
  },
  "tool_calls": [
    {
      "tool": "search_part_manual",
      "input": {
        "query": "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork",
        "max_results": 3
      }
    }
  ],
  "observations": [
    {
      "query": "Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork",
      "results": [
        {
          "title": "SERVICE MANUAL GEN.0000000007197 Rev C \u00a9 2024 SRAM, LLC 2019-2022 PIKE",
          "url": "https://www.sram.com/globalassets/document-hierarchy/service-manuals/rockshox/front-suspension/2019-2022-pike-2019-2023-revelation-service-manual.pdf",
          "snippet": "GEN.0000000007197 Rev C \u00a9 2024 SRAM, LLC \u00b7 2019-2023 REVELATION"
        },
        {
          "title": "Pike Ultimate | FS-PIKE-ULT-B3 | RockShox | Service",
          "url": "https://www.sram.com/en/service/models/fs-pike-ult-b3",
          "snippet": "2019-2022 Pike 2019-2023 Revelation Manual de Mantenimiento"
        },
        {
          "title": "Pike Ultimate | FS-PIKE-ULT-C1 | RockShox | Service",
          "url": "https://www.sram.com/en/service/models/fs-pike-ult-c1",
          "snippet": "Pike Ultimate, FS-PIKE-ULT-C1, RockShox"
        }
      ]
    }
  ],
  "final_answer": "Here's what I found:\n- SERVICE MANUAL GEN.0000000007197 Rev C \u00a9 2024 SRAM, LLC 2019-2022 PIKE: https://www.sram.com/globalassets/document-hierarchy/service-manuals/rockshox/front-suspension/2019-2022-pike-2019-2023-revelation-service-manual.pdf\n- Pike Ultimate | FS-PIKE-ULT-B3 | RockShox | Service: https://www.sram.com/en/service/models/fs-pike-ult-b3\n- Pike Ultimate | FS-PIKE-ULT-C1 | RockShox | Service: https://www.sram.com/en/service/models/fs-pike-ult-c1"
}

Final answer:
Here's what I found:
- SERVICE MANUAL GEN.0000000007197 Rev C © 2024 SRAM, LLC 2019-2022 PIKE: https://www.sram.com/globalassets/document-hierarchy/service-manuals/rockshox/front-suspension/2019-2022-pike-2019-2023-revelation-service-manual.pdf
- Pike Ultimate | FS-PIKE-ULT-B3 | RockShox | Service: https://www.sram.com/en/service/models/fs-pike-ult-b3
- Pike Ultimate | FS-PIKE-ULT-C1 | RockShox | Service: https://www.sram.com/en/service/models/fs-pike-ult-c1

---

Loading model : sentence-transformers/all-MiniLM-L6-v2
Loading index : /Users/pavlodudenkov/Desktop/learning/RAG-HW/HW2/index/faiss.index
Index ready   : 240 vectors, dim=384

Loading reranker: cross-encoder/ms-marco-MiniLM-L-6-v2
Question: How do I set sag on my mountain bike fork?

Route: knowledge_base_workflow

Nodes executed: classify_request -> knowledge_base_workflow

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

Question: Tell me something interesting about mountain biking.

Route: clarification

Nodes executed: classify_request -> clarification

Final state:
{
  "user_question": "Tell me something interesting about mountain biking.",
  "selected_route": "clarification",
  "extracted_slots": null,
  "tool_calls": [],
  "observations": [],
  "final_answer": "Could you please clarify your question? Are you asking about current/forecast weather and riding conditions, a specific part's manual or spec sheet, or a general how-to/maintenance question?"
}

Final answer:
Could you please clarify your question? Are you asking about current/forecast weather and riding conditions, a specific part's manual or spec sheet, or a general how-to/maintenance question?

---

