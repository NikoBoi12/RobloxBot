import logging
import os
import sys

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

import datastore
import orderedDataStore
import leaderBoards
from authorizedUsers import authorizedUsers

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("discord.log", encoding="utf-8", mode="w"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

AUTHORIZED_USER_IDS = set(authorizedUsers)


def is_allowed_user():
    """A check function to verify the command user is in the authorized list."""
    async def predicate(interaction: discord.Interaction) -> bool:
        is_allowed = interaction.user.id in AUTHORIZED_USER_IDS
        if not is_allowed:
            LOGGER.warning(f"Unauthorized command attempt by {interaction.user} (ID: {interaction.user.id}) for command: {interaction.command.name}")
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return is_allowed
    return app_commands.check(predicate)


@bot.event
async def on_ready():
    """Event handler for when the bot is ready and has connected to Discord."""
    LOGGER.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        LOGGER.info(f"Synced {len(synced)} application command(s)")
    except Exception as e:
        LOGGER.error(f"Failed to sync commands: {e}")


async def _show_leaderboard(interaction: discord.Interaction, data_key: str, leaderboard_name: str):
    """A helper function to display a paginated leaderboard."""
    await interaction.response.defer()
    try:
        leaderboard_data = orderedDataStore.GetLeaderboard(data_key)
        if not leaderboard_data or 'orderedDataStoreEntries' not in leaderboard_data:
            await interaction.followup.send(f"Could not retrieve leaderboard data for '{leaderboard_name}'.")
            return

        embed = leaderBoards.CreateLeaderEmbed(leaderboard_data['orderedDataStoreEntries'], leaderboard_name, 1)
        view = leaderBoards.ButtonView(data_name=data_key, most_recent_pages=leaderboard_data, leader_pages=[embed], name=leaderboard_name)

        await interaction.followup.send(embed=embed, view=view)
    except Exception as e:
        LOGGER.error(f"Error in /top{leaderboard_name.lower()} command: {e}", exc_info=True)
        await interaction.followup.send("An error occurred while fetching the leaderboard.", ephemeral=True)


@bot.tree.command(name="toprollers", description="Gets the top rollers in the game!")
async def toproller(interaction: discord.Interaction):
    """Displays a paginated leaderboard for the top 'Rollers'."""
    await _show_leaderboard(interaction, data_key="Rolls", leaderboard_name="Rollers")


@bot.tree.command(name="toptippers", description="Gets the top tippers in the game!")
async def toptippers(interaction: discord.Interaction):
    """Displays a paginated leaderboard for the top 'Tippers'."""
    await _show_leaderboard(interaction, data_key="Tips", leaderboard_name="Tippers")


@bot.tree.command(name="givedarkdollars", description="Gives darkdollars to a user")
@app_commands.describe(userid="The Roblox userid", amount="Amount of DarkDollars to give")
@is_allowed_user()
async def givedarkdollars(interaction: discord.Interaction, userid: int, amount: int):
    """Gives a specified amount of DarkDollars to a Roblox user."""
    await interaction.response.defer()

    try:
        datastore_class = datastore.DataStore(userid=userid)
        current_data = datastore_class.get_Datastore()

        if current_data and "value" in current_data and "DarkDollars" in current_data["value"]:
            current_data["value"]["DarkDollars"] += amount
        else:
            LOGGER.warning(f"Failed to give DarkDollars: Could not find user {userid} or 'DarkDollars' field.")
            await interaction.followup.send(f"Failed to give {userid} Dark Dollars. User data might be missing or corrupt.")
            return

        datastore_class.update_datastore(json=current_data["value"])
        await interaction.followup.send(f"Successfully gave {amount} Dark Dollars to {userid}. New balance: {current_data['value']['DarkDollars']}")
        LOGGER.info(f"{interaction.user} gave {amount} DarkDollars to {userid}.")

    except Exception as e:
        LOGGER.error(f"Error in /givedarkdollars command for user {userid}: {e}", exc_info=True)
        await interaction.followup.send(f"An error occurred while processing the request for {userid}.", ephemeral=True)


@bot.tree.command(name="giveaura", description="Gives an aura to a user")
@app_commands.describe(userid="The Roblox userid", aura_name="What aura to give to that user")
@is_allowed_user()
async def giveaura(interaction: discord.Interaction, userid: int, aura_name: str):
    """Gives a specified aura to a Roblox user."""
    await interaction.response.defer()

    try:
        datastore_class = datastore.DataStore(userid=userid)
        current_data = datastore_class.get_Datastore()

        if current_data and "value" in current_data and "Index" in current_data["value"]:
            if not isinstance(current_data["value"]["Index"], list):
                LOGGER.warning(f"User {userid}'s 'Index' field is not a list. Attempting to fix.")
                current_data["value"]["Index"] = []

            if aura_name not in current_data["value"]["Index"]:
                current_data["value"]["Index"].append(aura_name)
            else:
                await interaction.followup.send(f"User {userid} already has the aura '{aura_name}'.")
                return
        else:
            LOGGER.warning(f"Failed to give aura: Could not find user {userid} or 'Index' field.")
            await interaction.followup.send(f"Failed to give {userid} '{aura_name}'. User data might be missing or corrupt.")
            return

        datastore_class.update_datastore(json=current_data["value"])
        await interaction.followup.send(f"Successfully gave {userid} the aura '{aura_name}'.")
        LOGGER.info(f"{interaction.user} gave aura '{aura_name}' to {userid}.")

    except Exception as e:
        LOGGER.error(f"Error in /giveaura command for user {userid}: {e}", exc_info=True)
        await interaction.followup.send(f"An error occurred while processing the request for {userid}.", ephemeral=True)


def main():
    """Main entry point for the bot."""
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN, log_handler=None, log_level=logging.DEBUG)
    else:
        LOGGER.critical("ERROR: DISCORD_TOKEN not found in .env file.")


if __name__ == "__main__":
    main()