import json
import time
import tracemalloc

from src.api_handler import get_all_user_info, get_contact_uuids, get_user_info
from src.data_handler import (
    get_all_email_pref,
    remove_fake_emails,
    remove_opt_outs,
    extract_important_fields,
)


from test_data import test_contacts, test_uuids

# from test_data import test_contacts


def log_memory(tracer: tracemalloc):
    BYTES_PER_MB = 1024 * 1024
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current RAM usage: {current / BYTES_PER_MB:.2f} MB")
    print(f"Peak RAM usage:    {peak / BYTES_PER_MB:.2f} MB")


def main():
    # Time / Memory Tracking
    start_time = time.perf_counter()
    tracemalloc.start()

    # Date format: MM-DD-YYYY
    last_updated = "06-18-2026"

    log_memory(tracemalloc)

    print("Creating [search_id]...")
    uuids = get_contact_uuids(last_updated)
    log_memory(tracemalloc)

    get_all_user_info(uuids)

    # Time Logging
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Program ran for: {execution_time:.6f} seconds")
    # Memory Logging
    log_memory(tracemalloc)
    tracemalloc.stop()


if __name__ == "__main__":
    main()
