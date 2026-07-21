# Retrieval Examples — MTB Knowledge Base

Model: `sentence-transformers/all-MiniLM-L6-v2`
Index: FAISS `IndexFlatIP` (cosine similarity, 384-dim)
Chunks indexed: 240
k = 3 per query

---

## Q1

Query: How do I set sag on my mountain bike fork?

Top-1: `how_to_setup_suspension_chunk_0002` | score: 0.6881
  Text: The video above shows how our former resident suspension guru, Seb Stott, set up his bikes. It should get your suspension...
  Source: how_to_setup_suspension.mhtml (how_to_setup_suspension)

Top-2: `how_to_setup_suspension_chunk_0004` | score: 0.6243
  Text: 50mm), then multiply that by 100 to find the sag percentage. Helpfully, this is already marked on RockShox forks and sho...
  Source: how_to_setup_suspension.mhtml (how_to_setup_suspension)

Top-3: `bicycle_suspension_wiki_chunk_0050` | score: 0.5741
  Text: Sag refers to how much a suspension moves under just the static load of the rider. Sag is often used as one parameter wh...
  Source: bicycle_suspension_wiki.txt (bicycle_suspension_wiki)

Comment: **Relevant.** Top results correctly land on the BikeRadar sag setup guide. The Wikipedia chunk adds a concise definition. The dedicated step-by-step section from `mtb_suspension_setup_guide` didn't rank top-3 — it appears at k=4–5, suggesting slight semantic overlap dilution across similar sources.

---

## Q2

Query: What torque should I use when assembling a carbon steerer tube?

Top-1: `Suspension_SRAM_chunk_0016` | score: 0.5124
  Text: Star Nut Set Tool Depth = 15 mm (0.6 in) 4-5. Use a star nut setter to install a star nut 15 mm (0.6 inches) into the st...
  Source: Suspension_SRAM.pdf (Suspension_SRAM)

Top-2: `Suspension_SRAM_chunk_0015` | score: 0.4247
  Text: If damaged, replace the crown steerer upper tube prior the cables, housing, and brake hoses are not making contact with...
  Source: Suspension_SRAM.pdf (Suspension_SRAM)

Top-3: `Suspension_SRAM_chunk_0000` | score: 0.4208
  Text: Suspension User Manual Tools and Supplies Single Crown Fork Installation Aluminum and Steel Steerer Tube Hub End Cap Ada...
  Source: Suspension_SRAM.pdf (Suspension_SRAM)

Comment: **Partially relevant.** All results come from the SRAM PDF and are about steerer tube installation steps, which is on-topic. However, exact torque values for carbon are in a different chunk of the PDF that mentions specific Nm values — scores are moderate (0.42–0.51) because PDF chunks lack structural headings and torque tables render as flat text. Trek assembly PDF was not retrieved, likely because its torque section is phrased differently.

---

## Q3

Query: How often should I lube my chain and what type of lube should I use in wet conditions?

Top-1: `mtb_maintenance_guide_chunk_0008` | score: 0.4672
  Text: Track your ride hours using a GPS unit or app (Strava, TrailForks) to schedule service based on actual use, not just c...
  Source: mtb_maintenance_guide.md (mtb_maintenance_guide)

Top-2: `mtb_maintenance_guide_chunk_0003` | score: 0.4283
  Text: Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: Wet lube for wet/mu...
  Source: mtb_maintenance_guide.md (mtb_maintenance_guide)

Top-3: `mtb_maintenance_guide_chunk_0002` | score: 0.4075
  Text: 1. Rinse the Bike (3 min) Use a garden hose with moderate pressure — avoid pressure washers, which force water past seal...
  Source: mtb_maintenance_guide.md (mtb_maintenance_guide)

Comment: **Partially relevant.** Top-2 directly answers the query with "wet lube for wet/muddy conditions". Top-1 (lifehacks) is less directly relevant but contains ride-interval guidance. Top-3 (rinse routine) is weakly relevant. The chunk with explicit lube frequency landed at Top-2 rather than Top-1, as the lifehacks chunk has broader maintenance vocabulary that matched the "how often" part of the query.

---

## Q4

Query: Which New Zealand trails are rated beginner and suitable for easy rides?

Top-1: `doc_mtb_tracks_chunk_0026` | score: 0.6600
  Text: Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
  Source: doc_mtb_tracks.csv (doc_mtb_tracks)

Top-2: `doc_mtb_tracks_chunk_0022` | score: 0.6527
  Text: Estimated biking time: Full trail: 2-3 days. Using historic bush tramways, old bulldozer and haul roads, and newly const...
  Source: doc_mtb_tracks.csv (doc_mtb_tracks)

Top-3: `doc_mtb_tracks_chunk_0024` | score: 0.6300
  Text: This trail offers challenging, mixed riding through stunning scenery of mountain peaks, crystal clear waters, high countr...
  Source: doc_mtb_tracks.csv (doc_mtb_tracks)

Comment: **Not relevant.** All top-3 results are from the correct source (NZ DOC CSV) but return intermediate/challenging trails, not beginner/easy ones. This is a known semantic retrieval limitation: the query mentions "beginner" and "easy" but the CSV chunks don't repeat difficulty labels enough per chunk to distinguish difficulty via embedding similarity. Metadata filtering on `difficulty_levels` field would correctly solve this.

---

## Q5

Query: What is rebound damping and how do I adjust it on a RockShox shock?

Top-1: `how_to_setup_suspension_chunk_0007` | score: 0.7229
  Text: Ian Linton / Our Media Rebound damping controls how quickly your suspension resets after absorbing an impact and should...
  Source: how_to_setup_suspension.mhtml (how_to_setup_suspension)

Top-2: `how_to_setup_suspension_chunk_0008` | score: 0.7191
  Text: Session the trail section and decrease the damping – by turning the dial/lever towards the '-' or jackalope (hare) symbo...
  Source: how_to_setup_suspension.mhtml (how_to_setup_suspension)

Top-3: `how_to_setup_suspension_chunk_0006` | score: 0.6746
  Text: Andy Lloyd / Our Media Damping is a typically oil-based system that controls how fast the spring compresses and rebounds...
  Source: how_to_setup_suspension.mhtml (how_to_setup_suspension)

Comment: **Highly relevant.** Best result set of all 10 queries. Top-1 defines rebound damping precisely, Top-2 explains the RockShox jackalope/turtle dial adjustment, Top-3 provides broader damping context. All three from the BikeRadar MHTML article, scores are high (0.67–0.72). The SRAM manual and mtb_suspension_setup_guide also contain relevant content but were outscored.

---

## Q6

Query: How do I check if my brake pads are worn and when should I replace them?

Top-1: `mtb_maintenance_guide_chunk_0003` | score: 0.6129
  Text: Backpedal a dozen times to work it in, then wipe excess with a clean rag. Lube selection lifehack: Wet lube for wet/mu...
  Source: mtb_maintenance_guide.md (mtb_maintenance_guide)

Top-2: `mtb_maintenance_guide_chunk_0004` | score: 0.4915
  Text: Replace when worn to 1–1.5 mm remaining. Check rotor scoring by running a finger lightly along the braking surface wh...
  Source: mtb_maintenance_guide.md (mtb_maintenance_guide)

Top-3: `mtb_maintenance_guide_chunk_0010` | score: 0.4577
  Text: Component | Replace When | Chain | 0.5–0.75% wear (use chain wear tool) | Brake pads | Less than 1–2 mm...
  Source: mtb_maintenance_guide.md (mtb_maintenance_guide)

Comment: **Relevant.** Top-2 and Top-3 directly answer the query with the 1–1.5 mm threshold and the component replacement table. Top-1 is only partially relevant (chain lube section) but ranked first because the chunk also contains maintenance inspection language. Section-level chunking caused the brake pad inspection content to split across chunks, slightly reducing the top-1 score.

---

## Q7

Query: What is the difference between hardtail and full suspension mountain bikes?

Top-1: `mountain_bike_wiki_chunk_0006` | score: 0.7475
  Text: Mountain bikes can usually be divided into four broad categories based on suspension configuration: Rigid: A mountain bi...
  Source: mountain_bike_wiki.txt (mountain_bike_wiki)

Top-2: `mountain_bike_wiki_chunk_0010` | score: 0.7198
  Text: In the past mountain bikes had a rigid frame and fork. In the early 1990s, the first mountain bikes with suspension fork...
  Source: mountain_bike_wiki.txt (mountain_bike_wiki)

Top-3: `bicycle_suspension_wiki_chunk_0044` | score: 0.7100
  Text: For this reason, this style of suspension is most popular on more upright styles of bicycle, where the rider spends the...
  Source: bicycle_suspension_wiki.txt (bicycle_suspension_wiki)

Comment: **Highly relevant.** Top-1 gives an exact categorical breakdown including hardtail and full suspension definitions. Top-2 adds historical context and performance tradeoffs. Top-3 from the bicycle suspension Wikipedia article adds further context. Scores are consistently high (0.71–0.75) — this query benefits from clear encyclopedic language matching the Wikipedia source style.

---

## Q8

Query: How do I service my fork lowers and how often should it be done?

Top-1: `Suspension_SRAM_chunk_0051` | score: 0.5683
  Text: Every ride Clean the dirt and debris from the upper tubes and wiper seals, check air pressure, and inspect upper tubes f...
  Source: Suspension_SRAM.pdf (Suspension_SRAM)

Top-2: `Suspension_SRAM_chunk_0050` | score: 0.5157
  Text: Never use a high-powered washer to clean the suspension fork. To maintain the high performance, safety, and long life of...
  Source: Suspension_SRAM.pdf (Suspension_SRAM)

Top-3: `bicycle_suspension_wiki_chunk_0008` | score: 0.4984
  Text: Increasing the volume of the air inside the spring reduces this effect but the volume of the spring is ultimately limite...
  Source: bicycle_suspension_wiki.txt (bicycle_suspension_wiki)

Comment: **Partially relevant.** Top-1 and Top-2 are from the SRAM manual's maintenance section and cover per-ride fork cleaning, which is on-topic. However, the specific lower leg service procedure (oil change, seal replacement at 50 hours) is captured in `mtb_maintenance_guide` — that chunk didn't appear in top-3, possibly because "service" in the SRAM manual uses different vocabulary ("maintenance"). Top-3 (Wikipedia air spring physics) is not relevant.

---

## Q9

Query: Are there any intermediate difficulty mountain bike tracks in New Zealand longer than 2 hours?

Top-1: `doc_mtb_tracks_chunk_0026` | score: 0.7396
  Text: Estimated biking time: 2 hr 30 min - 3 hr 30 min. The Pakihi Track is a stunning but challenging 20 km journey through l...
  Source: doc_mtb_tracks.csv (doc_mtb_tracks)

Top-2: `doc_mtb_tracks_chunk_0015` | score: 0.6705
  Text: Difficulty: Intermediate, Advanced. Rising above Bannockburn and rich in goldmining history, the Carrick Range is one of...
  Source: doc_mtb_tracks.csv (doc_mtb_tracks)

Top-3: `doc_mtb_tracks_chunk_0009` | score: 0.6639
  Text: Estimated biking time: 2 hr. This loop track is an extension of the Basin View Tramping Track. It has a 300 m climb wit...
  Source: doc_mtb_tracks.csv (doc_mtb_tracks)

Comment: **Relevant.** All results are from the correct source. Top-2 explicitly shows "Intermediate, Advanced" difficulty, and Top-3 shows a 2-hour track. Top-1 is the Pakihi Track (2h30–3h30) which fits the duration criterion. Semantic search handles the time-range query better than the difficulty filter, since "2 hours" appears verbatim in chunk text. Full accuracy would require hybrid metadata + semantic search.

---

## Q10

Query: What compression damping settings should I use for climbing versus descending?

Top-1: `mtb_suspension_setup_guide_chunk_0006` | score: 0.6903
  Text: Every fork and shock differs in damping options—some offer high and low-speed compression settings, others provide two o...
  Source: mtb_suspension_setup_guide.md (mtb_suspension_setup_guide)

Top-2: `how_to_setup_suspension_chunk_0006` | score: 0.5790
  Text: Andy Lloyd / Our Media Damping is a typically oil-based system that controls how fast the spring compresses and rebounds...
  Source: how_to_setup_suspension.mhtml (how_to_setup_suspension)

Top-3: `Suspension_SRAM_chunk_0041` | score: 0.5748
  Text: Suspension compression may feel more firm on bumpier terrain. Decreased HSC damping: Allows the suspension to compress e...
  Source: Suspension_SRAM.pdf (Suspension_SRAM)

Comment: **Relevant.** Top-1 directly addresses the lockout/open compression decision for climbing vs descending. Top-3 from the SRAM manual explains HSC damping behaviour on different terrain types. Top-2 is general damping context. Good cross-source retrieval — three different source types (markdown, mhtml, pdf) all contributed relevant content.

---

## Summary Analysis

| Query | Relevance | Notes |
|-------|-----------|-------|
| Q1 — Sag setup | Relevant | Correct sources; step-by-step guide at k=4 |
| Q2 — Carbon steerer torque | Partially relevant | SRAM PDF on-topic but exact Nm values in different chunk |
| Q3 — Chain lube in wet | Partially relevant | Direct answer at Top-2; Top-1 displaced by vocabulary overlap |
| Q4 — Beginner NZ trails | Not relevant | Correct source but wrong difficulty; needs metadata filter |
| Q5 — Rebound damping RockShox | Highly relevant | Best query; all top-3 directly answer with RockShox details |
| Q6 — Brake pad replacement | Relevant | Answer split across chunks; direct content at Top-2/3 |
| Q7 — Hardtail vs full suspension | Highly relevant | Wikipedia encyclopedic style aligns perfectly |
| Q8 — Fork lower service | Partially relevant | Cleaning procedure retrieved; 50h service interval missed |
| Q9 — Intermediate NZ trails >2h | Relevant | Duration matched well; difficulty filter would improve precision |
| Q10 — Compression for climb/descent | Relevant | Good cross-source retrieval across 3 source types |

**Where retrieval works well:** Conceptual questions about suspension (sag, rebound, hardtail/full-sus) get high-confidence results (0.67–0.75) because the knowledge base has multiple overlapping sources on these topics. Wikipedia-style queries benefit from clean encyclopedic phrasing.

**Where retrieval struggles:** Structured/filtered queries ("beginner trails", "longer than 2 hours") rely on attribute matching that pure semantic search cannot do reliably — hybrid retrieval with metadata pre-filtering on `difficulty_levels` or `trail_names` fields would fix this. PDF chunks also score lower on specific technical queries because flat text extraction loses table and section structure.
