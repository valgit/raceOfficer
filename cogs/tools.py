import discord
from discord.ext import commands
import io
import aiohttp
import logging
import json
import random

 #tools functions
def partition (list_in, n):
   """Slice a list into n randomly-sized parts.
   """
   random.shuffle(list_in)
   #return [list_in[0::n] , list_in[n::]]
   return [list_in[x::n] for x in range(n)]
   #return [list_in[i:i+6] for i in x range(n)]

class tools(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command() 
	async def ping(self, ctx): 
		'''
		Pong!
		'''
		await ctx.send('Pong!') #Sends a chat message. Remember to await async functions.
			
	#	 print pool of user for apply
	# need to account for RO/SR
	#
	@commands.command(name="createpool", help="create pool for online users, set num repeat" )
	#@commands.has_role('race officers')
	async def division(self,ctx,num:int, *args):
		"""display pool division of online people
		num : number of loop
		args : race officers, list of participants
		without a registerd race
		"""

		#embed = discord.Embed(title='create pool regatta', description='group pool without registered race' , color = discord.Color.blue())
		#embed.add_field(name='ask by:' , value = f"{ctx.author.mention}")
		#await mChan.send(embed=embed)
		
		#await mChan.send('{} list : {}'.format(len(args), ', '.join(args)))

		onlineList = [*args]

		embed = discord.Embed(title='** pool assignement **', 
					description=' players : {} with {} groups'.format(len(args),num), 
					color = discord.Color.red())

		embed.set_footer(text="group are set")
		#for x in range(num):
		part = partition(onlineList,num) # 2 is num of division
		logging.info(part)
			# title='**race {}**'.format(x)

		for idx, div in enumerate(part):
			if not div:
				embed.add_field(name='--- **group {} ** ----'.format(idx), 
					value ="empty", inline=False)
			else:
				embed.add_field(name='--- **group {} ** ----'.format(idx) ,
					value = ('\n'.join(map(str, div))) , inline=False)
		else:	
			await ctx.send(embed=embed)
			#logging.info(list_of_values)
		 
		#await ctx.send('group are set in codes channel')
		return
		

	#	 random select boat
	#
	@commands.command(name="shuffleboat", help="randomly select boat" )
	async def shuffleboat(self,ctx,num:int):
		"""display a randomly selected boat liste
		num : number of boat
		"""
		boatlist = ["Formule 18", "Laser", "Star", "49er", "Nacra 17", "J/70", "F50", "Offshore Racer", "AC75"," FareEast28"]
		
		if (num>10):
			await ctx.send('too many boats requiered')
		else:
			random_boat = random.choices(boatlist, k=num,False)
			await ctx.send('boats are : {}'.format(random_boat))
			await ctx.send('selection done')

def setup(bot):
	bot.add_cog(tools(bot))

