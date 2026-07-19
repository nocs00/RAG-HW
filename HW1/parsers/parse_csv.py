"""Parser for CSV trail data — DOC New Zealand mountain bike tracks."""

import csv
from pathlib import Path
from datetime import date


def parse_csv(filepath: Path) -> list[dict]:
    records = []
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            intro = row.get("introduction", "").strip()
            difficulty = row.get("difficulty", "").strip()
            biking_time = row.get("bikingTime", "").strip()
            track_url = row.get("mountainBikingTrackWebPage", "").strip()
            date_loaded = row.get("dateLoadedToGIS", "").strip()
            obj_id = row.get("OBJECTID", "").strip()
            length_raw = row.get("Shape__Length", "").strip()

            # Build a natural-language text for embedding
            parts = [name]
            if difficulty:
                parts.append(f"Difficulty: {difficulty}")
            if biking_time:
                parts.append(f"Estimated biking time: {biking_time}")
            if intro:
                parts.append(intro)
            text = ". ".join(parts)

            records.append({
                "document_id": f"{filepath.stem}_{obj_id}",
                "source_file": filepath.name,
                "source_type": "csv",
                "title": name,
                "text": text,
                "metadata": {
                    "url": track_url,
                    "publisher": "New Zealand Department of Conservation",
                    "difficulty": difficulty,
                    "biking_time": biking_time,
                    "trail_length_m": float(length_raw) if length_raw else None,
                    "date_loaded": date_loaded,
                    "topic_tags": ["trails", "new-zealand", "doc"],
                    "language": "en",
                    "date_accessed": str(date.today()),
                },
            })

    return records
