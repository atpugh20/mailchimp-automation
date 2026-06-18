import requests
import math
import time

import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
import hashlib

from src.data_handler import get_email_pref, get_field
from src import config
from src.exceptions import APIConnectionError, APIResponseError

PREFIX = "https://api.xcdsystem.com/v2"

SEE_CONTACTS = f"{PREFIX}/SeeContacts?apikey={config.XCD_KEY}"
GET_USER_INFO = f"{PREFIX}/GetUserInfo?apikey={config.XCD_KEY}"

session = requests.Session()


def pull_api(url: str) -> list | dict:
    """
    Make a GET request to the given URL and return the parsed JSON response.

    Raises:
        APIConnectionError: Request failure
        APIResponseError:   Invalid or unexpected JSON responses.
    """
    max_fails = 10
    wait_time = 15

    for i in range(max_fails):
        if i > 0:
            print(f"Waiting {wait_time} seconds...")
            time.sleep(15)
            print("Trying again")

        # Ensure there is a response
        try:
            response = session.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to {url}: {e}")
            continue

        # Ensure the response can be converted to JSON
        try:
            response_json = response.json()
        except ValueError as e:
            print(f"Response was not valid JSON at {url}: {e}")
            continue

        # If already a dictionary, just return it
        if isinstance(response_json, dict):
            return response_json

        # Check response_json for errors
        if isinstance(response_json, list) and len(response_json) > 0:
            if any("error" in item for item in response_json):
                print(f"Invalid API call: {url}: {response_json}")
                continue
        return response_json

    return []


def get_contact_uuids(last_updated: str, testing=False) -> list:
    """
    Fetch all contacts updated since the given date
    and return the parsed response.
    """
    url = f"{SEE_CONTACTS}&last_updated={last_updated}"
    response = pull_api(url)

    # Handle empty response
    if not response:
        print(f"Zero contacts returned in response: {response}")
        return []

    response = response[0]
    contacts = []

    # Search info
    search_id = response.get("searchID")
    next_page = response.get("next_page", "")

    # First page data
    contacts.extend(response.get("contact_array", []))
    contacts_per_page = len(contacts)
    contact_count = (
        contacts_per_page if testing else int(response.get("contacts_found", 0))
    )
    if contacts_per_page:
        page_count = math.ceil(contact_count / contacts_per_page) - 1
    else:
        page_count = 0

    # Follow up pages
    if not testing:
        for i in range(page_count):
            if search_id and next_page:
                print(f"\rPage {i + 1}/{page_count}", end="", flush=True)

                new_url = f"{SEE_CONTACTS}&searchid={search_id}&pageid={next_page}"

                response = pull_api(new_url)
                if not response:
                    print(f"Zero contacts returned in page: {search_id} - {next_page}")
                    break
                response = response[0]

                contacts.extend(response.get("contact_array", []))
                next_page = response.get("next_page", "")
            else:
                print()
                break
        print()
    # Check that the correct number of contacts were extracted
    if contact_count != len(contacts):
        print(f"Incorrect amount of contacts: {len(contacts)}/{contact_count}")
        return []

    return [c["UUID"] for c in contacts if "UUID" in c]


def get_user_info(contact_id: str):
    """
    Fetch contact info for the given contact ID and return the parsed response.
    """
    url = f"{GET_USER_INFO}&contactid={contact_id}"
    response = pull_api(url)
    return response


def get_all_user_info(uuids: list):
    contacts = []
    counter = 0
    total = len(uuids)

    for uuid in uuids:
        counter += 1
        print(f"\rContacts: {counter}/{total}", end="", flush=True)
        contact = get_user_info(uuid)

        # Skip Opt-outs
        if not get_email_pref(contact):
            continue

        # Skip emails with "Fake"
        email = get_field(contact[0]["contact_info"], "Email")
        if "fake" in email:
            continue


def push_to_mailchimp(contacts: dict) -> None:
    client = MailchimpMarketing.Client()
    client.set_config({"api_key": config.MC_KEY, "server": config.MC_SERVER})

    import_list = []
