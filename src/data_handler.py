def initialize_contacts(contacts_meta: list) -> list:
    return []


def get_email_pref(contact) -> bool:
    """
    Using a given contact, extract the email preference as a bool
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


def remove_opt_outs(all_contacts: list):
    pass
