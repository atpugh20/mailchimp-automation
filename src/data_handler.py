def get_email_pref(contact) -> bool:
    """
    Extract the email marketing opt-in status for a single contact.

    Looks for email marketing entry with ID 5 and determines opt-in status
    based on the presence of an opt-in or opt-out date.

    Args:
        contact: A contact object (list) whose first element contains
                 an 'email_marketing' list of preference dicts.

    Returns:
        True if the contact has opted in, False otherwise.
    """
    is_opted_in = False

    email_pref = next(
        (e for e in contact[0]["email_marketing"] if e["emailmarketingid"] == 5), None
    )

    if email_pref:
        if email_pref["optindate"]:
            is_opted_in = True
        elif email_pref["optoutdate"]:
            print("Opted Out")
        else:
            print("Not able to determine Email preference")
    else:
        print("Incorrect path to `email_pref`")

    return is_opted_in


def get_all_email_pref(all_contacts: list) -> list:
    """
    Extract email marketing opt-in statuses for a list of contacts.

    Args:
        all_contacts: A list of contact objects to process.

    Returns:
        A list of booleans corresponding to each contact's opt-in status,
        in the same order as the input list.
    """
    preferences = []

    for contact in all_contacts:
        preferences.append(get_email_pref(contact))

    return preferences


def remove_opt_outs(all_contacts: list, statuses: list, uuids: list) -> list:
    """
    Filter out contacts who have not opted in to email marketing.

    Args:
        all_contacts: A list of contact objects.
        statuses: A list of booleans representing each contact's opt-in
                  status, parallel to all_contacts.
        uuids: A list of UUIDs corresponding to each contact,
               parallel to all_contacts.

    Returns:
        A two-element list: [opt_in_contacts, opt_in_uuids], where both
        lists contain only the contacts and UUIDs where the corresponding
        status is True. Returns None if all_contacts and statuses differ
        in length.
    """
    opt_ins = []
    updated_uuids = []

    if len(all_contacts) != len(statuses):
        print(
            "Number of contacts does not match the number of email preference statuses"
        )
        raise ValueError

    for i in range(len(all_contacts)):
        if statuses[i]:
            opt_ins.append(all_contacts[i])
            updated_uuids.append(uuids[i])

    return [opt_ins, updated_uuids]


def extract_important_fields(contacts: list, uuids: list) -> dict:
    """
    Reshape a list of contacts into a dict of flattened, relabeled contact records.

    Maps XCD internal field labels to friendlier keys, extracts membership type,
    and keys each record by its UUID.

    Args:
        contacts: A list of raw contact objects from the XCD API.
        uuids: A list of UUID strings corresponding to each contact,
               parallel to contacts.

    Returns:
        A dict keyed by UUID, where each value is a flattened contact dict
        with keys: uuid, email, first_name, last_name, degrees, country,
        city, state, institution, primary_subspecialty, and membership_type.
        Returns an empty dict if contacts and uuids differ in length.
    """
    new_contacts = {}

    label_map = {
        "Email": "email",
        "Firstname": "first_name",
        "Lastname": "last_name",
        "ContactDegrees": "degrees",
        "Country": "country",
        "City": "city",
        "State": "state",
        "Company": "institution",
        "CustomField_54": "primary_subspecialty",
    }

    if len(contacts) != len(uuids):
        print("Number of contacts does not match the number of UUIDs")
        return new_contacts

    for i in range(len(contacts)):
        contact = contacts[i][0]

        new_contact = {"uuid": uuids[i]}

        for key, value in label_map.items():
            new_contact[value] = get_field(contact["contact_info"], key)

        new_contact["membership_type"] = get_membership(contact["contact_groups"])

        new_contacts[uuids[i]] = new_contact

    return new_contacts


def get_field(contact_info: list, internal_label: str):
    """
    Extract the user_data value for a specific field from a contact's info list.

    Args:
        contact_info: A list of field dicts, each containing at minimum
                      'internal_label' and 'user_data' keys.
        internal_label: The internal label string to search for.

    Returns:
        The user_data value for the matching field, or an empty string
        if no matching field is found.
    """
    return next(
        (
            field["user_data"]
            for field in contact_info
            if field["internal_label"] == internal_label
        ),
        "",
    )


def get_membership(groups: list) -> str:
    """
    Determine a contact's active membership type from their group list.

    Checks a predefined set of known membership types and returns the one
    that is currently active. Logs a warning if more than one active
    membership type is found.

    Args:
        groups: A list of group dicts, each containing at minimum
                'groupname' and 'status' keys.

    Returns:
        The name of the contact's active membership type, or an empty
        string if none is found. If multiple active memberships are found,
        returns the first one.
    """
    # Current membership types
    group_types = [
        "Adjunct Member",
        "Honorary Member",
        "Medical Student Member",
        "Regular Member",
        "Regular/1st Yr Transition",
        "Regular/2nd yr Transition",
        "Retired Member",
        "Trainee Member",
    ]

    active_groups = []

    # Grab the user's membership status for every membership group
    for group_type in group_types:
        status = next(
            (field["status"] for field in groups if field["groupname"] == group_type),
            "",
        )

        if status == "active":
            active_groups.append(group_type)

    # Handle if in 0 groups or if in more than one
    if len(active_groups) == 0:
        return ""
    elif len(active_groups) > 1:
        print("More than one group found")

    return active_groups[0]
