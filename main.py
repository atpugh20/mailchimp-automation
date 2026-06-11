import json

from src.api_handler import get_contacts, get_user_info
from src.data_handler import get_email_pref


def main():
    # Date format: DD-MM-YYYY
    last_updated = "31-12-2000"

    contacts = []

    contact_id = "D4ED5672-05E2-0F11-6CC69A30C6D6A75F"

    contacts.append(get_user_info(contact_id))

    for c in contacts:
        if get_email_pref(c):
            print("Opted in")
        else:
            print("Opted out")

    get_contacts(last_updated)


if __name__ == "__main__":
    main()
