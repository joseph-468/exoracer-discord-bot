import os
import requests
import discord
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

# Setup
intents = Intents.all()
client = commands.Bot(command_prefix=">", intents=intents)
client.remove_command("help")
data_fields = ["UserID", "Country", "ClubName", "Skin", "Trail", "HookSkin"]
data = None


# Open data
def get_player_data():
    global data
    # Get data from the web
    try:
        url = "https://exo.lgms.nl/?api&users"
        json_data = requests.get(url=url).json()
        fields = json_data["fields"]
        json_data = json_data["data"]
        data = [None] * len(fields)
        for i in range(len(fields)):
            data[i] = [j[i] for j in json_data]
    except Exception:
        print("Error gathering data.")
        return "Error"
    return "No Error"


# Functions
@client.event
async def on_ready():
    print("Bot started.")


@client.command()
async def get_data(ctx, player_name=None):
    global data
    # Return if empty name
    if player_name is None:
        await ctx.send("Please enter a name.")
        return
    # Find player
    if data is None:
        player_data_success = get_player_data()
        if player_data_success == "Error":
            await ctx.send("Error gathering data.")
            return
    player_indexes = []
    for x, i in enumerate(data[1]):
        if i == player_name:
            player_indexes.append(x)
    # Return if player not found
    if not player_indexes:
        await ctx.send("Player not found.")
        return
    # Send data
    embeds = []
    for x, i in enumerate(player_indexes):
        embed = discord.Embed(title=player_name, color=0x7244CD)
        embed_fields = [data[0][i], data[6][i], data[9][i],
                        data[3][i], data[4][i], data[5][i]]
        for y, j in enumerate(embed_fields):
            if not j:
                embed_fields[y] = "null"
        for y, j in enumerate(embed_fields):
            embed.add_field(name=data_fields[y], value=j, inline=False)
        embeds.append(embed)
    for embed in embeds:
        await ctx.send(embed=embed)


# Run bot
if __name__ == "__main__":
    load_dotenv()
    client.run(os.getenv("TOKEN"))
