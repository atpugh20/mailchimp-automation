import requests

class Application:
    def __init__(self):
        print("Application built.")

    def Run(self):
        self.TestRequest()

    def TestRequest(self):
        url = "https://pokeapi.co/api/v2/pokemon/"


        print(f"Requesting from {url}")
        response = requests.get(url)

        if response.status_code == 200:
            print(f"Data recieved from {url}\n") 
            data = response.json()
            print(data)
        else:
            print(f"Error: {response.status_code}")
