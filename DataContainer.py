import requests

class DataContainer:
    def __init__(self):
        self.contacts = []

    def AddUser(self, firstName: str, lastName: str, email: str, xcdID: str) -> None:
        user = {
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "xcdID": xcdID
        }

        self.contacts.append(user)


    def AddMultipleUsers(self, users: list) -> None:
        pass