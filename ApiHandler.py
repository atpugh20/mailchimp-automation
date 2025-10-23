import requests
import os

from dotenv import load_dotenv

class ApiHandler:
    def __init__(self):
        print("Building API Handler...")
        load_dotenv()

        self.XCD_KEY = os.getenv("XCD_KEY")
        # self.XCD_URL = f"https://api.xcdsystem.com/v2/SeeContacts?apikey={self.XCD_KEY}&searchid&pageid&last_updated"
        self.XCD_URL = f"https://api.xcdsystem.com/v2/SeeContacts?apikey={self.XCD_KEY}&last_updated"

        print("API Handler built.")

    def MakeRequest(self):
        '''
        * Uses the requests package to make an API call to XCD's databases.
        '''
        print("Starting request to XCD...")

        with requests.Session() as s:
            response = s.get(self.XCD_URL)

        if response.status_code == 200:
            print(f"Successfully retrieved data.")
            data = response.json()
            print(data)

        else:
            print(f"Could not connect to database. Code: {response.status_code}")

        


    def TestRequest(self):
        '''
        * Runs a test request to PokeAPI to test the functionality
        * of the requests package.
        '''

        url = "https://pokeapi.co/api/v2/pokemon/"

        print(f"Requesting from {url}")
        response = requests.get(url)

        if response.status_code == 200:
            print(f"Data recieved from {url}\n") 
            data = response.json()
            print(data)
        else:
            print(f"Error: {response.status_code}")
