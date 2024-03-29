import discord
from discord import embeds
from discord.ext import commands
import io
import aiohttp
import logging
import json
import random
import os

def write_data(file,data):
    """for writing to the file"""
    #serdata = safe_serialize(data)
    with open(file,'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        #f.write(data)
    #logging.info('write disable')

def read_data(file):
    """for reading the file"""
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None

class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="config")
    #@commands.has_role('race officer VRI')    
    async def config(self,ctx,ro: discord.Role, skpname: discord.Role, prefix:str = None):
        """definit les roles config
        Parameters
        ------------
        ro: str [Required]
            race officer role
        skipper: str [Required]
            default participant role
        prefix : str
            race prefix name (prefix-name)
        """         
        await ctx.send('will set : "{}" for default participant role'.format(skpname) )
        await ctx.send('will set : "{}" for Race Officer role'.format(ro) )
        #await ctx.send('will use : "{}" for prefix (prefix-xxx) '.format(prefix) )
        fileset = ctx.guild.name + '_settings.json'
        logging.info("setting for guild : {} saved".format(ctx.guild.name))
        guildSet = {}
        guildSet['ro_name'] = ro.name
        guildSet['ro_mention'] = ro.mention
        guildSet['ro_id'] = ro.id
        guildSet['skipper_name'] = skpname.name
        guildSet['skipper_mention'] = skpname.mention
        guildSet['skipper_id'] = skpname.id
        if prefix:
            guildSet['prefix'] = prefix + '-' # always add a '-' by def
        else:
            guildSet['prefix'] = 'race-du-'

        write_data(fileset,guildSet)
        return

    @commands.command(name="show")
    #@commands.has_role('race officer VRI')    
    async def show(self,ctx):
        """display bot config
        """
        fileset = ctx.guild.name + '_settings.json'
        guildSet = read_data(fileset)

        await ctx.send('participant : "{}" role'.format(guildSet['skipper_name']) )
        await ctx.send('Race Officer : "{}" role'.format(guildSet['ro_name']) )
        pfx = guildSet.get('prefix')
        if pfx:
            await ctx.send('race prefix is : "{}" '.format(pfx) )
        else:
            await ctx.send('no race prefix')


def setup(bot):
    bot.add_cog(settings(bot))
