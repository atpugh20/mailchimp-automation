import requests
import math
import time
import json

import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
import hashlib

from src import config
from src.data_handler import (
    extract_important_fields,
    get_email_pref,
    get_field,
    fix_invalid_address,
)
from src.file_handler import load_file, save_email_map, save_file
from src.exceptions import APIConnectionError, APIResponseError

PREFIX = "https://api.xcdsystem.com/v2"

SEE_CONTACTS = f"{PREFIX}/SeeContacts?apikey={config.XCD_KEY}"
GET_USER_INFO = f"{PREFIX}/GetUserInfo?apikey={config.XCD_KEY}"

session = requests.Session()
client = MailchimpMarketing.Client()
client.set_config({"api_key": config.MC_KEY, "server": config.MC_SERVER})


def pull_api(url: str) -> list | dict:
    """
    Make a GET request to the given URL and return the parsed JSON response.

    Raises:
        APIConnectionError: Request failure
        APIResponseError:   Invalid or unexpected JSON responses.
    """
    max_fails = 10
    wait_time = 5

    for i in range(max_fails):
        if i > 0:
            print(f"Waiting {wait_time} seconds...")
            time.sleep(wait_time)
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
                break
        print()  # skip a line to counter the \r

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
    contacts = {}
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

        contacts[uuid] = {
            "email_address": email,
            "status_if_new": "subscribed",
            "merge_fields": extract_important_fields(contact, uuid),
        }

    print()  # skip a line to counter the \r
    return contacts


def update_mc_email(new_email: str, old_email: str, list_id: str) -> bool:
    """
    Update the email address for an individual contact in mailchimp. If it
    succeeds, it returns True. If it fails, it returns false.
    """
    try:
        subscriber_hash = hashlib.md5(old_email.lower().encode()).hexdigest()
        client.lists.set_list_member(
            list_id,
            subscriber_hash,
            {"email_address": new_email, "status_if_new": "subscribed"},
        )
        return True

    except ApiClientError as e:
        e_map = json.loads(e.text)
        title = e_map.get("title")

        if title == "Member Exists":
            print(f"{new_email} already in MC")
            return True
        elif title == "Invalid Resource":
            print(f"{new_email} has been deleted from mailchimp before.")
        else:
            print(f"Error :: {e.text}")
            print(f"Error changing email. Old: {old_email} New: {new_email}")

        return False


def update_mc_emails(contacts: dict, list_id: str):
    """
    Updates all the changed emails for
    """
    email_cache = load_file(f"./cache/email-map-{list_id}.json")

    for uuid, contact in contacts.items():
        new_email = contact["email_address"]
        old_email = email_cache.get(uuid, new_email)

        if old_email == new_email:
            continue

        if update_mc_email(new_email, old_email, list_id):
            email_cache[uuid] = new_email
        else:
            contact["email_address"] = old_email

    save_email_map(contacts, list_id)


def push_chunk(chunk: list, list_id: str) -> list:
    try:
        response = client.lists.batch_list_members(
            list_id, {"members": chunk, "update_existing": True}
        )

        print(
            f"{len(response['updated_members'])} updated, "
            f"{len(response['new_members'])} new, "
            f"{response['error_count']} errors"
        )

        return response.get("errors", [])

    except ApiClientError as e:
        print(f"Mailchimp error on batch: {e.text}")
    except Exception as e:
        print(f"Unknown error in `push_chunk`: {e}")

    return []


def push_to_mailchimp(contacts: dict, list_id: str) -> None:
    response = client.ping.get()

    members = []

    for uuid, contact in contacts.items():
        if not contact.get("email_address"):
            continue

        members.append(contact)

    chunk_size = 500

    for i in range(0, len(members), chunk_size):
        chunk = members[i : i + chunk_size]

        errors = push_chunk(chunk, list_id)

        if len(errors) > 0:
            print("Fixing address fields")
            new_chunk = fix_invalid_address(chunk, errors)
            new_errors = push_chunk(new_chunk, list_id)

    # print(last_response)


def pull_new_email_cache(list_id: str) -> None:
    offset = 0
    page_size = 1000
    email_map = {}

    try:
        print("Pulling new email cache from mailchimp.")
        while True:
            response = client.lists.get_list_members_info(
                list_id,
                fields=["members.email_address", "members.merge_fields"],
                count=page_size,
                offset=offset,
            )

            batch = response["members"]

            if not batch:
                break

            for member in batch:
                email = member["email_address"]
                uuid = member["merge_fields"]["XCDID"]
                email_map[uuid] = email

            offset += page_size
            print(f"\r{len(email_map)} emails pulled.", end="", flush=True)
        print()
        path = f"./cache/email-map-{list_id}.json"
        save_file(email_map, path)

    except ApiClientError as e:
        print(f"Status: {e.status_code}")
        print(e.text)
