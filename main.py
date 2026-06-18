import json
import time
import tracemalloc

from src.api_handler import get_all_user_info, get_contact_uuids


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


def main():
    sync_interval = 30  # seconds
    update_all = False

    while True:
        last_updated = "12-30-2000" if update_all else "06-18-2026"  # MM-DD-YYYY

        print(last_updated)

        # Time / Memory Tracking
        start_time = time.perf_counter()
        tracemalloc.start()

        # Get Contacts
        print("Creating [search_id]...")
        uuids = get_contact_uuids(last_updated)
        contacts = get_all_user_info(uuids)

        # Time / Memory Logging
        log_time(start_time)
        log_memory(tracemalloc)
        tracemalloc.stop()

        start_interval(sync_interval)


if __name__ == "__main__":
    main()
