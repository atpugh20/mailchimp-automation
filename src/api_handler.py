import requests
import math

from src import config
from src.exceptions import APIConnectionError, APIResponseError

PREFIX = "https://api.xcdsystem.com/v2"

SEE_CONTACTS = f"{PREFIX}/SeeContacts?apikey={config.XCD_KEY}"
GET_USER_INFO = f"{PREFIX}/GetUserInfo?apikey={config.XCD_KEY}"

session = requests.Session()


def pull_api(url: str):
    """
    Make a GET request to the given URL and return the parsed JSON response.

    Raises:
        APIConnectionError: Request failure
        APIResponseError:   Invalid or unexpected JSON responses.
    """
    print(f"Pulling API at {url}")

    # Ensure there is a response
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise APIConnectionError(f"Failed to connect to {url}: {e}") from e

    # Ensure the response can be converted to JSON
    try:
        response_json = response.json()
    except ValueError as e:
        raise APIResponseError(f"Response was not valid JSON at {url}: {e}") from e

    # Check for incorrect types
    if not isinstance(response_json, (list, dict)):
        raise APIResponseError(
            f"Unexpected response type {type(response_json)} at {url}"
        )

    # If already a dictionary, just return it
    if isinstance(response_json, dict):
        return response_json

    # Check response_json for errors
    if len(response_json) > 0:
        first = response_json[0]
        if "error" in first:
            raise APIResponseError(f"Invalid API call: {url}: {first}")

    return response_json


def get_contact_uuids(last_updated: str, testing=False) -> list:
    """
    Fetch all contacts updated since the given date
    and return the parsed response.
    """
    url = f"{SEE_CONTACTS}&last_updated={last_updated}"
    response = pull_api(url)[0]
    contacts = []

    # Search info
    search_id = response["searchID"]
    next_page = response["next_page"]

    # First page data
    contacts.extend(response["contact_array"])
    contacts_per_page = len(contacts)
    contact_count = response["contacts_found"] if not testing else contacts_per_page

    if contacts_per_page == 0:
        raise APIResponseError(f"Zero contacts returned in response: {response}")

    page_count = math.ceil(contact_count / contacts_per_page) - 1

    # Follow up pages
    if not testing:
        for i in range(page_count):
            print(f"Page {i + 1}/{page_count}")

            new_url = f"{SEE_CONTACTS}&searchid={search_id}&pageid={next_page}"
            response = pull_api(new_url)[0]

            contacts.extend(response["contact_array"])
            next_page = response["next_page"]

    # Check that the correct number of contacts were extracted
    if contact_count != len(contacts):
        print(f"Incorrect amount of contacts: {len(contacts)}/{contact_count}")

    return [c["UUID"] for c in contacts]


def get_user_info(contact_id: str):
    """
    Fetch contact info for the given contact ID and return the parsed response.
    """
    url = f"{GET_USER_INFO}&contactid={contact_id}"
    response = pull_api(url)
    return response
