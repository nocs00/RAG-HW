## [1/13] Q1 — Core suspension setup — should hit mtb_suspension_setup_guide and MHTML articles

### Baseline — plain semantic search

**Query:** How do I set sag on my mountain bike fork?

**Top-1:** `how_to_setup_suspension_chunk_0002` | score: **0.69**
- *Text:* The video above shows how our former resident suspension guru, Seb Stott, set up his bikes. It should get your suspensio...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-2:** `how_to_setup_suspension_chunk_0004` | score: **0.62**
- *Text:* 50mm), then multiply that by 100 to find the sag percentage. Helpfully, this is already marked on RockShox forks and sho...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-3:** `bicycle_suspension_wiki_chunk_0050` | score: **0.57**
- *Text:* Sag refers to how much a suspension moves under just the static load of the rider. Sag is often used as one parameter wh...
- *Source:* `HW1/data/raw/bicycle_suspension_wiki.txt`

> **Conclusion:** **Relevant**. Scores: **0.69** / **0.62** / **0.57**. Cross-source: `how_to_setup_suspension`, `bicycle_suspension_wiki`.

### Metadata filtering — `source_type=mhtml`

**Query:** How do I set sag on my mountain bike fork?

**Why:** Limit to MHTML articles (BikeRadar, Trek) — best suspension setup guides  
**Pool:** 240 → **35** chunks

**Top-1:** `how_to_setup_suspension_chunk_0002` | score: **0.69**
- *Text:* The video above shows how our former resident suspension guru, Seb Stott, set up his bikes. It should get your suspensio...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-2:** `how_to_setup_suspension_chunk_0004` | score: **0.62**
- *Text:* 50mm), then multiply that by 100 to find the sag percentage. Helpfully, this is already marked on RockShox forks and sho...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-3:** `how_to_setup_suspension_chunk_0009` | score: **0.51**
- *Text:* If your settings are correct but you can’t reach full travel, try removing any volume spacers, one at a time. Remember t...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** Search space: **240 → 35** chunks. **1 new chunk(s)** surfaced. **1 baseline chunk(s)** replaced. Top-1 score: **0.69 → 0.69** (+0.00). Sources: [`how_to_setup_suspension`, `bicycle_suspension_wiki`] → [`how_to_setup_suspension`].

### Hybrid search — `60% semantic + 40% BM25`

**Query:** How do I set sag on my mountain bike fork?

**Top-1:** `how_to_setup_suspension_chunk_0002` | score: **0.75**
- *Text:* The video above shows how our former resident suspension guru, Seb Stott, set up his bikes. It should get your suspensio...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-2:** `how_to_setup_suspension_chunk_0004` | score: **0.54**
- *Text:* 50mm), then multiply that by 100 to find the sag percentage. Helpfully, this is already marked on RockShox forks and sho...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-3:** `how_to_setup_suspension_chunk_0019` | score: **0.53**
- *Text:* Best mountain bike forks 2026: top-rated MTB suspension forks and buyer's guide 9/12/2025  Plus our buyer's guide to MTB...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. **Top-1 unchanged.** **1 new chunk(s)** promoted via BM25. Sources: [`how_to_setup_suspension`, `bicycle_suspension_wiki`] → [`how_to_setup_suspension`].

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** How do I set sag on my mountain bike fork?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `how_to_setup_suspension_chunk_0002` | score: **7.46**
- *Text:* The video above shows how our former resident suspension guru, Seb Stott, set up his bikes. It should get your suspensio...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-2:** `how_to_setup_suspension_chunk_0003` | score: **4.94**
- *Text:* This can be found in the manufacturer’s manual, on their website or, often in the case of forks, printed on the back of ...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-3:** `how_to_setup_suspension_chunk_0004` | score: **3.57**
- *Text:* 50mm), then multiply that by 100 to find the sag percentage. Helpfully, this is already marked on RockShox forks and sho...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. **Top-1 unchanged.** **1 chunk(s)** reordered. **1 new chunk(s)** promoted from outside baseline top-3.

---

## [2/13] Q2 — Assembly / torque specs — should hit Trek PDF and SRAM manual

### Baseline — plain semantic search

**Query:** What torque should I use when assembling a carbon steerer tube?

**Top-1:** `Suspension_SRAM_chunk_0016` | score: **0.51**
- *Text:* Star Nut Set Tool Depth = 15 mm (0.6 in) 4-5. Use a star nut setter to install a star nut 15 mm (0.6 inches) into the st...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0015` | score: **0.42**
- *Text:* If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0000` | score: **0.42**
- *Text:* Suspension User Manual Tools and Supplies Single Crown Fork Installation Aluminum and Steel Steerer Tube Hub End Cap Ada...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** **Partially relevant**. Scores: **0.51** / **0.42** / **0.42**. All top-3 from one source (`Suspension_SRAM`).

### Metadata filtering — `source_type=pdf`

**Query:** What torque should I use when assembling a carbon steerer tube?

**Why:** Limit to PDF manuals — torque specs live in technical manuals (SRAM, Trek)  
**Pool:** 240 → **60** chunks

**Top-1:** `Suspension_SRAM_chunk_0016` | score: **0.51**
- *Text:* Star Nut Set Tool Depth = 15 mm (0.6 in) 4-5. Use a star nut setter to install a star nut 15 mm (0.6 inches) into the st...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0015` | score: **0.42**
- *Text:* If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0000` | score: **0.42**
- *Text:* Suspension User Manual Tools and Supplies Single Crown Fork Installation Aluminum and Steel Steerer Tube Hub End Cap Ada...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** Search space: **240 → 60** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** What torque should I use when assembling a carbon steerer tube?

**Top-1:** `Suspension_SRAM_chunk_0016` | score: **0.71**
- *Text:* Star Nut Set Tool Depth = 15 mm (0.6 in) 4-5. Use a star nut setter to install a star nut 15 mm (0.6 inches) into the st...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0015` | score: **0.64**
- *Text:* If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0000` | score: **0.54**
- *Text:* Suspension User Manual Tools and Supplies Single Crown Fork Installation Aluminum and Steel Steerer Tube Hub End Cap Ada...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Order **unchanged** — keyword scores aligned with semantic ranking.

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** What torque should I use when assembling a carbon steerer tube?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `Suspension_SRAM_chunk_0000` | score: **-1.96**
- *Text:* Suspension User Manual Tools and Supplies Single Crown Fork Installation Aluminum and Steel Steerer Tube Hub End Cap Ada...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0016` | score: **-2.17**
- *Text:* Star Nut Set Tool Depth = 15 mm (0.6 in) 4-5. Use a star nut setter to install a star nut 15 mm (0.6 inches) into the st...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0015` | score: **-3.24**
- *Text:* If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `Suspension_SRAM_chunk_0016` → **`Suspension_SRAM_chunk_0000`**. **3 chunk(s)** reordered.

---

## [3/13] Q3 — Drivetrain maintenance — should hit mtb_maintenance_guide

### Baseline — plain semantic search

**Query:** How often should I lube my chain and what type of lube should I use in wet conditions?

**Top-1:** `mtb_maintenance_guide_chunk_0008` | score: **0.47**
- *Text:* - Track your ride hours using a GPS unit or app (Strava, TrailForks) to schedule service based on actual use, not just c...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `mtb_maintenance_guide_chunk_0003` | score: **0.43**
- *Text:* Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: - Wet lube for wet/mu...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-3:** `mtb_maintenance_guide_chunk_0002` | score: **0.41**
- *Text:* 1. Rinse the Bike (3 min) Use a garden hose with moderate pressure — avoid pressure washers, which force water past seal...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

> **Conclusion:** **Partially relevant**. Scores: **0.47** / **0.43** / **0.41**. All top-3 from one source (`mtb_maintenance_guide`).

### Metadata filtering — `document_id=mtb_maintenance_guide`

**Query:** How often should I lube my chain and what type of lube should I use in wet conditions?

**Why:** Limit to mtb_maintenance_guide — only source with drivetrain lube advice  
**Pool:** 240 → **11** chunks

**Top-1:** `mtb_maintenance_guide_chunk_0008` | score: **0.47**
- *Text:* - Track your ride hours using a GPS unit or app (Strava, TrailForks) to schedule service based on actual use, not just c...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `mtb_maintenance_guide_chunk_0003` | score: **0.43**
- *Text:* Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: - Wet lube for wet/mu...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-3:** `mtb_maintenance_guide_chunk_0002` | score: **0.41**
- *Text:* 1. Rinse the Bike (3 min) Use a garden hose with moderate pressure — avoid pressure washers, which force water past seal...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

> **Conclusion:** Search space: **240 → 11** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** How often should I lube my chain and what type of lube should I use in wet conditions?

**Top-1:** `mtb_maintenance_guide_chunk_0003` | score: **0.64**
- *Text:* Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: - Wet lube for wet/mu...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `mtb_maintenance_guide_chunk_0008` | score: **0.63**
- *Text:* - Track your ride hours using a GPS unit or app (Strava, TrailForks) to schedule service based on actual use, not just c...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-3:** `mtb_maintenance_guide_chunk_0002` | score: **0.62**
- *Text:* 1. Rinse the Bike (3 min) Use a garden hose with moderate pressure — avoid pressure washers, which force water past seal...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `mtb_maintenance_guide_chunk_0008` → **`mtb_maintenance_guide_chunk_0003`**. **2 chunk(s)** reordered by keyword boost.

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** How often should I lube my chain and what type of lube should I use in wet conditions?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `mtb_maintenance_guide_chunk_0003` | score: **0.45**
- *Text:* Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: - Wet lube for wet/mu...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `mtb_maintenance_guide_chunk_0008` | score: **-0.34**
- *Text:* - Track your ride hours using a GPS unit or app (Strava, TrailForks) to schedule service based on actual use, not just c...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-3:** `mtb_maintenance_guide_chunk_0002` | score: **-1.70**
- *Text:* 1. Rinse the Bike (3 min) Use a garden hose with moderate pressure — avoid pressure washers, which force water past seal...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `mtb_maintenance_guide_chunk_0008` → **`mtb_maintenance_guide_chunk_0003`**. **2 chunk(s)** reordered.

---

## [4/13] Q4 — Trail data query — should hit doc_mtb_tracks CSV chunks

### Baseline — plain semantic search

**Query:** Which New Zealand trails are rated beginner and suitable for easy rides?

**Top-1:** `doc_mtb_tracks_chunk_0026` | score: **0.66**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0022` | score: **0.65**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0024` | score: **0.63**
- *Text:* This trail offers challenging, mixed riding through stunning scenery of mountain peaks, crystal clear waters, high count...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** **Relevant**. Scores: **0.66** / **0.65** / **0.63**. All top-3 from one source (`doc_mtb_tracks`).

### Metadata filtering — `document_id=doc_mtb_tracks`

**Query:** Which New Zealand trails are rated beginner and suitable for easy rides?

**Why:** Limit to doc_mtb_tracks CSV — only source with NZ trail data  
**Pool:** 240 → **40** chunks

**Top-1:** `doc_mtb_tracks_chunk_0026` | score: **0.66**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0022` | score: **0.65**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0024` | score: **0.63**
- *Text:* This trail offers challenging, mixed riding through stunning scenery of mountain peaks, crystal clear waters, high count...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** Search space: **240 → 40** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** Which New Zealand trails are rated beginner and suitable for easy rides?

**Top-1:** `doc_mtb_tracks_chunk_0022` | score: **0.75**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0011` | score: **0.73**
- *Text:* Estimated biking time: 1 hr return. This is a short tramping track through the protected historic site in the impressive...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0028` | score: **0.71**
- *Text:* Difficulty: Intermediate. This popular walk takes you on a loop around the lake. Superb views are on offer as you travel...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `doc_mtb_tracks_chunk_0026` → **`doc_mtb_tracks_chunk_0022`**. **1 chunk(s)** reordered by keyword boost. **2 new chunk(s)** promoted via BM25.

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** Which New Zealand trails are rated beginner and suitable for easy rides?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `doc_mtb_tracks_chunk_0022` | score: **2.51**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0026` | score: **1.87**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0037` | score: **-0.77**
- *Text:* Difficulty: Expert. Walk or mountain bike between Fletcher Bay and Stony Bay. Cloudy Peak Track. Difficulty: Advanced. T...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `doc_mtb_tracks_chunk_0026` → **`doc_mtb_tracks_chunk_0022`**. **2 chunk(s)** reordered. **1 new chunk(s)** promoted from outside baseline top-3.

---

## [5/13] Q5 — Rebound tuning — should hit SRAM manual and suspension setup guides

### Baseline — plain semantic search

**Query:** What is rebound damping and how do I adjust it on a RockShox shock?

**Top-1:** `how_to_setup_suspension_chunk_0007` | score: **0.72**
- *Text:* Ian Linton / Our Media Rebound damping controls how quickly your suspension resets after absorbing an impact and should ...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-2:** `how_to_setup_suspension_chunk_0008` | score: **0.72**
- *Text:* Session the trail section and decrease the damping – by turning the dial/lever towards the ‘-’ or jackalope (hare) symbo...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-3:** `how_to_setup_suspension_chunk_0006` | score: **0.67**
- *Text:* Andy Lloyd / Our Media Damping is a typically oil-based system that controls how fast the spring compresses and rebounds...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** **Highly relevant**. Scores: **0.72** / **0.72** / **0.67**. All top-3 from one source (`how_to_setup_suspension`).

### Metadata filtering — `source_type=mhtml`

**Query:** What is rebound damping and how do I adjust it on a RockShox shock?

**Why:** Limit to MHTML articles — BikeRadar guide has RockShox-specific damping steps  
**Pool:** 240 → **35** chunks

**Top-1:** `how_to_setup_suspension_chunk_0007` | score: **0.72**
- *Text:* Ian Linton / Our Media Rebound damping controls how quickly your suspension resets after absorbing an impact and should ...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-2:** `how_to_setup_suspension_chunk_0008` | score: **0.72**
- *Text:* Session the trail section and decrease the damping – by turning the dial/lever towards the ‘-’ or jackalope (hare) symbo...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-3:** `how_to_setup_suspension_chunk_0006` | score: **0.67**
- *Text:* Andy Lloyd / Our Media Damping is a typically oil-based system that controls how fast the spring compresses and rebounds...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** Search space: **240 → 35** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** What is rebound damping and how do I adjust it on a RockShox shock?

**Top-1:** `Suspension_SRAM_chunk_0037` | score: **0.78**
- *Text:* For recommended rebound settings refer to RockShox Trailhead. After setting air pressure (DebonAir+) or sag, adjust the ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0036` | score: **0.73**
- *Text:* counterclockwise. Rebound damping controls suspension fork extension/return speed which affects traction and control. Op...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `how_to_setup_suspension_chunk_0007` | score: **0.73**
- *Text:* Ian Linton / Our Media Rebound damping controls how quickly your suspension resets after absorbing an impact and should ...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `how_to_setup_suspension_chunk_0007` → **`Suspension_SRAM_chunk_0037`**. **1 chunk(s)** reordered by keyword boost. **2 new chunk(s)** promoted via BM25. Sources: [`how_to_setup_suspension`] → [`Suspension_SRAM`, `how_to_setup_suspension`].

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** What is rebound damping and how do I adjust it on a RockShox shock?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `Suspension_SRAM_chunk_0037` | score: **6.03**
- *Text:* For recommended rebound settings refer to RockShox Trailhead. After setting air pressure (DebonAir+) or sag, adjust the ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0035` | score: **5.39**
- *Text:* Performance examples illustrated are for conceptual purposes and may vary from actual performance. Rebound (R) Damping -...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `how_to_setup_suspension_chunk_0008` | score: **5.22**
- *Text:* Session the trail section and decrease the damping – by turning the dial/lever towards the ‘-’ or jackalope (hare) symbo...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `how_to_setup_suspension_chunk_0007` → **`Suspension_SRAM_chunk_0037`**. **1 chunk(s)** reordered. **2 new chunk(s)** promoted from outside baseline top-3.

---

## [6/13] Q6 — Brake maintenance — should hit mtb_maintenance_guide post-ride routine section

### Baseline — plain semantic search

**Query:** How do I check if my brake pads are worn and when should I replace them?

**Top-1:** `mtb_maintenance_guide_chunk_0003` | score: **0.61**
- *Text:* Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: - Wet lube for wet/mu...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `mtb_maintenance_guide_chunk_0004` | score: **0.49**
- *Text:* - Replace when worn to 1–1.5 mm remaining - Check rotor scoring by running a finger lightly along the braking surface wh...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-3:** `mtb_maintenance_guide_chunk_0010` | score: **0.46**
- *Text:* | Component | Replace When | |---|---| | Chain | 0.5–0.75% wear (use chain wear tool) | | Brake pads | Less than 1–2 mm ...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

> **Conclusion:** **Relevant**. Scores: **0.61** / **0.49** / **0.46**. All top-3 from one source (`mtb_maintenance_guide`).

### Metadata filtering — `document_id=mtb_maintenance_guide`

**Query:** How do I check if my brake pads are worn and when should I replace them?

**Why:** Limit to mtb_maintenance_guide — brake pad wear thresholds are here  
**Pool:** 240 → **11** chunks

**Top-1:** `mtb_maintenance_guide_chunk_0003` | score: **0.61**
- *Text:* Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: - Wet lube for wet/mu...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `mtb_maintenance_guide_chunk_0004` | score: **0.49**
- *Text:* - Replace when worn to 1–1.5 mm remaining - Check rotor scoring by running a finger lightly along the braking surface wh...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-3:** `mtb_maintenance_guide_chunk_0010` | score: **0.46**
- *Text:* | Component | Replace When | |---|---| | Chain | 0.5–0.75% wear (use chain wear tool) | | Brake pads | Less than 1–2 mm ...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

> **Conclusion:** Search space: **240 → 11** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** How do I check if my brake pads are worn and when should I replace them?

**Top-1:** `mtb_maintenance_guide_chunk_0003` | score: **0.73**
- *Text:* Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: - Wet lube for wet/mu...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `mtb_maintenance_guide_chunk_0004` | score: **0.64**
- *Text:* - Replace when worn to 1–1.5 mm remaining - Check rotor scoring by running a finger lightly along the braking surface wh...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-3:** `mtb_maintenance_guide_chunk_0006` | score: **0.58**
- *Text:* - Drivetrain assessment: Check for shark-fin-shaped teeth on chainring or cassette (sign of wear). Use a chain wear tool...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. **Top-1 unchanged.** **1 new chunk(s)** promoted via BM25.

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** How do I check if my brake pads are worn and when should I replace them?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `mtb_maintenance_guide_chunk_0004` | score: **4.29**
- *Text:* - Replace when worn to 1–1.5 mm remaining - Check rotor scoring by running a finger lightly along the braking surface wh...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `mtb_maintenance_guide_chunk_0003` | score: **4.04**
- *Text:* Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: - Wet lube for wet/mu...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-3:** `mtb_maintenance_guide_chunk_0006` | score: **3.53**
- *Text:* - Drivetrain assessment: Check for shark-fin-shaped teeth on chainring or cassette (sign of wear). Use a chain wear tool...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `mtb_maintenance_guide_chunk_0003` → **`mtb_maintenance_guide_chunk_0004`**. **2 chunk(s)** reordered. **1 new chunk(s)** promoted from outside baseline top-3.

---

## [7/13] Q7 — Bike types comparison — should hit Wikipedia articles

### Baseline — plain semantic search

**Query:** What is the difference between hardtail and full suspension mountain bikes?

**Top-1:** `mountain_bike_wiki_chunk_0006` | score: **0.75**
- *Text:* Mountain bikes can usually be divided into four broad categories based on suspension configuration: Rigid: A mountain bi...
- *Source:* `HW1/data/raw/mountain_bike_wiki.txt`

**Top-2:** `mountain_bike_wiki_chunk_0010` | score: **0.72**
- *Text:* In the past mountain bikes had a rigid frame and fork. In the early 1990s, the first mountain bikes with suspension fork...
- *Source:* `HW1/data/raw/mountain_bike_wiki.txt`

**Top-3:** `bicycle_suspension_wiki_chunk_0044` | score: **0.71**
- *Text:* For this reason, this style of suspension is most popular on more upright styles of bicycle, where the rider spends the ...
- *Source:* `HW1/data/raw/bicycle_suspension_wiki.txt`

> **Conclusion:** **Highly relevant**. Scores: **0.75** / **0.72** / **0.71**. Cross-source: `mountain_bike_wiki`, `bicycle_suspension_wiki`.

### Metadata filtering — `source_type=wikipedia`

**Query:** What is the difference between hardtail and full suspension mountain bikes?

**Why:** Limit to Wikipedia sources — encyclopedic definitions of bike types  
**Pool:** 240 → **87** chunks

**Top-1:** `mountain_bike_wiki_chunk_0006` | score: **0.75**
- *Text:* Mountain bikes can usually be divided into four broad categories based on suspension configuration: Rigid: A mountain bi...
- *Source:* `HW1/data/raw/mountain_bike_wiki.txt`

**Top-2:** `mountain_bike_wiki_chunk_0010` | score: **0.72**
- *Text:* In the past mountain bikes had a rigid frame and fork. In the early 1990s, the first mountain bikes with suspension fork...
- *Source:* `HW1/data/raw/mountain_bike_wiki.txt`

**Top-3:** `bicycle_suspension_wiki_chunk_0044` | score: **0.71**
- *Text:* For this reason, this style of suspension is most popular on more upright styles of bicycle, where the rider spends the ...
- *Source:* `HW1/data/raw/bicycle_suspension_wiki.txt`

> **Conclusion:** Search space: **240 → 87** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** What is the difference between hardtail and full suspension mountain bikes?

**Top-1:** `mountain_bike_wiki_chunk_0010` | score: **0.80**
- *Text:* In the past mountain bikes had a rigid frame and fork. In the early 1990s, the first mountain bikes with suspension fork...
- *Source:* `HW1/data/raw/mountain_bike_wiki.txt`

**Top-2:** `bicycle_suspension_wiki_chunk_0000` | score: **0.75**
- *Text:* Bicycle suspension Bicycle suspension is the system, or systems, used to suspend the rider and bicycle in order to insul...
- *Source:* `HW1/data/raw/bicycle_suspension_wiki.txt`

**Top-3:** `mountain_bike_wiki_chunk_0006` | score: **0.73**
- *Text:* Mountain bikes can usually be divided into four broad categories based on suspension configuration: Rigid: A mountain bi...
- *Source:* `HW1/data/raw/mountain_bike_wiki.txt`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `mountain_bike_wiki_chunk_0006` → **`mountain_bike_wiki_chunk_0010`**. **2 chunk(s)** reordered by keyword boost. **1 new chunk(s)** promoted via BM25.

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** What is the difference between hardtail and full suspension mountain bikes?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `mountain_bike_wiki_chunk_0006` | score: **8.84**
- *Text:* Mountain bikes can usually be divided into four broad categories based on suspension configuration: Rigid: A mountain bi...
- *Source:* `HW1/data/raw/mountain_bike_wiki.txt`

**Top-2:** `mtb_suspension_setup_guide_chunk_0001` | score: **7.71**
- *Text:* Riding a full-suspension mountain bike instead of a hardtail generally allows you to traverse technical terrain with les...
- *Source:* `HW1/data/raw/mtb_suspension_setup_guide.md`

**Top-3:** `mountain_bike_wiki_chunk_0010` | score: **6.65**
- *Text:* In the past mountain bikes had a rigid frame and fork. In the early 1990s, the first mountain bikes with suspension fork...
- *Source:* `HW1/data/raw/mountain_bike_wiki.txt`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. **Top-1 unchanged.** **1 chunk(s)** reordered. **1 new chunk(s)** promoted from outside baseline top-3.

---

## [8/13] Q8 — Fork service interval — should hit maintenance guide (50hr service) and SRAM manual

### Baseline — plain semantic search

**Query:** How do I service my fork lowers and how often should it be done?

**Top-1:** `Suspension_SRAM_chunk_0051` | score: **0.57**
- *Text:* Every ride Clean the dirt and debris from the upper tubes and wiper seals, check air pressure, and inspect upper tubes f...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0050` | score: **0.52**
- *Text:* Never use a high-powered washer to clean the suspension fork. To maintain the high performance, safety, and long life of...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `bicycle_suspension_wiki_chunk_0008` | score: **0.50**
- *Text:* Increasing the volume of the air inside the spring reduces this effect but the volume of the spring is ultimately limite...
- *Source:* `HW1/data/raw/bicycle_suspension_wiki.txt`

> **Conclusion:** **Relevant**. Scores: **0.57** / **0.52** / **0.50**. Cross-source: `Suspension_SRAM`, `bicycle_suspension_wiki`.

### Metadata filtering — `source_type=[pdf, markdown]`

**Query:** How do I service my fork lowers and how often should it be done?

**Why:** Limit to PDF manuals + Markdown guides — fork service procedures and intervals  
**Pool:** 240 → **78** chunks

**Top-1:** `Suspension_SRAM_chunk_0051` | score: **0.57**
- *Text:* Every ride Clean the dirt and debris from the upper tubes and wiper seals, check air pressure, and inspect upper tubes f...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0050` | score: **0.52**
- *Text:* Never use a high-powered washer to clean the suspension fork. To maintain the high performance, safety, and long life of...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0030` | score: **0.49**
- *Text:* Adjust air spring pressure and damper settings as preferred. Bottomless Tokens can be removed or installed to fine-tune ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** Search space: **240 → 78** chunks. **1 new chunk(s)** surfaced. **1 baseline chunk(s)** replaced. Top-1 score: **0.57 → 0.57** (+0.00). Sources: [`Suspension_SRAM`, `bicycle_suspension_wiki`] → [`Suspension_SRAM`].

### Hybrid search — `60% semantic + 40% BM25`

**Query:** How do I service my fork lowers and how often should it be done?

**Top-1:** `how_to_setup_suspension_chunk_0002` | score: **0.59**
- *Text:* The video above shows how our former resident suspension guru, Seb Stott, set up his bikes. It should get your suspensio...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-2:** `Suspension_SRAM_chunk_0050` | score: **0.52**
- *Text:* Never use a high-powered washer to clean the suspension fork. To maintain the high performance, safety, and long life of...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `how_to_setup_suspension_chunk_0019` | score: **0.51**
- *Text:* Best mountain bike forks 2026: top-rated MTB suspension forks and buyer's guide 9/12/2025  Plus our buyer's guide to MTB...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `Suspension_SRAM_chunk_0051` → **`how_to_setup_suspension_chunk_0002`**. **2 new chunk(s)** promoted via BM25. Sources: [`Suspension_SRAM`, `bicycle_suspension_wiki`] → [`how_to_setup_suspension`, `Suspension_SRAM`].

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** How do I service my fork lowers and how often should it be done?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `mtb_maintenance_guide_chunk_0007` | score: **3.04**
- *Text:* | Frequency | Tasks | |---|---| | After every ride | Rinse bike, wipe chain, apply light lube, check tire pressure, tigh...
- *Source:* `HW1/data/raw/mtb_maintenance_guide.md`

**Top-2:** `Suspension_SRAM_chunk_0051` | score: **2.95**
- *Text:* Every ride Clean the dirt and debris from the upper tubes and wiper seals, check air pressure, and inspect upper tubes f...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0050` | score: **-1.00**
- *Text:* Never use a high-powered washer to clean the suspension fork. To maintain the high performance, safety, and long life of...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `Suspension_SRAM_chunk_0051` → **`mtb_maintenance_guide_chunk_0007`**. **2 chunk(s)** reordered. **1 new chunk(s)** promoted from outside baseline top-3.

---

## [9/13] Q9 — Filtered trail query — should hit doc_mtb_tracks chunks with intermediate difficulty

### Baseline — plain semantic search

**Query:** Are there any intermediate difficulty mountain bike tracks in New Zealand longer than 2 hours?

**Top-1:** `doc_mtb_tracks_chunk_0026` | score: **0.74**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0015` | score: **0.67**
- *Text:* Difficulty: Intermediate, Advanced. Rising above Bannockburn and rich in goldmining history, the Carrick Range is one of...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0009` | score: **0.66**
- *Text:* Estimated biking time: 2 hr. This loop track is an extension of the Basin View Tramping Track. It has a 300 m climb  wit...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** **Highly relevant**. Scores: **0.74** / **0.67** / **0.66**. All top-3 from one source (`doc_mtb_tracks`).

### Metadata filtering — `document_id=doc_mtb_tracks`

**Query:** Are there any intermediate difficulty mountain bike tracks in New Zealand longer than 2 hours?

**Why:** Limit to doc_mtb_tracks CSV — only source with NZ trail difficulty data  
**Pool:** 240 → **40** chunks

**Top-1:** `doc_mtb_tracks_chunk_0026` | score: **0.74**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0015` | score: **0.67**
- *Text:* Difficulty: Intermediate, Advanced. Rising above Bannockburn and rich in goldmining history, the Carrick Range is one of...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0009` | score: **0.66**
- *Text:* Estimated biking time: 2 hr. This loop track is an extension of the Basin View Tramping Track. It has a 300 m climb  wit...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** Search space: **240 → 40** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** Are there any intermediate difficulty mountain bike tracks in New Zealand longer than 2 hours?

**Top-1:** `doc_mtb_tracks_chunk_0015` | score: **0.80**
- *Text:* Difficulty: Intermediate, Advanced. Rising above Bannockburn and rich in goldmining history, the Carrick Range is one of...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0026` | score: **0.66**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0001` | score: **0.64**
- *Text:* Estimated biking time: 30 min - 4 hrs. This advanced mountain bike track can be accessed from the Canaan Downs car park....
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `doc_mtb_tracks_chunk_0026` → **`doc_mtb_tracks_chunk_0015`**. **2 chunk(s)** reordered by keyword boost. **1 new chunk(s)** promoted via BM25.

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** Are there any intermediate difficulty mountain bike tracks in New Zealand longer than 2 hours?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `doc_mtb_tracks_chunk_0022` | score: **5.37**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0015` | score: **5.19**
- *Text:* Difficulty: Intermediate, Advanced. Rising above Bannockburn and rich in goldmining history, the Carrick Range is one of...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0038` | score: **4.85**
- *Text:* Estimated biking time: 2 hr. A public access easement leads to Landslip Creek above Lake Pukaki. Bob’s Cove Track and Na...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `doc_mtb_tracks_chunk_0026` → **`doc_mtb_tracks_chunk_0022`**. **2 new chunk(s)** promoted from outside baseline top-3.

---

## [10/13] Q10 — Compression damping use case — should hit suspension setup guides and MHTML articles

### Baseline — plain semantic search

**Query:** What compression damping settings should I use for climbing versus descending?

**Top-1:** `mtb_suspension_setup_guide_chunk_0006` | score: **0.69**
- *Text:* Every fork and shock differs in damping options—some offer high and low-speed compression settings, others provide two o...
- *Source:* `HW1/data/raw/mtb_suspension_setup_guide.md`

**Top-2:** `how_to_setup_suspension_chunk_0006` | score: **0.58**
- *Text:* Andy Lloyd / Our Media Damping is a typically oil-based system that controls how fast the spring compresses and rebounds...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-3:** `Suspension_SRAM_chunk_0041` | score: **0.57**
- *Text:* Suspension compression may feel more firm on bumpier terrain. Decreased HSC damping: Allows the suspension to compress e...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** **Relevant**. Scores: **0.69** / **0.58** / **0.57**. Cross-source: `mtb_suspension_setup_guide`, `how_to_setup_suspension`, `Suspension_SRAM`.

### Metadata filtering — `source_type=[mhtml, markdown]`

**Query:** What compression damping settings should I use for climbing versus descending?

**Why:** Limit to MHTML articles + Markdown guides — compression damping setup content  
**Pool:** 240 → **53** chunks

**Top-1:** `mtb_suspension_setup_guide_chunk_0006` | score: **0.69**
- *Text:* Every fork and shock differs in damping options—some offer high and low-speed compression settings, others provide two o...
- *Source:* `HW1/data/raw/mtb_suspension_setup_guide.md`

**Top-2:** `how_to_setup_suspension_chunk_0006` | score: **0.58**
- *Text:* Andy Lloyd / Our Media Damping is a typically oil-based system that controls how fast the spring compresses and rebounds...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

**Top-3:** `trek_suspension_guide_chunk_0001` | score: **0.54**
- *Text:* They feel more plush, predictable and responsive because there are fewer stiction-causing seals than with air shocks. Ho...
- *Source:* `HW1/data/raw/trek_suspension_guide.mhtml`

> **Conclusion:** Search space: **240 → 53** chunks. **1 new chunk(s)** surfaced. **1 baseline chunk(s)** replaced. Top-1 score: **0.69 → 0.69** (+0.00). Sources: [`mtb_suspension_setup_guide`, `how_to_setup_suspension`, `Suspension_SRAM`] → [`mtb_suspension_setup_guide`, `how_to_setup_suspension`, `trek_suspension_guide`].

### Hybrid search — `60% semantic + 40% BM25`

**Query:** What compression damping settings should I use for climbing versus descending?

**Top-1:** `mtb_suspension_setup_guide_chunk_0006` | score: **0.81**
- *Text:* Every fork and shock differs in damping options—some offer high and low-speed compression settings, others provide two o...
- *Source:* `HW1/data/raw/mtb_suspension_setup_guide.md`

**Top-2:** `trek_suspension_guide_chunk_0001` | score: **0.61**
- *Text:* They feel more plush, predictable and responsive because there are fewer stiction-causing seals than with air shocks. Ho...
- *Source:* `HW1/data/raw/trek_suspension_guide.mhtml`

**Top-3:** `Suspension_SRAM_chunk_0047` | score: **0.58**
- *Text:* Increase LSC damping to reduce compression stroke speed and increase efficiency on rolling or smoother terrain, and when...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. **Top-1 unchanged.** **2 new chunk(s)** promoted via BM25. Sources: [`mtb_suspension_setup_guide`, `how_to_setup_suspension`, `Suspension_SRAM`] → [`mtb_suspension_setup_guide`, `trek_suspension_guide`, `Suspension_SRAM`].

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** What compression damping settings should I use for climbing versus descending?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `mtb_suspension_setup_guide_chunk_0006` | score: **5.20**
- *Text:* Every fork and shock differs in damping options—some offer high and low-speed compression settings, others provide two o...
- *Source:* `HW1/data/raw/mtb_suspension_setup_guide.md`

**Top-2:** `Suspension_SRAM_chunk_0047` | score: **0.97**
- *Text:* Increase LSC damping to reduce compression stroke speed and increase efficiency on rolling or smoother terrain, and when...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `how_to_setup_suspension_chunk_0009` | score: **0.45**
- *Text:* If your settings are correct but you can’t reach full travel, try removing any volume spacers, one at a time. Remember t...
- *Source:* `HW1/data/raw/how_to_setup_suspension.mhtml`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. **Top-1 unchanged.** **2 new chunk(s)** promoted from outside baseline top-3.

---

## [11/13] Q11 — Trail factual lookup — 'days' vocabulary overlaps with maintenance guides; filter to doc_mtb_tracks should fix it

### Baseline — plain semantic search

**Query:** How many days does it take to ride the Timber Trail in New Zealand?

**Top-1:** `doc_mtb_tracks_chunk_0021` | score: **0.69**
- *Text:* Estimated biking time: 40 min. Specifically designed dual use trail through native bush with great downhills and some de...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0026` | score: **0.69**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0022` | score: **0.68**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** **Relevant**. Scores: **0.69** / **0.69** / **0.68**. All top-3 from one source (`doc_mtb_tracks`).

### Metadata filtering — `document_id=doc_mtb_tracks`

**Query:** How many days does it take to ride the Timber Trail in New Zealand?

**Why:** Limit to doc_mtb_tracks CSV — trail duration data; 'days' in query overlaps with maintenance schedule vocabulary  
**Pool:** 240 → **40** chunks

**Top-1:** `doc_mtb_tracks_chunk_0021` | score: **0.69**
- *Text:* Estimated biking time: 40 min. Specifically designed dual use trail through native bush with great downhills and some de...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0026` | score: **0.69**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0022` | score: **0.68**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** Search space: **240 → 40** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** How many days does it take to ride the Timber Trail in New Zealand?

**Top-1:** `doc_mtb_tracks_chunk_0026` | score: **0.81**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0021` | score: **0.75**
- *Text:* Estimated biking time: 40 min. Specifically designed dual use trail through native bush with great downhills and some de...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0038` | score: **0.65**
- *Text:* Estimated biking time: 2 hr. A public access easement leads to Landslip Creek above Lake Pukaki. Bob’s Cove Track and Na...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `doc_mtb_tracks_chunk_0021` → **`doc_mtb_tracks_chunk_0026`**. **2 chunk(s)** reordered by keyword boost. **1 new chunk(s)** promoted via BM25.

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** How many days does it take to ride the Timber Trail in New Zealand?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `doc_mtb_tracks_chunk_0022` | score: **4.23**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0021` | score: **1.69**
- *Text:* Estimated biking time: 40 min. Specifically designed dual use trail through native bush with great downhills and some de...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0026` | score: **0.95**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `doc_mtb_tracks_chunk_0021` → **`doc_mtb_tracks_chunk_0022`**. **3 chunk(s)** reordered.

---

## [12/13] Q12 — Assembly grease spec — 'grease/lube' overlaps with maintenance guide; filter to PDF manuals should fix it

### Baseline — plain semantic search

**Query:** What grease should I use when installing headset bearings?

**Top-1:** `Suspension_SRAM_chunk_0015` | score: **0.37**
- *Text:* If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0018` | score: **0.37**
- *Text:* Apply grease to the axle threads. MTB - Front - 15 mm (D) Road - Front - 15 mm (D) & 12 mm (D) MTB - Rear - 12 mm (D) Ro...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0016` | score: **0.36**
- *Text:* Star Nut Set Tool Depth = 15 mm (0.6 in) 4-5. Use a star nut setter to install a star nut 15 mm (0.6 inches) into the st...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** **Weak** — retrieval struggles here. Scores: **0.37** / **0.37** / **0.36**. All top-3 from one source (`Suspension_SRAM`).

### Metadata filtering — `source_type=pdf`

**Query:** What grease should I use when installing headset bearings?

**Why:** Limit to PDF manuals — headset bearing grease specs; 'grease/lube' overlaps with chain lube in maintenance guide  
**Pool:** 240 → **60** chunks

**Top-1:** `Suspension_SRAM_chunk_0015` | score: **0.37**
- *Text:* If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0018` | score: **0.37**
- *Text:* Apply grease to the axle threads. MTB - Front - 15 mm (D) Road - Front - 15 mm (D) & 12 mm (D) MTB - Rear - 12 mm (D) Ro...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0016` | score: **0.36**
- *Text:* Star Nut Set Tool Depth = 15 mm (0.6 in) 4-5. Use a star nut setter to install a star nut 15 mm (0.6 inches) into the st...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** Search space: **240 → 60** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** What grease should I use when installing headset bearings?

**Top-1:** `Suspension_SRAM_chunk_0017` | score: **0.52**
- *Text:* The axle is fixed into place by applying the required torque indicated. Never use any tool other than what is indicated ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0015` | score: **0.48**
- *Text:* If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `trek_full_suspension_assembly_guide_chunk_0003` | score: **0.44**
- *Text:* 4. Presta only — rotate the valve head clockwise to close it. 5. Put the dust cap back on the valve. Dust cap IMPORTANT:...
- *Source:* `HW1/data/raw/trek_full_suspension_assembly_guide.pdf`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `Suspension_SRAM_chunk_0015` → **`Suspension_SRAM_chunk_0017`**. **1 chunk(s)** reordered by keyword boost. **2 new chunk(s)** promoted via BM25. Sources: [`Suspension_SRAM`] → [`Suspension_SRAM`, `trek_full_suspension_assembly_guide`].

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** What grease should I use when installing headset bearings?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `Suspension_SRAM_chunk_0016` | score: **-4.50**
- *Text:* Star Nut Set Tool Depth = 15 mm (0.6 in) 4-5. Use a star nut setter to install a star nut 15 mm (0.6 inches) into the st...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-2:** `Suspension_SRAM_chunk_0018` | score: **-5.76**
- *Text:* Apply grease to the axle threads. MTB - Front - 15 mm (D) Road - Front - 15 mm (D) & 12 mm (D) MTB - Rear - 12 mm (D) Ro...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

**Top-3:** `Suspension_SRAM_chunk_0015` | score: **-6.10**
- *Text:* If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with ...
- *Source:* `HW1/data/raw/Suspension_SRAM.pdf`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. Top-1 changed: `Suspension_SRAM_chunk_0015` → **`Suspension_SRAM_chunk_0016`**. **2 chunk(s)** reordered.

---

## [13/13] Q13 — Easy difficulty label lookup — semantic embeds 'easy' broadly; BM25 exact-matches the 'Difficulty: Easy' label in CSV chunks

### Baseline — plain semantic search

**Query:** Which New Zealand trails have difficulty rated as Easy?

**Top-1:** `doc_mtb_tracks_chunk_0026` | score: **0.64**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0022` | score: **0.63**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0024` | score: **0.60**
- *Text:* This trail offers challenging, mixed riding through stunning scenery of mountain peaks, crystal clear waters, high count...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** **Relevant**. Scores: **0.64** / **0.63** / **0.60**. All top-3 from one source (`doc_mtb_tracks`).

### Metadata filtering — `document_id=doc_mtb_tracks`

**Query:** Which New Zealand trails have difficulty rated as Easy?

**Why:** Limit to doc_mtb_tracks CSV — only source with NZ trail difficulty labels  
**Pool:** 240 → **40** chunks

**Top-1:** `doc_mtb_tracks_chunk_0026` | score: **0.64**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0022` | score: **0.63**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0024` | score: **0.60**
- *Text:* This trail offers challenging, mixed riding through stunning scenery of mountain peaks, crystal clear waters, high count...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** Search space: **240 → 40** chunks. Results **unchanged** — filter did not affect top-k ranking.

### Hybrid search — `60% semantic + 40% BM25`

**Query:** Which New Zealand trails have difficulty rated as Easy?

**Top-1:** `doc_mtb_tracks_chunk_0015` | score: **0.61**
- *Text:* Difficulty: Intermediate, Advanced. Rising above Bannockburn and rich in goldmining history, the Carrick Range is one of...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0022` | score: **0.57**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0024` | score: **0.53**
- *Text:* This trail offers challenging, mixed riding through stunning scenery of mountain peaks, crystal clear waters, high count...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** BM25 weight: **40%**, semantic weight: **60%**. Top-1 changed: `doc_mtb_tracks_chunk_0026` → **`doc_mtb_tracks_chunk_0015`**. **1 new chunk(s)** promoted via BM25.

### Reranking — `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Query:** Which New Zealand trails have difficulty rated as Easy?

**Candidates:** top-**12** semantic → rescored by cross-encoder → top-**3**

**Top-1:** `doc_mtb_tracks_chunk_0026` | score: **4.87**
- *Text:* Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-2:** `doc_mtb_tracks_chunk_0022` | score: **2.48**
- *Text:* Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

**Top-3:** `doc_mtb_tracks_chunk_0038` | score: **2.41**
- *Text:* Estimated biking time: 2 hr. A public access easement leads to Landslip Creek above Lake Pukaki. Bob’s Cove Track and Na...
- *Source:* `HW1/data/raw/doc_mtb_tracks.csv`

> **Conclusion:** Candidates rescored: **top-12** semantic → reranked to **top-3**. **Top-1 unchanged.** **1 new chunk(s)** promoted from outside baseline top-3.

---

