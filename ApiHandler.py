import requests
import os
import json
from datetime import datetime

from dotenv import load_dotenv

class ApiHandler:
    def __init__(self):
        load_dotenv()
        self.LastUpdated = "31-12-2024"
        self.XCD_KEY = os.getenv("XCD_KEY")
        self.XCD_URL = f"https://api.xcdsystem.com/v2/SeeContacts?apikey={self.XCD_KEY}&last_updated={self.LastUpdated}" 
        print("API Handler built.")


    def MakeRequest(self, apiURL: str) -> list:
        '''
        * Uses the requests package to make an API call to XCD's databases,
        * then returns the reponse as a json-parsed list.
        '''
        print("\nStarting request to XCD...")
        parsedData = []

        with requests.Session() as s:
            response = s.get(apiURL)

        # If sucessfully connected, parse the data and pass it into parsedData to be returned
        if response.status_code == 200:
            responseText = response.text
            parsedData = json.loads(responseText)
            print(f"Successfully retrieved data.")
        else:
            print(f"Could not connect to database. Code: {response.status_code}")
        
        return parsedData


    def ExtractContacts(self, showStats = False) -> list:
        '''
        * Uses self.MakeRequest to pull the entire API contact search, and
        * returns all contacts from XCD. This needs to be done since each 
        * request only returns 100 contacts. This method will make requests 
        * until the "next_page" field returns an empty string.
        '''
        startDatetime = datetime.now()
        currentDatetime = datetime.now()

        parsedData = self.MakeRequest(self.XCD_URL) 

        searchID = parsedData[0]["searchID"]  # API id for current search session
        nextPage = parsedData[0]["next_page"]  # The string that gets the next page of the search (100 contacts each page)
        contacts = parsedData[0]["contact_array"]  # The list of contacts from the current page
        
        counter = 0

        # Continue to make API calls until the next_page string is empty (no more contacts)
        while nextPage != "":
            # Update the call for the new request
            newURL = f"https://api.xcdsystem.com/v2/SeeContacts?apikey={self.XCD_KEY}&searchid={searchID}&pageid={nextPage}&last_updated={self.LastUpdated}"
            parsedData = self.MakeRequest(newURL)
            contacts = [*contacts, *parsedData[0]["contact_array"]] # Fill in the contacts
            
            nextPage = parsedData[0]["next_page"]

            # Show background stats (Total contacts, total calls, overall time since starting)
            if showStats:
                print("Total Contacts: ", len(contacts)) 
                print("Iterations: ", counter)
                print(currentDatetime - startDatetime)

                currentDatetime = datetime.now()
                counter += 1

        return contacts


    def UploadContacts(self):
        '''
        * This will make a post request to update the contacts in Mailchimp 
        ''' 
        pass


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
