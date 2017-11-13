import discord
import json
import requests
import re
import asyncio
from objects import glob
from objects import discordmessage as dMessage
from objects import user as userObject
from ripple import MessageHandle as ripple
from helpers import stringhelper as stringHelper

@glob.discordclient.event
async def on_ready():
	print("Discord bot {} with id {} has logged in.".format(glob.discordclient.user.name, glob.discordclient.user.id))

async def HandleCommand(msg):
	#Handle message if discord_snowflake is in our account list
	if msg.author.id in glob.irc_clients.keys():
		if msg.content.startswith('.help'):
			em = discord.Embed(description=".help       List all commands\n.status    Return status of an user ingame [.status sunpy]", colour=0x0000FF)
			em.set_author(name="Commands", icon_url="http://i.imgur.com/CEYdeUi.png")
			await msg.channel.send(embed=em)
			return True
		elif msg.content.startswith('.status') or msg.content.startswith('.lookup'):
			m = msg.content.split(' ', 1)
			if len(m) >= 2:
				safe_usr_name = "_".join(m[1:]).lower()
				if safe_usr_name in glob.cached_users.keys():
					usr = glob.cached_users[safe_usr_name]
					silences = usr.silenced
					color = min(silences * 16, 255) * 65536 + (255 - min(silences * 16, 255)) * 256
					em = discord.Embed(description="ID: {}\nUsername_Safe: {}\nSilences: {}".format(usr.userid, usr.username_safe, silences), colour=color)
					em.set_author(name=usr.username, icon_url=usr.avatar)
					await msg.channel.send(embed=em)
				else:
					await msg.channel.send("{} was not found.".format(safe_usr_name))
			else:
				await msg.channel.send("Missing arguments. [Usage: `.lookup sunpy`]")
			return True
	else:
		return False

@glob.discordclient.event
async def on_message(msg):
	if msg.author.bot:  #Dont care about messages from bot accounts
		return

	if msg.channel.category.name in glob.ignore_categories:
		await HandleCommand(msg)
		return

	#Handle message if discord_snowflake is in our account list
	if msg.author.id in glob.irc_clients.keys():
		is_command = await HandleCommand(msg)
		if not is_command:
			await msg.delete()
			await ForwardDiscordMessage(msg)
	else:
		await msg.delete()

async def HandleMessage(ircclient, channel, user, message):
	#Cache user details if they are new
	if not user.lower() in glob.cached_users.keys():
		userObject.User(user)

	if await ripple.handle(ircclient, channel, user, message):
		return

	no_lower_user = user
	channel = channel.lower()		#Discord channels only accept lowercase
	user = user.lower()				#^
	message = message.replace("@", "(@)")		#Quickfix to disable highlights
	
	private = True
	if channel.startswith("#"):
		private = False
		channel = channel[1:] #Remove first char so we got the raw channel name

	if not private:
		#Adds highlights
		for c in glob.irc_clients.values():
			if c.always_highlight or c.connection.is_connected():
				for highlight in c.highlights:
					message = stringHelper.Replace("[^a-zA-Z0-9_\-]{1}" + c.usr_name.lower() + "[^a-zA-Z0-9_\-]{1}", "<@{}>".format(c.discord_snowflake), message, pad_left=1, pad_right=1, wrap=True, flags=re.I)
		#for k, v, in glob.highlight_list.items():
			#message = stringHelper.Replace("[^a-zA-Z0-9_\-]{1}" + k + "[^a-zA-Z0-9_\-]{1}", v, message, pad_left=1, pad_right=1, wrap=True, flags=re.I) #re.sub(k, v, message, flags=re.IGNORECASE)
	
	try:
		c = glob.discordclient.get_guild(glob.settings["discord_guild"])
		cats = c.categories
		#chas = c.text_channels
		if private:
			if not any(x.name in ircclient.usr_name for x in cats):
				cat = await c.create_category(ircclient.usr_name, overwrites={ c.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),  glob.discordclient.get_user(ircclient.discord_snowflake): discord.PermissionOverwrite(add_reactions=True, read_messages=True, send_messages=True, embed_links=True, manage_messages=True, read_message_history=True, ) })
			else:
				cat = next(x for x in cats if x.name == ircclient.usr_name)

			if not any(x.name in user for x in cat.channels):
				chan = await c.create_text_channel(user, category=cat)
			else:
				chan = next(x for x in cat.channels if x.name == user)

			hooks = await chan.webhooks()
			if len(hooks) == 0:
				hook = await chan.create_webhook(name="{}/{}".format(cat.name, chan.name))
			else:
				hook = hooks[0]
		else:
			if not any(x.name == glob.settings["discord_main_category"] for x in cats):
				cat = await c.create_category(glob.settings["discord_main_category"])
			else:
				cat = next(x for x in cats if x.name == glob.settings["discord_main_category"])
			
			if not any(x.name in channel for x in cat.channels):
				chan = await c.create_text_channel(channel, category=cat)
			else:
				chan = next(x for x in cat.channels if x.name == channel)
			
			hooks = await chan.webhooks()
			if len(hooks) == 0:
				hook = await chan.create_webhook(name="#{}".format(chan.name))
			else:
				hook = hooks[0]

		message = dMessage.DiscordMessage(no_lower_user.replace(" ", "_"), message) #Convert to discordmessage object for json serialization
		query = json.dumps(message.__dict__)
		req = requests.post("{}/slack".format(hook.url), data=query)
	except Exception as e:
		we.fprint("ERROR: {}".format(e))

async def HandleSelfMessage(client, chan, msg):
	#Cache user details if they are new
	if not client.usr_name.lower() in glob.cached_users.keys():
		userObject.User(client.usr_name)
	
	try:
		hooks = await chan.webhooks()
		if len(hooks) == 0:
			hook = await chan.create_webhook(name="{}/{}".format(chan.category.name, chan.name))
		else:
			hook = hooks[0]
		
		msg = dMessage.DiscordMessage(client.usr_name.replace(" ","_"), msg)
		query = json.dumps(msg.__dict__)
		req = requests.post("{}/slack".format(hook.url), data=query)
	except Exception as e:
		we.fprint("ERROR: {}".format(e))

async def ForwardDiscordMessage(msg):
	client = glob.irc_clients[msg.author.id]

	if not client.connection.is_connected(): #Make sure client is online, if not try reconnect and if not warn user and return
		connected = client.tryReconnect()
		if not connected:
			await msg.channel.send("<@{}> Your bot were unable to connect... please try again.".format(msg.author.id))
			return

	cat = msg.channel.category.name
	chan = msg.channel.name
	if glob.settings["discord_main_category"] == cat:
		chan = "#{}".format(chan)
	else:
		chan = glob.cached_users[chan.lower()].username_safe
		await HandleSelfMessage(client, msg.channel, msg.content)
	client.send_message(chan, msg.content)