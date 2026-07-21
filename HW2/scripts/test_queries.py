"""
10 test queries for the MTB knowledge base (HW1 chunks).

Each query targets a different source document or topic to verify cross-source retrieval.
Expected source hints are comments only — not used at runtime.
"""

TEST_QUERIES = [
    {
        "id": "q1",
        "query": "How do I set sag on my mountain bike fork?",
        # Expected: mtb_suspension_setup_guide, how_to_setup_suspension, trek_suspension_guide
        "note": "Core suspension setup — should hit mtb_suspension_setup_guide and MHTML articles",
    },
    {
        "id": "q2",
        "query": "What torque should I use when assembling a carbon steerer tube?",
        # Expected: trek_full_suspension_assembly_guide, Suspension_SRAM
        "note": "Assembly / torque specs — should hit Trek PDF and SRAM manual",
    },
    {
        "id": "q3",
        "query": "How often should I lube my chain and what type of lube should I use in wet conditions?",
        # Expected: mtb_maintenance_guide
        "note": "Drivetrain maintenance — should hit mtb_maintenance_guide",
    },
    {
        "id": "q4",
        "query": "Which New Zealand trails are rated beginner and suitable for easy rides?",
        # Expected: doc_mtb_tracks
        "note": "Trail data query — should hit doc_mtb_tracks CSV chunks",
    },
    {
        "id": "q5",
        "query": "What is rebound damping and how do I adjust it on a RockShox shock?",
        # Expected: Suspension_SRAM, mtb_suspension_setup_guide, bicycle_suspension_wiki
        "note": "Rebound tuning — should hit SRAM manual and suspension setup guides",
    },
    {
        "id": "q6",
        "query": "How do I check if my brake pads are worn and when should I replace them?",
        # Expected: mtb_maintenance_guide
        "note": "Brake maintenance — should hit mtb_maintenance_guide post-ride routine section",
    },
    {
        "id": "q7",
        "query": "What is the difference between hardtail and full suspension mountain bikes?",
        # Expected: mountain_bike_wiki, bicycle_suspension_wiki
        "note": "Bike types comparison — should hit Wikipedia articles",
    },
    {
        "id": "q8",
        "query": "How do I service my fork lowers and how often should it be done?",
        # Expected: mtb_maintenance_guide, Suspension_SRAM
        "note": "Fork service interval — should hit maintenance guide (50hr service) and SRAM manual",
    },
    {
        "id": "q9",
        "query": "Are there any intermediate difficulty mountain bike tracks in New Zealand longer than 2 hours?",
        # Expected: doc_mtb_tracks
        "note": "Filtered trail query — should hit doc_mtb_tracks chunks with intermediate difficulty",
    },
    {
        "id": "q10",
        "query": "What compression damping settings should I use for climbing versus descending?",
        # Expected: mtb_suspension_setup_guide, how_to_setup_suspension, trek_suspension_guide
        "note": "Compression damping use case — should hit suspension setup guides and MHTML articles",
    },
]

if __name__ == "__main__":
    for q in TEST_QUERIES:
        print(f"[{q['id']}] {q['query']}")
        print(f"       Note: {q['note']}")
        print()
