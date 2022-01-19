import discord
from discord import embeds
from discord.ext import commands
import io
import aiohttp
import logging
import json
import random
import os
from string import Template

#tools functions
def partition (list_in, n):
    """Slice a list into n randomly-sized parts.
    """
    random.shuffle(list_in)
    #return [list_in[0::n] , list_in[n::]]
    return [list_in[x::n] for x in range(n)]
    #return [list_in[i:i+6] for i in x range(n)]

def buildList (participants):
    """extract online into a list
    """
    list_of_values = ['']
    j = 0
    for u in participants:
            if participants[u]['online'] == True:
                if j==0:
                    list_of_values[0]=participants[u]['name']
                else:
                    list_of_values.append(participants[u]['name'])
                j+=1
    return list_of_values

#participants = {}

def safe_serialize(obj):
    """exclude non seriealisable objetc from json"""
    default = lambda o: f"<<non-serializable: {type(o).__qualname__}>>"
    return json.dumps(obj, default=default)

def write_data(file,data):
    """for writing to the file"""
    #serdata = safe_serialize(data)
    #with open(file,'w') as f:
    #        f.write(serdata)
    logging.info('write disable')

def read_data(file):
    """for reading the file"""
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None


    
class raceOfficer(commands.Cog):
    regatta = {}
    database = ''
    skip_role = 'skipper'

    def __init__(self, bot):
        self.bot = bot
        self.database = os.getenv('FILE') # ? NoneType
        logging.info('will store data in '+self.database) 
        logging.info('loading bck')
        self.database = read_data(self.database)
        print(self.regatta)
        # handle role
        self.skip_role = os.getenv('code_role')
        logging.info('will add role : {} to code channel'.format(self.skip_role))
        return


    def findChannel(self,ctx,name):
        """ find a channel by name
        """
        logging.info('findChannel : {}'.format(name))
        try:
            for channel in ctx.guild.text_channels:
                if name in channel.name.lower():
                #       logging.info('current channel : {}'.format(channel))
                    mChan = channel
                    break
            return mChan
        except:
            return None

    def readIC(self,race):
        """ TODO: read the IC template
        """
        with open('ic.md', encoding='utf8') as f:
            contents = f.read()
        f.close()
        # apply template ?
        temp = Template(contents)
        return temp.substitute(racename=race['name'],
            date=race['date'],time=race['time'],
            code="codes-" + race['name'])
        #return contents

    def buildEmbed(self,race):
        embed = discord.Embed(title='⛵ new {} regatta'.format(race['name']), 
            description='regatta at : {} {}'.format(race['date'],race['time']), 
            color=discord.Color.blue())
        tmpl = self.readIC(race)
        embed.add_field(name='**🇫🇷Avis de course 🇫🇷**', value=tmpl,inline=False)
        embed.add_field(name="Registration", 
            value='Use command : ``!register _srid_ "_boat name_" `` \n``!online`` will be required', 
            inline=False)
        return embed

    def getRaceKey(self, ctx, name):
        """ define key for race"""
        key=ctx.guild.name+"_"+name
        return key

    def makeKey(self,ctx):
        """ define the key for the race
        channel name should be xxx-xxx-racename
        """
        # name should be last in channel name
        name = ctx.channel.name.split("-")[-1]
        key=ctx.guild.name+"_"+name
        return key

    #just test
    @commands.command(name="officer", help="server alive and info")
    async def officer(self,ctx):
        #await ctx.send('pong')
        await ctx.send('⛵ I am your race officer helper bot ⛵')
        await ctx.send("discord.py v{}".format(discord.__version__))
        await ctx.send('role particpant will be :' + self.skip_role)
        

    # 
    # create regatta at date time
    # stored in dict
    @commands.command(name="create", pass_context=True, help="register for this regatta")
    async def create(self,ctx, name: str, date: str, time: str):
        await ctx.send("registering new regatta "+ name)
        # need to create channel
        logging.info("register regatta "+ name + " at " + date)
        try:
            # look for race channel

            key = self.getRaceKey(ctx, name)
            #key = self.makeKey(ctx)
            #print("key will be : {key}".format(key=key))

            race = {}
            race['name'] = name
            race['date'] = date
            race['time'] = time
            race['channel']= ctx.channel
            #race['channel'] = mChan
            #race['code'] = channel
            race['status'] = True  # we accept registration
            race['skipper'] = dict()
            self.regatta[key]=race

            # create code channel
            #get orig categorie
            regatta = "race-" + name
            raceChan = self.findChannel(ctx,regatta)
            logging.info('regata is in "'+raceChan.category.name+'"')
            mChan = "codes-" + name
            #annChannel = await ctx.guild.create_text_channel(mChan, category=ctx.channel.category, topic="code régate {}".format(name))
            annChannel = await ctx.guild.create_text_channel(mChan, category=raceChan.category, topic="code régate {}".format(name))

            # create a RO channelfor announcement
            #print('ch : {}'.format(ctx.channel))
            #print('cat : {}'.format(ctx.channel.category))

            #category = discord.utils.get(ctx.guild.categories, name="Salons textuels")
            #print(category)
            mChan = "info-" + name
            #annChannel = await ctx.guild.create_text_channel(mChan, category=ctx.channel.category, topic="info régate {}".format(name))
            #role = discord.utils.get(ctx.author.guild.roles, name='members VRI')
            #perms = annChannel.overwrites_for(role) # ctx.guild.default_role)
            #perms.send_messages=False
            #perms.read_message_history=True
            #await annChannel.set_permissions(ctx.guild.default_role, overwrite=perms)
            
            #await annChannel.send(tmpl)
            # add a mention ?
            annChannel = self.findChannel(ctx,mChan)
            logging.info('announce channel is :'+annChannel.name)
            # end

            try:
                #regSafe = safe_serialize(regatta)
                #print(regSafe)
                logging.info('saving data')
                write_data(self.database,self.regatta)
            except Exception as e:
                await ctx.send('file error {} database {}'.format(e,self.database))

            #await ctx.send('new regatta at : {} {}, please register here'.format(date,time))
            #await ctx.send('use command : !register _srid_ "_boat name_"')

            embed = self.buildEmbed(race)
            #embed.set_thumbnail(url="https://i.imgur.com/axLm3p6.jpeg")
            #embed.set_footer(text="!online will be required") #if you like to
            info = await annChannel.send(embed=embed)
            race['info'] = info
            #print('msg id : {}'.format(info.id))
            #user = discord.utils.get(ctx.guild.members, name="members VRI")
            user = discord.utils.get(ctx.guild.roles, name='members VRI')

            await annChannel.send("{} n'oubliez pas de vous enregistrer".format(user.mention))
            
            await info.pin()

        except Exception as e:
            await ctx.send('There was an error running this command ' + str(e)) #if error
        ## get the message
        message = ctx.message
        ## delete the message
        #await message.delete()
        return

  

    #
    # list all current regatta
    # check for : Race officer VRI VRI (ESF) ?
    #
    @commands.command(name="listraces", help="list all servers regatta" )
    #@commands.has_role('race officer VRI')
    @commands.is_owner()
    #@commands.has_role('raceofficer')
    async def listrace(self,ctx):
        logging.info("listing ")
        
        msg = ''
        for r in self.regatta:
            tmpmsg='{key}, **{name}** ,{date} ,{time}, {num}, {state}  \n'.format(
                        key=r, name=self.regatta[r]['name'],
                        date=self.regatta[r]['date'],time=self.regatta[r]['time'],
                        num=len(self.regatta[r]['skipper']),state=self.regatta[r]['status'])
                    #print(msg)
            msg = msg + tmpmsg
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send('no race')
        return

    # 
    # register <srid> <boatd name>
    # register a boat to current regatta
    # need to be in goot channel 
    @commands.command(name="register", pass_context=True, help="register for this regatta <sailrank><boat name>")
    async def register(self,ctx, sr: int, boatid: str):
            member = ctx.author

            logging.info('registering {}'.format(member))
            #key=ctx.guild.name+"_"+ctx.channel.name
            key = self.makeKey(ctx)
            
            race = self.regatta.get(key)
            if not race:
                await ctx.send('no race define')
                return
            else:
                participants = race['skipper']

                if race['status'] == True:
                    user = {}
                    user['name'] = member.display_name
                    user['sr'] = sr
                    user['boat'] = boatid
                    user['online'] = False
                    user['mention'] = member.mention
                    user['member'] = member.id
                    print(member.id)
                    #user = discord.utils.get(guild.members, id=123749839583)
                    #uid = await ctx.guild.fetch_member(member.id)
                    #print('user{}'.format(uid))

                    #print(user)
                    participants[ctx.author.display_name] = user

                    msg = ''
                    for u in participants:
                        tmpmsg='**{user}** ,{rank} ,{boat}  \n'.format(user=participants[u]['name'],
                            rank=participants[u]['sr'],boat=participants[u]['boat'])
                        #print(msg)
                        msg = msg + tmpmsg
                    
                    embed = self.buildEmbed(race)
                    embed.add_field(name="Participants", value=msg, inline=False)

                    info = race['info']
                    #info = await ctx.fetch_message(infoid)
                    await info.edit(embed=embed)
                    write_data(self.database,self.regatta)

                    await ctx.send('👍 ' + user['name'] + ' will register your boat : ' + user['boat'])
                else:
                    await ctx.send('🚫 : registration are close for this race')
         


    # 
    # unregister registration
    # race channel
    #
    @commands.command(name="unregister", help="unregister for this regatta")
    async def unregister(self,ctx):
        member = ctx.author
        #key=ctx.guild.name+"_"+ctx.channel.name
        key = self.makeKey(ctx)
        race = self.regatta[key]
        participants = race['skipper']

        logging.info('unregistering {}'.format(member))

        if member.display_name in participants:
            #remove role for user
            try:
                role = discord.utils.get(member.guild.roles, name=self.skip_role)
                await member.remove_roles(role)
            except Exception as e:
                await ctx.send('There was an error running this command ' + str(e)) #if error       

            del participants[ctx.author.display_name]

            await ctx.send('ok! ' + ctx.author.display_name + ' will be unregistered')
        else:
            await ctx.send(ctx.author.display_name +" you are not registered")

  
    #
    # annonce 'online' pour la regatte
    # give acces to code
    # race channel
    #
    @commands.command(name="online", help="enable esailors" , aliases=['connecte','yes'])
    async def online(self,ctx):
        member = ctx.author
        #key=ctx.guild.name+"_"+ctx.channel.name
        key = self.makeKey(ctx)
        race = self.regatta[key]
        participants = race['skipper']

        logging.info('online for {}'.format(member))

        if member.display_name in participants:
            participants[member.display_name]['online'] = True
            try:
                # for test : 849645701947719730
                role = discord.utils.get(member.guild.roles, name=self.skip_role)
                #print(role)
                await member.add_roles(role)
            except Exception as e:
                await ctx.send('There was an error running this command ' + str(e)) #if error
            #add reaction to message
            #emoji = '\N{THUMBS UP SIGN}'
            emoji = '✅' # \N{WHITE CHECK MARK}' u"\u2705"
            
            await ctx.message.add_reaction(emoji)
        else:
            emoji = '❌'
            await ctx.message.add_reaction(emoji)
            await ctx.send("you are not registered")

    #
    # close the resgistration process
    #
    @commands.command(name="close", help="close registration" )
    @commands.has_role('race officer VRI')
    async def close(self,ctx,name: str):
        """
        close the registration for the race
        RO channel
        """
        #key=ctx.guild.name+"_"+name
        key = self.getRaceKey(ctx, name)
        #key = self.makeKey(ctx)
        race = self.regatta.get(key)
        if not race:
            await ctx.send('no race define')
            return
        else:
            race['status'] = False
            participants = race['skipper']

            logging.info('closing regatta {}'.format(race['name']))

            nb = len(participants)
            # TODO : embed
            msg= 'registered users are : {nb} '.format(nb=nb)
            await ctx.send(msg)
            await ctx.send("registration are closed")
            ## get the message
            message = ctx.message
            ## delete the message
            await message.delete()
            return

    #
    # open the resgistration process
    #
    @commands.command(name="open", help="(re)open registration" )
    @commands.has_role('race officer VRI')
    async def open(self,ctx,name: str):
        """
        (re)open the registration for the race
        RO channel
        """
        #key=ctx.guild.name+"_"+name
        key = self.getRaceKey(ctx, name)
        #key = self.makeKey(ctx)
        race = self.regatta.get(key)
        if not race:
            await ctx.send('no race define')
            return
        else:
            race['status'] = True
            participants = race['skipper']

            logging.info('opening regatta {}'.format(race['name']))

            nb = len(participants)
            # TODO : embed
            msg= 'registered users are : {nb} '.format(nb=nb)
            await ctx.send(msg)
            await ctx.send("registration are open")
            ## get the message
            message = ctx.message
            ## delete the message
            await message.delete()
            return

    #
    # mention list user which have not send online
    #
    @commands.command(name="notify", help="mention offline users" )
    @commands.has_role('race officer VRI')
    async def notify(self,ctx, name:str):
        #key = self.makeKey(ctx)
        key = self.getRaceKey(ctx, name)
        race = self.regatta.get(key)
        if not race:
            await ctx.send('no race define')
            return
        else:
            regatta = "race-" + name
            raceChan = self.findChannel(ctx,regatta)

            participants = race['skipper']
            logging.info("notifying registered user of 'online' missing")
            msg = ''
            for u in participants:
                if participants[u]['online'] == False:
                    tmpmsg='{mention} '.format(mention=participants[u]['mention'])
                    #print(msg)
                    #await ctx.send(msg) 
                    msg = msg + tmpmsg
            else:
                if msg:
                    await raceChan.send(msg)
                    await raceChan.send("are you online ? use : $online")
                    return
        return

    #
    # cancel/delete a regatta
    # RO channel
    #
    @commands.command(name="remove", help="cancel/delete regatta" )
    #@commands.has_role('raceofficer')
    async def remove(self,ctx, name:str):
        logging.info("canceling " + name)
        #key=ctx.guild.name+"_"+name
        key = self.getRaceKey(ctx, name)
        #key = self.makeKey(ctx)
        race = self.regatta.get(key)
        if not race:
            await ctx.send('no race define for : {}'.format(name))
            return
        else:
            #await race['code'].delete()
            participants = race['skipper']

            logging.info('canceling regatta {}'.format(name))

            for u in participants:
                memberId = participants[u]['member']
                #print(member)
                try:
                    member = await ctx.guild.fetch_member(memberId)
                    role = discord.utils.get(member.guild.roles, name=self.skip_role)
                    #if role in member.roles:
                    await member.remove_roles(role)
                except Exception as e:
                    await ctx.send('There was an error running this command ' + str(e)) #if error 
            else:
                participants.clear()
                #await ctx.send("all participants are removed, regatta " + name + " remove")
                embed = discord.Embed(title='cancel regatta '.format(name), description='all participants are removed, regatta' , color = discord.Color.blue())
                embed.add_field(name='cancel by:' , value = f"{ctx.author.mention}")
                await ctx.send(embed=embed)

            await race['info'].unpin()

            # remove all associated channels
            # code channel
            mChan = "codes-" + name
            codeChan = self.findChannel(ctx,mChan)
            await codeChan.delete()

            del self.regatta[key]

            await ctx.send("ready for new one")
            ## get the message
            message = ctx.message
            ## delete the message
            await message.delete()
            return
        
    #
    # display some regatta info
    #
    @commands.command(name="status", help="list esailors online" )
    @commands.has_role('race officer VRI')
    async def status(self,ctx, name: str):
        """
        list esailor
        param:
        name: race name
        RO channel
        """
        #key = ctx.guild.name + "-" + name
        key = self.getRaceKey(ctx, name)
        # key = self.makeKey(ctx)
        race = self.regatta.get(key)
        if not race:
            await ctx.send('no race define')
            return
        else:
            participants = race['skipper']

            emoji = '⛵'
            nb = len(participants)
            msg= 'registered users are : {nb} '.format(nb=nb)
            #print(msg)
            await ctx.send(msg)
            
            msg = ''
            nb = 0
            for u in participants:
                if participants[u]['online'] == True:
                    #tmpmsg='**{user}** ,{rank} ,{boat}\n'.format(user=participants[u]['name'],
                    #    rank=participants[u]['sr'],boat=participants[u]['boat'])
                    #print(msg)
                    #msg = msg + tmpmsg
                    #print(participants[u]['name'])
                    nb = nb + 1
            else:
                await ctx.send('total online user {nb}'.format(nb=nb))
                
            #try:
                #print(msg)
            #    if msg:
            #        await ctx.send('partipant,sailrank,bateau')
            #        await ctx.send(msg)

            #except Exception as e:
            #        await ctx.send('There was an error running this command ' + str(e)) #if error 

    #
    # print list of sailrank for apply
    #
    @commands.command(name="srlist", help="get sailrank list of esailors online" )
    @commands.has_role('race officer VRI')
    async def srlist(self,ctx,name: str):
        """display sailrank of online people
        """
        #key = ctx.guild.name + "-" + name
        key = self.getRaceKey(ctx, name)
        #key = self.makeKey(ctx)
        race = self.regatta.get(key)
        if not race:
            await ctx.send('no race define')
            return
        else:
            participants = race['skipper']
            
            nb = len(participants)
            msg= 'registered users are : {nb} '.format(nb=nb)
            #print(msg)
            await ctx.send(msg)
            
            msg = ''
            nb = 0
            for u in participants:
                if participants[u]['online'] == True:
                    tmpmsg='{rank}\n'.format(rank=participants[u]['sr'])
                    #print(msg)
                    msg = msg + tmpmsg
                    #print(participants[u]['name'])
                    nb = nb + 1
            else:
                await ctx.send('total online user {nb}'.format(nb=nb))
                
            try:
                #print(msg)
                if msg:
                    await ctx.send('sailrank')
                    await ctx.send(msg)

            except Exception as e:
                    await ctx.send('There was an error running this command ' + str(e)) #if error 

    
    
    #
    #  list sailor for regatta
    #
    @commands.command(name="list", help="list registerd esailors" )
    @commands.has_role('race officer VRI')
    async def list(self,ctx,name: str):
        """
        list registered esailors
        name: race name
        in ro channel
        """
        #key=ctx.guild.name+"_"+name
        key = self.getRaceKey(ctx, name)
        #key = self.makeKey(ctx)
        race = self.regatta.get(key)
        if not race:
            await ctx.send('no race define')
            return
        else:
            participants = race['skipper']

            msg = 'race **{name}**'.format(name=race['name'])
            await ctx.send(msg)
            if race['status'] == True:
                await ctx.send('registration are open')
            else:
                await ctx.send('registration are closed')
            nb = len(participants)
            msg= 'registered users are : {nb} '.format(nb=nb)
            #print(msg)
            await ctx.send(msg)
            await ctx.send('partipant,sailrank,bateau,online')
            msg = ''
            for u in participants:
                tmpmsg='**{user}** ,{rank} ,{boat}, {on}  \n'.format(user=participants[u]['name'],
                    rank=participants[u]['sr'],boat=participants[u]['boat'],on=participants[u]['online'])
                #print(msg)
                msg = msg + tmpmsg

            if msg:
                await ctx.send(msg) 
        return

    #
    # print pool of user for apply
    # need to account for RO/SR
    #
    @commands.command(name="division", help="create pool for online users, set num repeat and Race Officer(s)" )
    @commands.has_role('race officer VRI')
    async def division(self,ctx,name: str,num:int, *args):
        """display pool division of online people
        num : number of loop
        args : race officer VRI
        """
        #key = ctx.guild.name + "-" + name
        key = self.getRaceKey(ctx, name)
        #key = self.makeKey(ctx)
        race = self.regatta.get(key)
        if not race:
            await ctx.send('no race define')
            return
        else:
            participants = race['skipper']
        
            mChan = self.findChannel(ctx,'codes')

            # args are RO/SR
            if len(args) < 4 :
                await ctx.send("**WARNING** not enough Race Officer(s) defined !")
            
            if len(args) > 0 :
                await ctx.send('{} Race officer VRI : {}'.format(len(args), ', '.join(args)))

            onlineList = buildList(participants)
            #should remove them from list
            for ro in args:
                onlineList.remove(ro)

            embed = discord.Embed(title='** pool assignement **', 
                        description=' players : {}'.format(len(args)), 
                        color = discord.Color.red())

            for x in range(num):
                part = partition(onlineList,2) # 2 is num of division
                #logging.info(part)
                # title='**race {}**'.format(x)
                for idx, div in enumerate(part):
                    if not div:
                        embed.add_field(name='--- **group {} ** ----'.format(idx), 
                            value ="empty", inline=False)
                    else:
                        embed.add_field(name='--- **group {} ** ----'.format(idx) ,
                            value = ('\n'.join(map(str, div))) , inline=False)
            else:
                await mChan.send(embed=embed)
                #logging.info(list_of_values)

            await ctx.send('group are set in codes channel')
            return


    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role (race officer VRI) for this command.')
        else:
            await ctx.send('general error ' + str(error))

 
def setup(bot):
    bot.add_cog(raceOfficer(bot))

