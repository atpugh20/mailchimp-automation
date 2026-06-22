"""
The date format used is 'MM-DD-YYYY'

The file_path used should be "./data/dates.json"

Example Date Data:
{
    "last_update": "06-22-2026",
    "last_manual": "12-30-2000"
}

Example Email Map Data:
{
    "C72F8BE6-AC31-8464-748EE3A4F9FF9D16": "mojito@uscap.org"
}
"""

import json


def load_file(file_path: str, default_data):
    try:
        with open(file_path, "r") as f:
            return json.load(f)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return default_data
    except json.JSONDecodeError:
        print(f"Invalid JSON in {file_path}")
        return default_data
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {e}")
        return default_data


def save_file(data, file_path: str):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            print(f"File saved at {file_path}.")
    except Exception as e:
        print(f"Error saving {file_path} : {e}")


def load_dates() -> dict:
    default_data = {}
    default_data["last_update"] = "06-22-2026"
    default_data["last_manual"] = "12-30-2000"

    return load_file("./data/dates.json", default_data)


def save_email_map(data: dict, list_id: str):
    map = {}
    for uuid, contact in data.items():
        map[uuid] = contact["email_address"]

    save_file(map, f"./data/email-map-{list_id}.json")
