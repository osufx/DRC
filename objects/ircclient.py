import irc.bot
import irc.strings
import asyncio
import discord
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
		if not bot.connection.is_connected():
			print("disconnected")
			bot.jump_server()

class IRCClient(irc.bot.SingleServerIRCBot):
	def __init__(self, srv_addr, srv_port, usr_name, usr_token):
		self.usr_name = usr_name
		irc.bot.SingleServerIRCBot.__init__(self, [(srv_addr, srv_port, usr_token)], usr_name, usr_name, recon=Reconnect())
		print("IRCClient {} has been created!".format(usr_name))

	def on_welcome(self, c, e):
		for channel in glob.settings["irc_srv_channels"].split(","):
			c.join(channel)

	def on_privmsg(self, c, e):
		for msg in e.arguments:
			print("@{} #{} => {}".format(self.usr_name, e.source, msg))

	def on_pubmsg(self, c, e):
		for msg in e.arguments:
			print("@{} {}:{} => {}".format(self.usr_name, e.target, e.source, msg))

class IRCClientUser(IRCClient):
	def __init__(self, discord_snowflake, usr_name, usr_token, allow_dm, always_online, highlights):
		self.discord_snowflake = discord_snowflake
		self.allow_dm = allow_dm
		self.always_online = always_online
		self.highlights = highlights
		IRCClient.__init__(self, glob.settings["irc_srv_addr"], glob.settings["irc_srv_port"], usr_name, usr_token)

	def on_pubmsg(self, c, e):
		pass
	
	def on_privmsg(self, c, e):
		IRCClient.on_privmsg(self, c, e)
		for msg in e.arguments:
			sawait(discordbot.HandleMessage(self, e.target, e.source, msg), glob.discordloop)
	
	def send_message(self, channel, msg):
		self.connection.privmsg(channel, msg)

class IRCClientBot(IRCClientUser):
	def __init__(self, usr_name, usr_token):
		IRCClientUser.__init__(self, "-1", usr_name, usr_token, True, True, [])
	
	def on_pubmsg(self, c, e):
		IRCClient.on_pubmsg(self, c, e)
		for msg in e.arguments:
			sawait(discordbot.HandleMessage(self, e.target, e.source, msg), glob.discordloop)

	def on_privmsg(self, c, e):
		IRCClient.on_privmsg(self, c, e)
		c.privmsg(e.target, "This is a bot account. All messages will be ignored.")

	def on_part(self, c, e):
		#check if its one of the ircClient users and login if they left
		pass