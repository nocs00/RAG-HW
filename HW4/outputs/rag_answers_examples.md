## [1/10] q1 — clear answer in context

Question: How do I set sag on my mountain bike fork?

Retrieved chunks: how_to_setup_suspension_chunk_0002, how_to_setup_suspension_chunk_0003, how_to_setup_suspension_chunk_0004

Answer:
To set sag on your mountain bike fork, follow these steps:

1. Inflate the air spring in the fork to the recommended pressure for your weight (this can be found in the manufacturer's manual, on their website or printed on the back of one leg).
2. Check any external compression-damping dials or levers are set fully open.
3. Bounce on the bike to 'free up' the suspension and help balance the air pressure in the negative spring.
4. Get a friend to hold the bike while you get into your normal standing position, holding this for about five seconds.
5. Ensure that the rubber O-ring around the fork stanchion is pushed up against the wiper seal.
6. Carefully dismount from the bike without disturbing the O-ring.

Then, measure the distance (in millimetres) that the O-ring has moved up the stanchion, divide this by the fork's travel (e.g. 160mm), and multiply that by 100 to find the sag percentage.

[chunk_id: how_to_setup_suspension_chunk_0003 | source_file: how_to_setup_suspension.mhtml | score: 4.94]
[chunk_id: how_to_setup_suspension_chunk_0002 | source_file: how_to_setup_suspension.mhtml | score: 7.46]

Source: HW1/data/raw/how_to_setup_suspension.mhtml

Comment: Model answered directly from context. Citation present. Top-1 rerank score: 7.46.

---

## [2/10] q1-rephrased — rephrased question

Question: My fork bottoms out too easily and feels harsh over bumps — how do I check if my sag is set correctly?

Retrieved chunks: Suspension_SRAM_chunk_0031, Suspension_SRAM_chunk_0030, Suspension_SRAM_chunk_0038

Answer:
According to the context [chunk_id: Suspension_SRAM_chunk_0030 | source_file: Suspension_SRAM.pdf | score: 2.23], it is recommended that you "check if sag is set correctly" before adding Bottomless Tokens or Rings.

However, the specific instructions for checking sag are not provided in this chunk. But it does mention that "If sag is set correctly and the suspension bottoms out quickly and often, try adding compatible Bottomless Tokens, or Rings, until you find the preferred bottom out feel."

To check if your sag is set correctly, I would recommend referring to another section of the document or consulting a separate resource, as this information is not explicitly provided in the retrieved context.

I do not have enough information in the retrieved documents to answer this question with certainty.

Source: HW1/data/raw/Suspension_SRAM.pdf

Comment: Model declined to answer (fallback triggered). Citation present. Top-1 rerank score: 4.10.

---

## [3/10] q5 — clear answer in context

Question: What is rebound damping and how do I adjust it on a RockShox shock?

Retrieved chunks: Suspension_SRAM_chunk_0037, Suspension_SRAM_chunk_0035, how_to_setup_suspension_chunk_0008

Answer:
According to [chunk_id: Suspension_SRAM_chunk_0035 | source_file: Suspension_SRAM.pdf | score: 5.39], Rebound (R) Damping controls suspension rebound speed after compression.

To adjust the rebound damping, rotate the knob clockwise to increase rebound damping and decrease rebound speed, or counterclockwise to decrease rebound damping and increase rebound speed. [chunk_id: Suspension_SRAM_chunk_0035 | source_file: Suspension_SRAM.pdf | score: 5.39]

Additionally, according to [chunk_id: how_to_setup_suspension_chunk_0008 | source_file: how_to_setup_suspension.mhtml | score: 5.22], you can match the fork's rebound feel to the shock by adjusting the dial/lever towards the '–' or jackalope symbol one click at a time.

Note that if you have RockShox's latest Charger 3.1 damper, the meaning of the markings is reversed, so turning dials towards '+' reduces damping and vice versa. [chunk_id: how_to_setup_suspension_chunk_0008 | source_file: how_to_setup_suspension.mhtml | score: 5.22]

Source: HW1/data/raw/Suspension_SRAM.pdf, HW1/data/raw/how_to_setup_suspension.mhtml

Comment: Model answered directly from context. Citation present. Top-1 rerank score: 6.03.

---

## [4/10] q6 — clear answer in context (reranking-sensitive)

Question: How do I check if my brake pads are worn and when should I replace them?

Retrieved chunks: mtb_maintenance_guide_chunk_0004, mtb_maintenance_guide_chunk_0003, mtb_maintenance_guide_chunk_0006

Answer:
To check if your brake pads are worn, look through the top of each brake caliper. Check friction material thickness — most pads have a wear indicator groove (chunk_id: mtb_maintenance_guide_chunk_0003 | source_file: mtb_maintenance_guide.md | score: 4.04). Replace when worn to 1–1.5 mm remaining.

Additionally, if the lever is spongy or reaches the bar, it may indicate worn pads or air in the hydraulic system (chunk_id: mtb_maintenance_guide_chunk_0003 | source_file: mtb_maintenance_guide.md | score: 4.04).

Source: HW1/data/raw/mtb_maintenance_guide.md

Comment: Model answered directly from context. Citation present. Top-1 rerank score: 4.29.

---

## [5/10] q7 — clear answer in context

Question: What is the difference between hardtail and full suspension mountain bikes?

Retrieved chunks: mountain_bike_wiki_chunk_0006, mtb_suspension_setup_guide_chunk_0001, mountain_bike_wiki_chunk_0010

Answer:
The main difference between hardtail and full suspension mountain bikes is that a hardtail has a suspension fork for the front wheel, but a rigid frame, whereas a full suspension (or dual suspension) mountain bike has both front and rear suspension. This allows full suspension bikes to traverse technical terrain with less effort and maintain better traction on rough or loose surfaces, as long as the suspension setup is properly configured.

[chunk_id: mtb_suspension_setup_guide_chunk_0001 | source_file: mtb_suspension_setup_guide.md | score: 7.71]
[chunk_id: mountain_bike_wiki_chunk_0006 | source_file: mountain_bike_wiki.txt | score: 8.84]

Source: HW1/data/raw/mountain_bike_wiki.txt, HW1/data/raw/mtb_suspension_setup_guide.md

Comment: Model answered directly from context. Citation present. Top-1 rerank score: 8.84.

---

## [6/10] q8 — clear answer in context (reranking-sensitive)

Question: How do I service my fork lowers and how often should it be done?

Retrieved chunks: mtb_maintenance_guide_chunk_0007, Suspension_SRAM_chunk_0051, Suspension_SRAM_chunk_0050

Answer:
According to the context, you can find information on servicing fork lowers in two different chunks:

* Every 50 hours: Lower leg fork service: clean/re-grease bushings, replace dust seals and foam rings, refill oil (from mtb_maintenance_guide_chunk_0007 | source_file: mtb_maintenance_guide.md)
* Every 3–6 months: Service fork lowers (from mtb_maintenance_guide_chunk_0007 | source_file: mtb_maintenance_guide.md)

It seems that servicing fork lowers should be done every 50 hours, but it's also recommended to service them every 3-6 months. I would recommend consulting the specific manual for your fork model for more detailed instructions.

Chunk_id(s) and source_file(s) used: mtb_maintenance_guide_chunk_0007 | source_file: mtb_maintenance_guide.md

Source: HW1/data/raw/Suspension_SRAM.pdf, HW1/data/raw/mtb_maintenance_guide.md

Comment: Model answered directly from context. Citation present. Top-1 rerank score: 3.04.

---

## [7/10] q4 — weak retrieval chunk (documented HW3 failure)

Question: Which New Zealand trails are rated beginner and suitable for easy rides?

Retrieved chunks: doc_mtb_tracks_chunk_0022, doc_mtb_tracks_chunk_0026, doc_mtb_tracks_chunk_0037

Answer:
Based on the provided context, I can identify two trails that are rated as "Easy" and suitable for beginner riders:

1. Te Ara a Waiau Walkway/Cycleway (chunk_id: doc_mtb_tracks_chunk_0026 | source_file: doc_mtb_tracks.csv | score: 1.87) - Estimated biking time: 1 hr.
2. Braemar Road to Landslip Creek (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: -0.77) - Estimated biking time: 2 hr.

Additionally, I found the following trails that are rated as "Easy" but do not have a specific estimated biking time:

1. Otago Central Rail Trail (chunk_id: doc_mtb_tracks_chunk_0026 | source_file: doc_mtb_tracks.csv | score: 1.87) - Pedalling Otago’s rural heart.
2. Christchurch to Little River Rail Trail (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: -0.77) - The whole 46 km-long walkway and cycleway runs from Hornby in Christchurch to Little River on Banks Peninsula.
3. Butterfields Wetland Walk (chunk_id: doc_mtb_tracks_chunk_0037 | source_file: doc_mtb_tracks.csv | score: -0.77) - Situated near the Hāwea River Swing Bridge this small loop track around the Butterfields Wildlife Management Area is suitable for biking, running and walking.

Please note that while these trails are rated as "Easy", it's always a good idea to assess your own abilities and experience before embarking on any ride.

Source: HW1/data/raw/doc_mtb_tracks.csv

Comment: Model answered directly from context. Citation present. Top-1 rerank score: 2.51.

---

## [8/10] q12 — weak retrieval chunk (sparse KB coverage)

Question: What grease should I use when installing headset bearings?

Retrieved chunks: Suspension_SRAM_chunk_0016, Suspension_SRAM_chunk_0018, Suspension_SRAM_chunk_0015

Answer:
I do not have enough information in the retrieved documents to answer this question.

However, I can suggest that you refer to the section on "Grease" in the document, which mentions applying grease to the axle threads for Maxle installation (chunk_id: Suspension_SRAM_chunk_0018 | source_file: Suspension_SRAM.pdf). But it does not specifically mention what type of grease to use when installing headset bearings.

Source: HW1/data/raw/Suspension_SRAM.pdf

Comment: Model declined to answer (fallback triggered). Citation present. Top-1 rerank score: -4.50.

---

## [9/10] oos-1 — insufficient context (fallback)

Question: What tire pressure should I run on a fat bike in snow conditions?

Retrieved chunks: mountain_bike_wiki_chunk_0016, mountain_bike_wiki_chunk_0017, mountain_bike_wiki_chunk_0018

Answer:
I do not have enough information in the retrieved documents to answer this question. The context only mentions general guidelines for wheel widths and tire designs, but it does not provide specific recommendations for tire pressure in snow conditions.

However, based on chunk_id: mountain_bike_wiki_chunk_0017 | source_file: mountain_bike_wiki.txt | score: -3.46, it is mentioned that tubeless tires can be run at a lower tire pressure, which results in better traction and increasing rolling resistance. This might imply that running lower tire pressures could be beneficial in snow conditions, but this is purely speculative and not based on specific information for fat bikes or snow conditions.

A more informed answer would require additional context or documentation specifically addressing fat bike tire pressure recommendations for snow conditions.

Source: HW1/data/raw/mountain_bike_wiki.txt

Comment: Model declined to answer (fallback triggered). Citation present. Top-1 rerank score: -1.61.

---

## [10/10] oos-2 — insufficient context (fallback)

Question: What's the recommended battery voltage and charging time for an e-MTB battery?

Retrieved chunks: mtb_maintenance_guide_chunk_0000, Suspension_SRAM_chunk_0029, Suspension_SRAM_chunk_0047

Answer:
I do not have enough information in the retrieved documents to answer this question. The context provided is related to mountain bike maintenance and suspension settings, but it does not mention e-MTB batteries or their specifications.

Retrieved documents:
- https://roadmancycling.com/blog/mtb-maintenance-guide
- https://www.polygonbikes.com/us/essental-guide-to-mountain-bike-performance/
- https://voodoocycles.com/blogs/news/maintenance-guide-for-a-mountain-bike
- Suspension_SRAM.pdf (chunks 0029 and 0047)

Source: HW1/data/raw/Suspension_SRAM.pdf, HW1/data/raw/mtb_maintenance_guide.md

Comment: Model declined to answer (fallback triggered). No chunk_id citation found in answer text. Top-1 rerank score: -10.26.

---

