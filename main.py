import json

from src.api_handler import get_contacts, get_user_info
from src.data_handler import get_email_pref


def main():
    #contacts = get_contacts()
    contact_id = "D4ED5672-05E2-0F11-6CC69A30C6D6A75F"

    user_info = get_user_info(contact_id)
    is_opted_in = get_email_pref(user_info)


if __name__ == "__main__":
    main()
