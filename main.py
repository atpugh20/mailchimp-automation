import json
import time
import tracemalloc
from datetime import datetime as dt

from src.file_handler import load_dates, save_file
from src.api_handler import (
    get_all_user_info,
    get_contact_uuids,
    get_mc_contacts,
    push_to_mailchimp,
)


def log_time(start_time):
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Program ran for: {execution_time:.6f} seconds")


def log_memory(tracer: tracemalloc):
    BYTES_PER_MB = 1024 * 1024
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current RAM usage: {current / BYTES_PER_MB:.2f} MB")
    print(f"Peak RAM usage:    {peak / BYTES_PER_MB:.2f} MB")


def start_interval(sync_interval):
    print(f"Waiting for {sync_interval} seconds...")
    print("======================================")
    time.sleep(sync_interval)


mc_test_data = {
    "D4ED5672-05E2-0F11-6CC69A30C6D6A75F": {
        "email_address": "alex@uscap.org",
        "status_if_new": "subscribed",
        "merge_fields": {
            "XCDID": "D4ED5672-05E2-0F11-6CC69A30C6D6A75F",
            "FNAME": "Alexander",
            "LNAME": "Pugh",
            "DEGREES": "MSCS, MPA",
            "COUNTRY": "United States",
            "CITY": "Palm Springs",
            "STATE": "California",
            "INST": "USCAP",
            "SUBSPECIAL": "",
            "MTYPE": "Regular Member",
        },
    },
    "C72F8BE6-AC31-8464-748EE3A4F9FF9D16": {
        "email_address": "atpugh20@gmail.com",
        "status_if_new": "subscribed",
        "merge_fields": {
            "XCDID": "C72F8BE6-AC31-8464-748EE3A4F9FF9D16",
            "FNAME": "Alfredo",
            "LNAME": "Abromaitis",
            "DEGREES": "MSCS",
            "COUNTRY": "United States",
            "CITY": "Palm Springs",
            "STATE": "California",
            "INST": "USCAP",
            "SUBSPECIAL": "",
            "MTYPE": "",
        },
    },
}


def main():
    sync_interval = 30  # seconds
    update_all = False

    while True:
        dates = load_dates()
        if update_all:
            date = dates["last_manual"]
        else:
            date = dates["last_update"]

        # Time / Memory Tracking
        start_time = time.perf_counter()
        tracemalloc.start()

        # Get Contacts
        """print(f"Checking updates since: {date}")
        print("Creating [search_id]...")
        uuids = get_contact_uuids(date, testing)
        contacts = get_all_user_info(uuids)"""

        # contacts = mc_test_data
        # push_to_mailchimp(contacts)

        # get_mc_contacts()

        # Time / Memory Logging
        log_time(start_time)
        log_memory(tracemalloc)
        tracemalloc.stop()

        dates["last_update"] = dt.now().strftime("%m-%d-%Y")
        save_file(dates, "./data/dates.json")

        start_interval(sync_interval)


if __name__ == "__main__":
    main()
