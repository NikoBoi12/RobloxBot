import os
from dotenv import load_dotenv
import requests
import json
from cachetools import TTLCache

load_dotenv()

# Configuration for API
apiToken = os.getenv("ROBLOX_TOKEN")


cache = {}

# Function to list entries from the datastore
def list_entries(data_name, page_num=1, page_size=10, page_token=None):
    url = f"https://apis.roblox.com/cloud/v2/universes/6037884519/ordered-data-stores/{data_name}/scopes/global/entries"

    if data_name not in cache:
        cache[data_name] = TTLCache(maxsize=1024, ttl=300)
    elif page_num in cache[data_name]:
        return cache[data_name][page_num]
    
    headers = {
        "x-api-key": apiToken,
        "Content-Type": "application/json"
    }

    params = {
        "max_page_size": page_size,
        "order_by": "value desc",
    }
    
    if page_token:
        params["page_token"] = page_token

    # Send GET request to the API
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        cache[data_name][page_num] = response.json()
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    

def NextLeaderPage(data_name, entries, page_num):
    if not entries:
        return
    
    next_cursor = entries.get("nextPageToken")
    page_two_data = list_entries(data_name, page_num=page_num, page_token=next_cursor)

    return page_two_data


def GetLeaderboard(data_name):
    return list_entries(data_name)


def get_user(user_id):
    url = f"https://apis.roblox.com/cloud/v2/users/{user_id}"


    if "players" not in cache:
        cache["players"] = TTLCache(maxsize=1024, ttl=300)
    elif user_id in cache["players"]:
        return cache["players"][user_id]
    
   

    headers = {
        "x-api-key": apiToken,
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        cache["players"][user_id] = response.json()
        entries = response.json()
        return entries 
    else:
        print(f"Error: {response.status_code} - {response.text} - {user_id}")
        returnTable = {
            "name": "unknown",
            }
        
        return returnTable
