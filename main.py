import json
import time
from pprint import pprint

from src.api_handler import get_contact_uuids, get_user_info
from src.data_handler import (
    get_all_email_pref,
    remove_opt_outs,
    extract_important_fields,
)

from test_data import test_contacts, test_uuids

# from test_data import test_contacts


def main():
    # Date format: DD-MM-YYYY
    last_updated = "31-12-2000"

    # contact_id = "D4ED5672-05E2-0F11-6CC69A30C6D6A75F"

    """uuids = get_contact_uuids(last_updated, testing=True)

    contacts = []
    for uuid in uuids:
        contacts.append(get_user_info(uuid))"""

    statuses = get_all_email_pref(test_contacts)
    opt_in_data = remove_opt_outs(test_contacts, statuses, test_uuids)
    opt_in_contacts = opt_in_data[0]
    opt_in_uuids = opt_in_data[1]
    new_contacts = extract_important_fields(opt_in_contacts, opt_in_uuids)

    for key, value in new_contacts.items():
        print(value["membership_type"])

    # print(opt_in_contacts[0][0]["contact_info"])

    # correct_info_contacts = extract_important_fields(opt_in_contacts, opt_in_uuids)


if __name__ == "__main__":
    main()
