import os
import requests
import json
import discord
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

# Setup
intents = Intents.all()
client = commands.Bot(command_prefix=">", intents=intents)
client.remove_command("help")
data_fields = ["UserID", "Country", "ClubName", "Skin", "Trail", "HookSkin"]
data = []
READ_FROM_FILE = True


# Import data
def get_player_data():
    global data
    try:
        if READ_FROM_FILE:
            try:
                # Imports data from file
                file = open("data.json", "r")
                json_data = json.load(file)
                file.close()
            except Exception:
                # Imports data from L3's site and saves it locally
                json_data = requests.get(url="https://exo.lgms.nl/?api&users").json()
                file = open("data.json", "w")
                json.dump(json_data, file, indent=3)
                file.close()
        else:
            # Imports data from L3's site and saves it locally
            json_data = requests.get(url="https://exo.lgms.nl/?api&users").json()
            file = open("data.json", "w")
            json.dump(json_data, file, indent=3)
            file.close()
        # Convert data from json to multiple strings
        fields = json_data["fields"]
        json_data = json_data["data"]
        data = [[]] * len(fields)
        for i in range(len(fields)):
            data[i] = [j[i] for j in json_data]
    except Exception:
        # Returns error found
        return False
    # Returns no error found
    return True


# Commands
@client.command()
async def get_data(ctx, player_name=None, player_number=None):
    global data
    # Returns with error if name argument is missing
    if player_name is None:
        await ctx.send("Please enter a name.")
        return
    # Convert player number to integer and returns with an error if not an integer
    if player_number is not None:
        try:
            player_number = int(player_number)
        except ValueError:
            await ctx.send("Player number must be an integer.")
            return
    # If data is not in memory import it, returns if there is an error
    if not data:
        player_data_success = get_player_data()
        if not player_data_success:
            await ctx.send("Error gathering data.")
            return
    # Searches through all name fields and stores index of matching names
    player_indexes = []
    for x, i in enumerate(data[1]):
        if i == player_name:
            player_indexes.append(x)
    # Returns if player is not found
    if not player_indexes:
        await ctx.send("Player not found.")
        return

    # Send data when multiple accounts exist
    if len(player_indexes) > 1 and player_number is None:
        file = open(str(player_indexes[0]) + ".txt", "w")
        path = player_indexes[0]
        for x, i in enumerate(player_indexes):
            file.write(f"{player_name} {x+1}\n")
            fields = [data[0][i], data[6][i], data[9][i],
                      data[3][i], data[4][i], data[5][i]]
            for y, j in enumerate(fields):
                if not j:
                    fields[y] = "null"
            for y, j in enumerate(fields):
                file.write(f"{data_fields[y]}: {j}\n")
            file.write("\n")
        file.close()
        await ctx.send(file=discord.File(f"{path}.txt", f"{player_name}.txt"))
        if os.path.exists(str(player_indexes[0]) + ".txt"):
            os.remove(str(player_indexes[0]) + ".txt")
        return
    elif player_number is not None:
        if player_number < 1 or player_number > len(player_indexes):
            await ctx.send("Player not found.")
            return
        player_indexes = [player_indexes[player_number-1]]
    # Send data when one account exists
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


# Import token from env file and run bot
if __name__ == "__main__":
    load_dotenv()
    client.run(os.getenv("TOKEN"))
