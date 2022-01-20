import sys

# adding Folder_2 to the system path
#sys.path.insert(0, '/Users/val/Documents/sailing/raceOfficer2/pycord')

import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import logging

# prodbot : https://discord.com/api/oauth2/authorize?client_id=919955519949668373&permissions=337960446032&scope=bot
# devbot url : https://discord.com/api/oauth2/authorize?client_id=922889780180688927&permissions=406679956560&scope=bot

logging.basicConfig(level=logging.INFO)
load_dotenv()

token = os.getenv('DISCORD_TOKEN')
prefix = os.getenv('BOT_PREFIX')

logging.info('the prefix will be '+prefix)
client = commands.Bot(command_prefix = prefix)

# 'cogs' is the folder name
# 'fun', 'mod', and 'misc' are the file names
cogs = ['cogs.tools','cogs.raceOfficer','cogs.settings']

@client.event
async def on_ready():
    logging.info(f'Logged in as: {client.user.name}')
    logging.info(f'With ID: {client.user.id}')
    async for guild in client.fetch_guilds(limit=150):
         logging.info(guild.name)

    game = discord.Game("Virtual Regatta Inshore")
    await client.change_presence(activity=game)

    for cog in cogs: # Looks for the cogs,
        client.load_extension(cog) # Loads the cogs.
    return


client.run(token)

