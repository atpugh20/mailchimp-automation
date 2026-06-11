import json

from src.api_handler import get_contact_uuids, get_user_info
from src.data_handler import get_email_pref


def main():
    # Date format: DD-MM-YYYY
    last_updated = "31-12-2000"

    # contact_id = "D4ED5672-05E2-0F11-6CC69A30C6D6A75F"

    uuids = get_contact_uuids(last_updated, testing=True)

    print(uuids)
    print(len(uuids))


if __name__ == "__main__":
    main()
