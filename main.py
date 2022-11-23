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
def get_player_data(read_from_file):
    global data
    try:
        if read_from_file:
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
        data_import_success = get_player_data(READ_FROM_FILE)
        if not data_import_success:
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

    # Runs if multiple players with same name are found and a specific one isn't specified
    if len(player_indexes) > 1 and player_number is None:
        path = str(player_indexes[0]) + ".txt"
        file = open(path, "w")
        # Store defined fields under player name in file for each player found
        for x, i in enumerate(player_indexes):
            file.write(f"{player_name} {x+1}\n")
            fields = [data[0][i], data[6][i], data[9][i],
                      data[3][i], data[4][i], data[5][i]]
            # Write fields to convert empty string to avoid errors
            for y, j in enumerate(fields):
                if not j:
                    j = "null"
                file.write(f"{data_fields[y]}: {j}\n")
            file.write("\n")
        file.close()
        # Sends file, deletes it and returns
        await ctx.send(file=discord.File(path, f"{player_name}.txt"))
        if os.path.exists(path):
            os.remove(path)
        return

    # Runs if player number is specified
    elif player_number is not None:
        # Returns with error if player number is out of range
        if player_number < 1 or player_number > len(player_indexes):
            await ctx.send("Player not found.")
            return
        # Removes all other players besides the one specified
        player_indexes = [player_indexes[player_number-1]]
    # Creates embed with defined fields for all players found
    embed = discord.Embed(title=player_name, color=0x7244CD)
    embed_fields = [data[0][player_indexes[0]], data[6][player_indexes[0]], data[9][player_indexes[0]],
                    data[3][player_indexes[0]], data[4][player_indexes[0]], data[5][player_indexes[0]]]
    # Add fields to embed and converts empty string to avoid errors
    for y, j in enumerate(embed_fields):
        if not j:
            j = "null"
        embed.add_field(name=data_fields[y], value=j, inline=False)
    # Send embed
    await ctx.send(embed=embed)


@client.command()
async def update_data(ctx):
    # Send data update message, update data then delete the message
    update_message = await ctx.send("Updating...")
    data_import_success = get_player_data(False)
    await update_message.delete()
    # Send success message
    if not data_import_success:
        await ctx.send("Data failed to update.")
    else:
        await ctx.send("Data updated successfully.")


# Import token from env file and run the bot
if __name__ == "__main__":
    load_dotenv()
    client.run(os.getenv("TOKEN"))
