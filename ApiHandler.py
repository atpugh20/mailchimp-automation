import requests

class ApiHandler:
    def __init__(self):
        print("Building API Handler...")

        print("API Handler built.")

    def PullFromXCD(self) -> None:
        '''
        * Pulls all users from the X-CD database, then places it into the DataContainer.
        '''
        r = requests.get(self.xcd_url)
        print(r.text)

    def PostToXCD():
        '''
        * Uses DataContainer to update X-CD's database.
        '''
        pass

    def PullFromMailchimp():
        '''
        * Pulls all users from the Mailchip database, then places it into DataContainer.
        '''
        pass

    def PostToMailchimp():
        '''
        * Uses DataContainer to update Mailchimp's database.
        '''
        pass