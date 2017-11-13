import irc.bot
import irc.strings
import asyncio
import discord
import requests
import json
import time
from objects import glob
from objects import discordbot

def sawait(coro, loop): #Thanks Nyo-chan <3
    """
    Runs a coroutine in IOLoop `loop` in a synchronous function

    :param coro: future
    :param loop: IOLoop
    :return:
    """
    return asyncio.run_coroutine_threadsafe(coro, loop).result()

class Reconnect(irc.bot.ReconnectStrategy):
	def run(self, bot):
		print("{} was disconnected.".format(bot.usr_name))
		while not bot.connection.is_connected():
			time.sleep(6) #Just incase something happened to the user while they try to connect
			connected = bot.tryReconnect()
			if not connected: #We didnt connect; retry in 1 min
				time.sleep(60)

class IRCClient(irc.bot.SingleServerIRCBot):
	def __init__(self, srv_addr, srv_port, usr_name, usr_token):
		self.usr_name = usr_name
		irc.bot.SingleServerIRCBot.__init__(self, [(srv_addr, srv_port, usr_token)], usr_name, usr_name, recon=Reconnect())
		print("IRCClient {} has been created!".format(usr_name))

	def on_welcome(self, c, e):
		for channel in glob.settings["irc_srv_channels"].split(","):
			c.join(channel)
	
	def on_nicknameinuse(self, c, e):
		c.disconnect()

	def on_privmsg(self, c, e):
		for msg in e.arguments:
			print("@{} #{} => {}".format(self.usr_name, e.source, msg))

	def on_pubmsg(self, c, e):
		for msg in e.arguments:
			print("@{} {}:{} => {}".format(self.usr_name, e.target, e.source, msg))
	
	def on_action(self, c, e):
		for msg in e.arguments:
			print("@{} {}:{} => {} -> {}".format(self.usr_name, e.target, e.source, e.type, msg))

	def isOnline(self):
		req = requests.get("http://c.{}/api/v1/isOnline?u={}".format(glob.settings["osu_srv_frontend"], self.usr_name))
		status = json.loads(req.text)
		return status["result"]

	def tryReconnect(self):
		print("{}: Checking if user is online...".format(self.usr_name))
		if not self.isOnline():
			self.jump_server()
			print("{}: Reconnecting".format(self.usr_name))
			return True
		else:
			print("{}: User is already logged in... waiting".format(self.usr_name))
			return False

class IRCClientUser(IRCClient):
	def __init__(self, discord_snowflake, usr_name, usr_token, allow_dm, always_online, highlights, always_highlight = False):
		self.discord_snowflake = discord_snowflake
		self.allow_dm = allow_dm
		self.always_online = always_online
		self.highlights = highlights
		self.always_highlight = always_highlight
		IRCClient.__init__(self, glob.settings["irc_srv_addr"], glob.settings["irc_srv_port"], usr_name, usr_token)

	def on_pubmsg(self, c, e):
		pass

	def on_action(self, c, e):
		IRCClient.on_action(self, c, e)
		if not e.target.startswith("#"):
			for msg in e.arguments:
				sawait(discordbot.HandleAction(self, e.target, e.source, msg), glob.discordloop)
	
	def on_privmsg(self, c, e):
		IRCClient.on_privmsg(self, c, e)
		if not self.allow_dm:
			return
		for msg in e.arguments:
			sawait(discordbot.HandleMessage(self, e.target, e.source, msg), glob.discordloop)
	
	def send_message(self, channel, msg):
		self.connection.privmsg(channel, msg)
		print("@{} {} <= {}".format(self.usr_name, channel, msg))

class IRCClientBot(IRCClientUser):
	def __init__(self, usr_name, usr_token):
		IRCClientUser.__init__(self, "-1", usr_name, usr_token, True, True, [])
	
	def on_pubmsg(self, c, e):
		IRCClient.on_pubmsg(self, c, e)
		for msg in e.arguments:
			sawait(discordbot.HandleMessage(self, e.target, e.source, msg), glob.discordloop)

	def on_privmsg(self, c, e):
		IRCClient.on_privmsg(self, c, e)
		c.privmsg(e.source, "This is a bot account. All messages will be ignored.")
	
	def on_action(self, c, e):
		IRCClient.on_action(self, c, e)
		if e.target.startswith("#"):
			for msg in e.arguments:
				sawait(discordbot.HandleAction(self, e.target, e.source, msg), glob.discordloop)

"""
	def on_part(self, c, e):
		if e.source in glob.irc_snowflake_link.keys(): #Check if its one of our irc client accounts
			req = requests.get("http://c.{}/api/v1/isOnline?u={}".format(glob.settings["osu_srv_frontend"], e.source))
			status = json.loads(req.text)
			if not status["result"]:
				glob.irc_clients[glob.irc_snowflake_link[e.source]].connect()
"""