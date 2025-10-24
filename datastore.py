from dotenv import load_dotenv
import requests
import os
import json

class DataStore:
    BASE_URL = "https://apis.roblox.com/cloud/v2/universes"

    def __init__(self, api_key, universe_id, datastore_name, userid):
        self.api_key = api_key
        self.datastore_name = datastore_name
        self.userid = str(userid)
        self.universe_id = universe_id
        
        self.entry_url = f"{self.BASE_URL}/{self.universe_id}/data-stores/{self.datastore_name}/entries/{self.userid}"
        self.set_url = f"{self.BASE_URL}/{self.universe_id}/data-stores/{self.datastore_name}/entries"

    def _get_headers(self, include_content_type=False):
        headers = {
            "x-api-key": self.api_key
        }
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def get_datastore(self):
        try:
            response = requests.get(self.entry_url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                print(f"No entry found for user {self.userid}.")
                return None
            print(f"HTTP Error getting datastore: {err}")
        except requests.exceptions.RequestException as err:
            print(f"Request Error getting datastore: {err}")
        return None

    def update_datastore(self, new_value):
        payload = {
            "keyName": self.userid,
            "value": json.dumps(new_value)
        }
        
        try:
            response = requests.post(
                self.set_url, 
                headers=self._get_headers(include_content_type=True), 
                data=json.dumps(payload)
            )
            response.raise_for_status()
            print("SUCCESS!!!!")
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error updating datastore: {err.response.status_code} - {err.response.text}")
        except requests.exceptions.RequestException as err:
            print(f"Request Error updating datastore: {err}")
        return None


if __name__ == "__main__":
    load_dotenv()
    
    api_token = os.getenv("ROBLOX_TOKEN")
    
    if not api_token:
        print("Error: ROBLOX_TOKEN not found in .env file.")