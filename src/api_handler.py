import requests

from src import config
from src.exceptions import APIConnectionError, APIResponseError

PREFIX = "https://api.xcdsystem.com/v2"

SEE_CONTACTS = f"{PREFIX}/SeeContacts?apikey={config.XCD_KEY}"
GET_USER_INFO = f"{PREFIX}/GetUserInfo?apikey={config.XCD_KEY}"


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
        response = requests.get(url)
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
        raise APIResponseError(f"Unexpected response type {type(response_json)} at {url}")

    # If already a dictionary, just return it
    if isinstance(response_json, dict):
        return response_json

    # Check response_json for errors
    if len(response_json) > 0:
        first = response_json[0]
        if "error" in first:
            raise APIResponseError(f"Invalid API call: {url}: {first}")
 
    return response_json


def get_contacts(last_updated: str) -> list:
    """
    Fetch all contacts updated since the given date 
    and return the parsed response.
    """
    url = f"{SEE_CONTACTS}&last_updated={last_updated}"
    response = pull_api(url)
    return response


def get_user_info(contact_id: str):
    '''
    Fetch contact info for the given contact ID and return the parsed response.
    '''
    url = f"{GET_USER_INFO}&contactid={contact_id}"
    response = pull_api(url)
    return response
