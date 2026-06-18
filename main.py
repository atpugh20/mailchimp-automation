import json
import time
import tracemalloc

from src.api_handler import get_contact_uuids, get_user_info
from src.data_handler import (
    get_all_email_pref,
    remove_fake_emails,
    remove_opt_outs,
    extract_important_fields,
)


from test_data import test_contacts, test_uuids

# from test_data import test_contacts

BYTES_PER_MB = 1024 * 1024


def main():
    tracemalloc.start()
    # Date format: DD-MM-YYYY
    last_updated = "12-31-2000"

    # contact_id = "D4ED5672-05E2-0F11-6CC69A30C6D6A75F"
    print("Creating search id")
    uuids = get_contact_uuids(last_updated)

    # Get extra details for each UUID
    contacts = []
    counter = 0
    for uuid in uuids:
        counter += 1
        print(f"\rContacts: {counter}/{len(uuids)}", end="", flush=True)
        contacts.append(get_user_info(uuid))

    with open("./test_data/test_data_large.json", "w") as f:
        contacts_string = json.dump(contacts)
        f.write(contacts_string)

    statuses = get_all_email_pref(contacts)
    contacts, uuids = remove_opt_outs(contacts, statuses, uuids)
    contacts = extract_important_fields(contacts, uuids)
    contacts = remove_fake_emails(contacts)

    with open("./test_data/test_data_modified.json", "w") as f:
        contacts_string = json.dump(contacts)
        f.write(contacts_string)

    current, peak = tracemalloc.get_traced_memory()

    print(f"Current RAM usage: {current / BYTES_PER_MB:.2f} MB")
    print(f"Peak RAM usage:    {peak / BYTES_PER_MB:.2f} MB")

    # Stop tracking
    tracemalloc.stop()


if __name__ == "__main__":
    main()
