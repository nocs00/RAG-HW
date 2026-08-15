# HW5 — External Tool Examples

## case-1-current-weather

User question: Is it a good day to ride the trails in Queenstown, New Zealand today?

Tool called: get_trail_weather

Input: {"days_ahead": "0", "location": "Queenstown, New Zealand"}

Result: {"location": "Queenstown, New Zealand", "resolved_place": "Queenstown, New Zealand", "coordinates": {"lat": -45.03023, "lon": 168.6627}, "date": "2026-08-16", "temperature_max_c": 7.4, "temperature_min_c": 0.3, "precipitation_mm": 0.0, "wind_speed_max_kmh": 2.6, "weather_description": "Overcast", "riding_conditions_note": "Good riding conditions expected."}

Final answer:
It's a good day to ride the trails in Queenstown, New Zealand today! The weather is overcast with a high of 7.4°C and low of 0.3°C, with no precipitation expected. The wind speed is relatively calm at 2.6 km/h.

Why tool is better than retrieval:
Weather is live, hourly-changing data. A static knowledge base snapshot would go stale within hours and could never answer 'today' correctly -- a tool that queries a live source is the only correct approach.

---

## case-2-forecast

User question: What's the forecast for Rotorua, New Zealand 3 days from now -- should I plan a ride?

Tool called: get_trail_weather

Input: {"days_ahead": "3", "location": "Rotorua, New Zealand"}

Result: {"location": "Rotorua, New Zealand", "resolved_place": "Rotorua, New Zealand", "coordinates": {"lat": -38.13874, "lon": 176.24516}, "date": "2026-08-19", "temperature_max_c": 10.3, "temperature_min_c": 4.4, "precipitation_mm": 0.0, "wind_speed_max_kmh": 27.9, "weather_description": "Partly cloudy", "riding_conditions_note": "Good riding conditions expected."}

Final answer:
Based on the forecast, it appears that you should plan a ride for Rotorua, New Zealand in three days. The weather is expected to be partly cloudy with good riding conditions. However, please note that this is just a forecast and actual conditions may vary. It's always a good idea to check the latest updates before heading out on your ride.

Why tool is better than retrieval:
This requires a specific future forecast date. Retrieval over static documents has no concept of 'in 3 days' at all -- there is nothing to retrieve; only a live forecast API can answer this.

---

Loading model : sentence-transformers/all-MiniLM-L6-v2
Loading index : /Users/pavlodudenkov/Desktop/learning/RAG-HW/HW2/index/faiss.index
Index ready   : 240 vectors, dim=384

Loading reranker: cross-encoder/ms-marco-MiniLM-L-6-v2
## case-3-static-question

User question: How do I set sag on my mountain bike fork?

Tool called: search_knowledge_base

Input: {"query": "mountain bike fork sag setup"}

Result: {"answer": "To set the sag on your mountain bike fork, follow these steps:\n\n1. Inflate the air spring in the fork to the recommended pressure for your weight, which can be found in the manufacturer's manual or on their website (chunk_id: how_to_setup_suspension_chunk_0002 | source_file: how_to_setup_suspension.mhtml).\n\nNote that sag is defined as the travel consumed simply by sitting on the bike, and ideally you should compress 25-35% of total travel when seated (chunk_id: mtb_suspension_setup_guide_chunk_0001 | source_file: mtb_suspension_setup_guide.md).", "chunk_ids": ["how_to_setup_suspension_chunk_0002", "mtb_suspension_setup_guide_chunk_0001", "how_to_setup_suspension_chunk_0000"], "sources": ["how_to_setup_suspension.mhtml", "mtb_suspension_setup_guide.md"]}

Final answer:
To set the sag on your mountain bike fork, follow these steps:

1. Inflate the air spring in the fork to the recommended pressure for your weight, which can be found in the manufacturer's manual or on their website (chunk_id: how_to_setup_suspension_chunk_0002 | source_file: how_to_setup_suspension.mhtml).

Note that sag is defined as the travel consumed simply by sitting on the bike, and ideally you should compress 25-35% of total travel when seated (chunk_id: mtb_suspension_setup_guide_chunk_0001 | source_file: mtb_suspension_setup_guide.md).

Why tool is better than retrieval:
This is a static how-to question already covered by the HW1-4 knowledge base. Demonstrates the orchestration layer correctly choosing search_knowledge_base over get_trail_weather -- the tool is available but not the right one here.

---

## case-4-out-of-range-forecast

User question: What will the weather be like in Queenstown, New Zealand in 2 weeks?

Tool called: get_trail_weather

Input: {"days_ahead": "14", "location": "Queenstown, New Zealand"}

Result: {"error": "Value error, days_ahead must be between 0 and 7 (Open-Meteo daily forecast horizon used here)"}

Final answer:
Since the tool has a limitation of only being able to look ahead 7 days, I'll have to use another tool to find more general information about Queenstown's weather. 

However, since you asked for the weather in 2 weeks, which is beyond the 7-day limit, I will answer directly:

Unfortunately, with this tool, I can't provide a specific forecast for 2 weeks from now. However, I can suggest that you check a general weather website or app for more information.

If you'd like to know the current weather in Queenstown, I can try to help with that!

Why tool is better than retrieval:
Demonstrates validation rejecting an out-of-contract value: the model naturally asks for a ~14-day-ahead forecast, which violates the days_ahead <= 7 rule enforced before any network call is made, rather than silently returning wrong data or crashing on an out-of-bounds array index.

---

## case-5-unresolvable-location

User question: What's the current weather in Xyzzyplaceville?

Tool called: get_trail_weather

Input: {"location": "Xyzzyplaceville", "days_ahead": "0"}

Result: {"error": "Could not resolve location: 'Xyzzyplaceville'"}

Final answer:
It seems like the location "Xyzzyplaceville" is not recognized. Can you please provide a valid location or trail name? I'll be happy to help with the current weather conditions.

Why tool is better than retrieval:
Demonstrates graceful handling of a genuine external-source failure (the geocoding API can't resolve a nonexistent place) -- the tool returns a structured error instead of crashing, and the model relays that honestly instead of inventing a forecast.

---

## case-6-part-manual-lookup

User question: Where can I find the official service manual for a RockShox Pike Ultimate 2023 fork?

Tool called: search_part_manual

Input: {"max_results": "5", "query": "RockShox Pike Ultimate 2023 service manual"}

Result: {"query": "RockShox Pike Ultimate 2023 service manual", "results": [{"title": "Pike Ultimate | FS-PIKE-ULT-C1 | RockShox | Service", "url": "https://www.sram.com/en/service/models/fs-pike-ult-c1", "snippet": "Model ID: FS-PIKE-ULT-C1 \u00b7 Product Page \u00b7 Show All Available Languages \u00b7 RockShox Suspension User Manual \u00b7 Language: English, \u7b80\u4f53\u4e2d\u6587, \u010cesk\u00fd Jazyk, Dansk, Nederlands, Fran\u00e7ais, Deutsch, \u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac, Italiano, \u65e5\u672c\u8a9e, J\u0119zyk polski, Portugu\u00eas, Rom\u00e2n\u0103, Espa\u00f1ol \u00b7 2023 Front Suspension Oil Air Coil Token Specifications English \u00b7"}, {"title": "Pike Ultimate | FS-PIKE-ULT-B3 | RockShox | Service", "url": "https://www.sram.com/en/service/models/fs-pike-ult-b3", "snippet": "RockShox Suspension User Manual \u00b7 Language: English, \u7b80\u4f53\u4e2d\u6587, \u010cesk\u00fd Jazyk, Dansk, Nederlands, Fran\u00e7ais, Deutsch, \u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac, Italiano, \u65e5\u672c\u8a9e, J\u0119zyk polski, Portugu\u00eas, Rom\u00e2n\u0103, Espa\u00f1ol \u00b7 2019-2022 Pike 2019-2023 Revelation Manual de Mantenimiento \u00b7"}, {"title": "Pike Ultimate | FS-PIKE-ULT-C2 | RockShox | Service", "url": "https://www.sram.com/en/service/models/fs-pike-ult-c2", "snippet": "Model ID: FS-PIKE-ULT-C2 \u00b7 Product Page \u00b7 Show All Available Languages \u00b7 RockShox Suspension User Manual \u00b7 Language: English, \u7b80\u4f53\u4e2d\u6587, \u010cesk\u00fd Jazyk, Dansk, Nederlands, Fran\u00e7ais, Deutsch, \u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac, Italiano, \u65e5\u672c\u8a9e, J\u0119zyk polski, Portugu\u00eas, Rom\u00e2n\u0103, Espa\u00f1ol \u00b7 2023 ZEB Lyrik Pike Manual de Mantenimiento \u00b7"}, {"title": "RockShox 2023 ZEB, Lyrik, Pike Service Manual - Maintenance and Repair Guide", "url": "https://manuals.plus/m/bdfdb761307247e88f4046880605f24212c8c176f3fcab8d7f8e57bf6f1dd65d", "snippet": "November 3, 2025 - Comprehensive service manual for RockShox 2023 ZEB, Lyrik, and Pike suspension forks. Includes detailed maintenance procedures, exploded views, parts lists, torque values, and tro\u2026"}, {"title": "SERVICE MANUAL GEN.0000000007197 Rev C \u00a9 2024 SRAM, LLC 2019-2022 PIKE", "url": "https://www.sram.com/globalassets/document-hierarchy/service-manuals/rockshox/front-suspension/2019-2022-pike-2019-2023-revelation-service-manual.pdf", "snippet": "2019-2022 PIKE \u00b7 2019-2023 REVELATION \u00b7 SAFETY FIRST! We care about YOU. Please, always wear your safety glasses \u00b7 and protective gloves when servicing RockShox products. Protect yourself! Wear your safety gear! \u26a0WARNING - PRESSURIZED DEVICE \u00b7 Suspension products may contain pressurized air, nitrogen, springs, and oil."}]}

Final answer:
The official service manual for a RockShox Pike Ultimate 2023 fork can be found on the SRAM website. The correct model ID is FS-PIKE-ULT-C1, and the manual can be accessed through this link: https://www.sram.com/en/service/models/fs-pike-ult-c1

Why tool is better than retrieval:
The knowledge base's suspension chunks are generic setup/maintenance guides -- they don't (and can't) contain the official per-model service manual for every fork SRAM has ever sold. A specific product model is exactly the kind of long-tail, ever-growing catalog that a live web lookup handles and a fixed KB snapshot never will.

---

## case-7-part-manual-different-model

User question: I need the spare parts catalog for a SRAM GX Eagle rear derailleur.

Tool called: search_part_manual

Input: {"max_results": "3", "query": "SRAM GX Eagle rear derailleur spare parts catalog"}

Result: {"query": "SRAM GX Eagle rear derailleur spare parts catalog", "results": [{"title": "GX Eagle Rear Derailleur - RD-GX-1-B2 - SRAM - Service", "url": "https://www.sram.com/en/service/models/rd-gx-1-b2", "snippet": "GX Eagle Rear Derailleur Model ID: RD-GX-1-B2 Product Page"}, {"title": "Sram Gx Eagle Replacement Parts - The Pro's Closet", "url": "https://www.theproscloset.com/collections/adm-sram-gx-eagle-replacement-parts", "snippet": "Looking for replacement parts for your SRAM GX Eagle drivetrain? Look no further! We have a wide selection of high-quality replacement parts that will keep your drivetrain running smoothly and efficiently. Whether you need a new rear derailleur, chainring, crankset, chain, shifter, or cassette, we've got you covered. Our replacement parts are designed to be durable, reliable, and easy to ..."}, {"title": "SRAM Spare Parts Catalog 2024 | PDF - Scribd", "url": "https://www.scribd.com/document/840213413/2024-Sram-Spare-Parts-Catalog", "snippet": "The 2024 SRAM Spare Parts Catalog provides instructions for locating spare parts using the product's model code and serial number. It includes a comprehensive table of contents detailing various components such as rear and front derailleurs, shifters, brake calipers, and more, along with their respective part numbers and descriptions. Users can access additional support and service ..."}]}

Final answer:
The spare parts catalog for the SRAM GX Eagle rear derailleur is available on the SRAM website at https://www.sram.com/en/service/models/rd-gx-1-b2. You can also find replacement parts on The Pro's Closet website, or access the 2024 SRAM Spare Parts Catalog as a PDF document on Scribd.

Why tool is better than retrieval:
Another specific product model not covered by the ingested documents (HW1's KB has no drivetrain/derailleur source at all) -- demonstrates the router picking the web-lookup tool over both other tools for a product the KB was never built to contain.

---

## case-8-part-manual-validation

User question: Find me the installation instructions for a Shimano XT M8100 crankset, just give me 1 result.

Tool called: search_part_manual

Input: {"max_results": "1", "query": "Shimano XT M8100 crankset service manual"}

Result: {"query": "Shimano XT M8100 crankset service manual", "results": [{"title": "Crankset - SHIMANO", "url": "https://si.shimano.com/en/pdfs/dm/MAFC002/DM-MAFC002-10-ENG.pdf", "snippet": "This dealer's manual is intended primarily for use by professional bicycle mechanics. Users who are not professionally trained for bicycle assembly should not attempt to install the components themselves using the dealer's manuals."}]}

Final answer:
The installation instructions for a Shimano XT M8100 crankset can be found in the official service manual, which is available on the Shimano website at https://si.shimano.com/en/pdfs/dm/MAFC002/DM-MAFC002-10-ENG.pdf.

Why tool is better than retrieval:
Demonstrates the max_results contract in practice: the user's '1 result' phrasing maps to max_results=1 within the tool's 1-5 range, so validation passes through cleanly and the search runs with the requested limit instead of a hardcoded default.

---

