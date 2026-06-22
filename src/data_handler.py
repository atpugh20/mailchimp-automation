def get_email_pref(contact) -> bool:
    """
    Extract the email marketing opt-in status for a single contact.

    Looks for email marketing entry with ID 5 and determines opt-in status
    based on the presence of an opt-in or opt-out date.
    """
    is_opted_in = False

    email_pref = next(
        (e for e in contact[0]["email_marketing"] if e["emailmarketingid"] == 5), None
    )

    if email_pref:
        # If there is an "optindate" filled, then they are subscribed
        if email_pref["optindate"]:
            is_opted_in = True
    else:
        # Do not unsubscribe unless it is specifically stated in a future pull
        is_opted_in = True

    return is_opted_in


def get_all_email_pref(all_contacts: list) -> list:
    """
    Extract email marketing opt-in statuses for a list of contacts.
    """
    preferences = []

    for contact in all_contacts:
        preferences.append(get_email_pref(contact))

    return preferences


def extract_important_fields(contact, uuid) -> dict:

    label_map = {
        "Firstname": "FNAME",
        "Lastname": "LNAME",
        "ContactDegrees": "DEGREES",
        "Country": "COUNTRY",
        "City": "CITY",
        "State": "STATE",
        "Company": "INST",
        "CustomField_54": "SUBSPECIAL",
    }

    contact = contact[0]

    new_contact = {"XCDID": uuid}

    for key, value in label_map.items():
        new_contact[value] = get_field(contact["contact_info"], key)

    new_contact["MTYPE"] = get_membership(contact["contact_groups"])

    return new_contact


def get_field(contact_info: list, internal_label: str):
    """
    Extract the user_data value for a specific field from a contact's info list.
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
