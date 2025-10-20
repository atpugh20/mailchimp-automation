import requests

class Application:
    def __init__(self):
        print("Application built.")

    def Run(self):
        self.GetMC()

    def GetMC(self):
        url = "https://pokeapi.co/api/v2/pokemon/"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            self.PrintDict(data)
        else:
            print(f"Error: {response.status_code}")
