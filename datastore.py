from dotenv import load_dotenv
import requests
import os

load_dotenv()

apiToken = os.getenv("ROBLOX_TOKEN")


headers = {
    "x-api-key": apiToken,
    "Content-Type": "application/json"
}


class DataStore():
    def __init__(self, userid):
          self.datastore_url = f"https://apis.roblox.com/cloud/v2/universes/6037884519/data-stores/Data/entries/{userid}"
    

    def get_Datastore(self):
        url = self.datastore_url

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
             print(f"Error: {response.status_code} - {response.text}")


    def update_datastore(self, json):
        if json:
            patch_data = {
                "value": json
            }

            response = requests.patch(self.datastore_url, headers=headers, json=patch_data)

            if response:
                print("SUCESS!!!!")
                pass
            else:
                print(f"Error: {response.status_code} - {response.text}")
         

         


"""

    datastore = DataStore(userid=28249453)

    datastore.get_Datastore()

    data = datastore.Datastore["value"]

    data["DarkDollars"] += 10

    patch_data = {
        "value": data
    }

    response = requests.patch(datastore.datastore_url, headers=headers, json=patch_data)
    print(response)
"""