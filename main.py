import copy
import json
import time
import tracemalloc
from datetime import datetime as dt

from src import config
from src.file_handler import load_dates, save_file, dates_file_path
from src.api_handler import (
    get_all_user_info,
    get_contact_uuids,
    pull_new_email_cache,
    push_to_mailchimp,
    update_mc_emails,
)


def log_time(start_time):
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Program ran for: {execution_time:.6f} seconds")


def log_memory():
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
        "email_address": "mojito@uscap.org",
        "status_if_new": "subscribed",
        "merge_fields": {
            "XCDID": "C72F8BE6-AC31-8464-748EE3A4F9FF9D16",
            "FNAME": "Alfredo",
            "LNAME": "Abromaitis",
            "DEGREES": "",
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

    testing = False

    last_manual = False
    new_email_cache = False

    list_id = config.MC_MAIN_LIST_ID
    # list_id = config.MC_TEST_LIST_ID

    while True:
        # Time / Memory Tracking
        start_time = time.perf_counter()
        tracemalloc.start()

        # Get date for XCD Pull
        dates = load_dates()
        if last_manual:
            date = dates["last_manual"]
        else:
            date = dates["last_update"]

        if new_email_cache:
            pull_new_email_cache(list_id)

        # Get XCD contacts
        print(f"Checking updates since: {date}")
        print("Creating [search_id]...")
        uuids = get_contact_uuids(date, testing)
        contacts = get_all_user_info(uuids)

        # Use this when using test data
        # contacts = copy.deepcopy(mc_test_data)

        # Update emails in MC
        update_mc_emails(contacts, list_id)

        # Update rest of data
        push_to_mailchimp(contacts, list_id)

        # Save current date as last_update
        dates["last_update"] = dt.now().strftime("%m-%d-%Y")
        if last_manual:
            dates["last_manual"] = dates["last_update"]

        save_file(dates, dates_file_path)

        # Time / Memory Logging
        log_time(start_time)
        log_memory()
        tracemalloc.stop()

        # Wait for next loop
        # start_interval(sync_interval)


if __name__ == "__main__":
    main()
