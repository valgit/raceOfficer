import discord
from discord import embeds
from discord.ext import commands
import io
import aiohttp
import logging
import json
import random
import os

class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="config", help="definie role config" )
    #@commands.has_role('race officer VRI')
    async def config(self,ctx,ro: str, skpname: str):
        return

def setup(bot):
    bot.add_cog(settings(bot))
