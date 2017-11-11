import irc.bot
import irc.strings
from objects import glob

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
		#TODO: Make discord channel inside the category (Do not assume it already exist even if it is created as users can delete them at any time)
	
	def send_message(self, channel, msg):
		self.connection.privmsg(channel, msg)


class IRCClientBot(IRCClientUser):
	def __init__(self, usr_name, usr_token):
		IRCClientUser.__init__(self, "-1", usr_name, usr_token, True, True, [])
	
	def on_pubmsg(self, c, e):
		IRCClient.on_pubmsg(self, c, e)
		for msg in e.arguments:
			self.HandleMessage(e.target, e.source, msg)

	def on_privmsg(self, c, e):
		IRCClient.on_privmsg(self, c, e)
		c.privmsg(e.target, "This is a bot account. All messages will be ignored.")
	
	def HandleMessage(self, chan, user, message):
		message = message.replace("@", "(@)")		#Quickfix to disable highlights
		
		#Adds highlights
		for k, v, in glob.highlight_list.items():
			message = message.replace(k, v)
		
		#TODO: Forward message to discord
		try:
			#webhook = 
			#req = requests.post("{}/slack".format(webhook), data=query)
			pass
		except:
			pass


	def on_part(self, c, e):
		#check if its one of the ircClient users and login if they left
		pass