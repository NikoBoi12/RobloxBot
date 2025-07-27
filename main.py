import discord
from discord.ext import commands
import logging
import os
import datastore
from authorizedUsers import authorizedUsers

from dotenv import load_dotenv

import orderedDataStore
import leaderBoards

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def is_allowed_user():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id in authorizedUsers
    return discord.app_commands.check(predicate)

@bot.event 
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


"""
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
 
    if "say hi to bestie for me bot" in message.content.lower():
        while True:
            await message.channel.send("hi bestie <@1282867739178045532>")
        
"""

@bot.tree.command(name="toprollers", description="Gets the top rollers in the game!")
async def toproller(interaction: discord.Interaction):
    await interaction.response.defer()

    top_rollers = orderedDataStore.GetLeaderboard("Rolls")
    embed = leaderBoards.CreateLeaderEmbed(top_rollers['orderedDataStoreEntries'], "Rollers", 1)
    view = leaderBoards.ButtonView(data_name="Rolls", most_recent_pages=top_rollers, leader_pages=[embed], name="Rollers")

    await interaction.followup.send(embed=embed, view=view)


@bot.tree.command(name="toptippers", description="Gets the top tippers in the game!")
async def toptippers(interaction: discord.Interaction):
    await interaction.response.defer()

    top_rollers = orderedDataStore.GetLeaderboard("Tips")
    embed = leaderBoards.CreateLeaderEmbed(top_rollers['orderedDataStoreEntries'], "Tippers", 1)
    view = leaderBoards.ButtonView(data_name="Tips", most_recent_pages=top_rollers, leader_pages=[embed], name="Tippers")

    await interaction.followup.send(embed=embed, view=view)


@bot.tree.command(name="givedarkdollars", description="Gives darkdollars to a user")
@discord.app_commands.describe(userid="The roblox userid", amount="Amount of DarkDollars to give")
@is_allowed_user()
async def givedarkdollars(interaction: discord.Interaction, userid: int, amount: int):
    await interaction.response.defer()

    datastore_class = datastore.DataStore(userid=userid)
    current_data = datastore_class.get_Datastore()

    if "value" in current_data and "DarkDollars" in current_data["value"]:
        current_data["value"]["DarkDollars"] += amount
    else:
        await interaction.followup.send(f"Failed to give {userid} Dark Dollars")
        return

    datastore_class.update_datastore(json=current_data["value"])

    await interaction.followup.send(f"Sucessfully gave {userid} Dark Dollars")



@bot.tree.command(name="giveaura", description="Gives an aura to a user")
@discord.app_commands.describe(userid="The roblox userid", aura_name="What aura to give to that user")
@is_allowed_user()
async def givedarkdollars(interaction: discord.Interaction, userid: int, aura_name: str):
    await interaction.response.defer()

    datastore_class = datastore.DataStore(userid=userid)
    current_data = datastore_class.get_Datastore()

    if "value" in current_data and "Index" in current_data["value"]:
        if not (aura_name in current_data["value"]["Index"]):
            current_data["value"]["Index"].append(aura_name)
        else:
            await interaction.followup.send(f"User already has {aura_name}")
            return
        
    else:
        await interaction.followup.send(f"Failed to give {userid} {aura_name}")
        return

    datastore_class.update_datastore(json=current_data["value"])

    await interaction.followup.send(f"Sucessfully gave {userid} {aura_name}")


if token:
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
else:
    print("ERROR: DISCORD_TOKEN not found in .env file.")
