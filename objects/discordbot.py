import discord
import json
from objects import glob

@glob.discordclient.event
async def on_ready():
	print("Discord bot {} with id {} has logged in.".format(glob.discordclient.user.name, glob.discordclient.user.id))

@glob.discordclient.event
async def on_message(msg):
	if msg.author.bot:  #Dont care about messages from bot accounts
		return

	#Handle message if discord_snowflake is in our account list
	if msg.author.id in glob.irc_clients.keys():
		if msg.content.startswith('.help'):
			em = discord.Embed(description=".help       List all commands\n.status    Return status of an user ingame [.status sunpy]\n.online    Show yourself as online on irc\n.offline    Show yourself as offline in irc", colour=0x0000FF)
			em.set_author(name="Commands", icon_url="http://i.imgur.com/CEYdeUi.png")
			await glob.discordclient.send_message(msg.channel, embed=em)
		elif msg.content.startswith('.status') or msg.content.startswith('.lookup'):
			m = msg.content.split(' ', 1)
			if len(m) >= 2:
				safe_usr_name = "_".join(m[1:])
				if safe_usr_name in glob.cached_users.keys():
					usr = glob.cached_users[safe_usr_name]
					silences = usr.silenced
					color = min(silences * 16, 255) * 65536 + (255 - min(silences * 16, 255)) * 256
					em = discord.Embed(description="ID: {}\nUsername_Safe: {}\nSilences: {}".format(usr.userid, usr.username_safe, silences), colour=color)
					em.set_author(name=usr.username, icon_url=usr.avatar)
					await glob.discordclient.send_message(msg.channel, embed=em)
				else:
					await glob.discordclient.send_message(msg.channel, "{} was not found.".format(safe_usr_name))
			else:
				await glob.discordclient.send_message(msg.channel, "Missing arguments. [Usage: `.lookup sunpy`]")
		else:
			await msg.delete()
			ForwardDiscordMessage(msg.author.id, msg.content, msg.channel)
	else:
		await msg.delete()

async def HandleMessage(ircclient, channel, user, message):
	channel = channel.lower()		#Discord channels only accept lowercase
	user = user.lower()				#^
	message = message.replace("@", "(@)")		#Quickfix to disable highlights
	
	private = True
	if channel.startswith("#"):
		private = False
		channel = channel[1:] #Remove first char so we got the raw channel name

	if not private:
		#Adds highlights
		for k, v, in glob.highlight_list.items():
			message = message.replace(k, v)
	
	try:
		c = glob.discordclient.get_guild(glob.settings["discord_guild"])
		cats = c.categories
		#chas = c.text_channels
		if private:
			if not any(x.name in ircclient.usr_name for x in cats):
				cat = await c.create_category(ircclient.usr_name) #ADD: overwrites=self.getPermissionOverwrite()
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
			if not any(x.name in glob.settings["discord_main_category"] for x in cats):
				cat = await c.create_category(glob.settings["discord_main_category"]) #ADD: overwrites=self.getPermissionOverwrite()
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

		message = DiscordMessage(user, message) #Convert to discordmessage object for json serialization
		query = json.dumps(message.__dict__)
		req = requests.post("{}/slack".format(hook), data=query)
	except:
		pass

def ForwardDiscordMessage(id, msg, channel):
	client = glob.irc_clients[id]
	cat = channel.category.name
	chan = channel.name
	if glob.settings["discord_main_category"] == cat:
		chan = "#{}".format(chan)
	client.send_message(chan, msg)
	print("id={} msg={} channel={}".format(id, msg, "{}/{}".format(channel.category, channel.name)))