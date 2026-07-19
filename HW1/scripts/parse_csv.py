"""Parser for CSV trail data — DOC New Zealand mountain bike tracks."""

import csv
from pathlib import Path
from datetime import date


def parse_csv(filepath: Path) -> list[dict]:
    trails: list[dict] = []

    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            intro = row.get("introduction", "").strip()
            difficulty = row.get("difficulty", "").strip()
            biking_time = row.get("bikingTime", "").strip()
            track_url = row.get("mountainBikingTrackWebPage", "").strip()
            length_raw = row.get("Shape__Length", "").strip()

            parts = [name]
            if difficulty:
                parts.append(f"Difficulty: {difficulty}")
            if biking_time:
                parts.append(f"Estimated biking time: {biking_time}")
            if intro:
                parts.append(intro)

            trails.append({
                "name": name,
                "difficulty": difficulty,
                "biking_time": biking_time,
                "trail_length_m": float(length_raw) if length_raw else None,
                "url": track_url,
                "text": ". ".join(parts),
            })

    full_text = "\n\n".join(t["text"] for t in trails)

    return [{
        "document_id": filepath.stem,
        "source_file": filepath.name,
        "source_type": "csv",
        "title": "New Zealand DOC Mountain Bike Tracks",
        "text": full_text,
        "metadata": {
            "url": "https://doc-deptconservation.opendata.arcgis.com/datasets/0fdd22944b1b42ec87f54c11790208f6_1",
            "publisher": "New Zealand Department of Conservation",
            "total_trails": len(trails),
            "trails": trails,
            "topic_tags": ["trails", "new-zealand", "doc"],
            "language": "en",
            "date_accessed": str(date.today()),
        },
    }]
