# Undertale RNG Utility Bot

This is a private Discord bot built with `discord.py` to serve as an admin panel and utility tool for a Roblox game. Its primary purpose is to manage and interact with the game's Roblox DataStores directly from Discord, allowing for admin-only data modification and public-facing leaderboards.

## ✨ Features

* **View Leaderboards:** Displays paginated, interactive leaderboards for in-game stats (e.g., Top Rollers, Top Tippers) by fetching data from `OrderedDataStore`.
* **Admin-Only Commands:** Secure commands are restricted to a predefined list of Discord user IDs (`authorizedUsers.py`).
* **Player Data Modification:**
    * `/givedarkdollars`: Safely increments a player's "DarkDollars" currency.
    * `/giveaura`: Grants a player a new "Aura" by appending it to their inventory list.
* **Direct Roblox Integration:** Uses the Roblox Open Cloud API to get and set player data in real-time.
* **Logging:** Logs all major actions, errors, and unauthorized command attempts to `discord.log`.
