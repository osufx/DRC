import MySQLdb
import MySQLdb.cursors
import irc.bot
import irc.strings
import discord
import json
import requests
from threading import Thread

settings = {}
irc_clients = {}
cached_users = {}
highlight_list = {}

discordclient = discord.Client()

@discordclient.event
async def on_ready():
	print("Discord bot {} with id {} has logged in.".format(discordclient.user.name, discordclient.user.id))

@discordclient.event
async def on_message(msg):
	if msg.author.bot:  #Dont care about messages from bot accounts
		return

	#if int(msg.author.id) in 




class MySql(object):
	def __init__(self, host, user, passwd, db, cursorclass = MySQLdb.cursors.DictCursor):
		self.connection = MySQLdb.connect(host = host, user = user, passwd = passwd, db = db, cursorclass = cursorclass)
		self.cursor = self.connection.cursor()

sql = MySql("localhost", "root", "toor", "irc_forward_new")

#sql functions
def LoadFromDatabase():
	#Settings
	sql.cursor.execute("SELECT * FROM settings")
	rows = sql.cursor.fetchall()
	for row in rows:
		settings[row["name"]] = row["value_string"] if row["value_int"] == None else row["value_int"]

	#Accounts
	sql.cursor.execute("SELECT * FROM accounts")
	rows = sql.cursor.fetchall()
	for row in rows:
		if row["is_bot"]:
			irc_clients[row["discord_snowflake"]] = IRCClientUser(row["discord_snowflake"], row["irc_username"], row["irc_token"], row["allow_dm"], row["always_online"], row["highlights"])
		else:
			irc_clients[row["irc_username"]] = IRCClientBot(row["irc_username"], row["irc_token"])




#Ripple spesific functions
def getID(u):
		url = "http://{}/api/v1/users/whatid?name={}".format(settings["osu_srv_frontend"], u)
		res = requests.get(url)
		json_data = json.loads(res.text)
		return json_data["id"]

def getUsername(i):
	url = "http://{}/api/v1/users?id={}".format(settings["osu_srv_frontend"], i)
	res = requests.get(url)
	json_data = json.loads(res.text)
	return json_data["username"]

class User(object):
	def __init__(self, username_safe, userid = None, username = None, avatar = None, silenced = 0):
		self.username_safe = username_safe
		self.silenced = silenced
		if None in (userid, username, avatar):
			self.lookup()
			return
		self.userid = userid
		self.username = username
		self.avatar = avatar
		cached_users[username_safe] = self

	def lookup(self):
		self.userid = getId(self.username_safe)
		self.username = getUsername(self.userid)
		self.avatar = "http://a.{}/{}".format(settings["osu_srv_frontend"], self.userid)
		cached_users[self.username_safe] = self
		sql.cursor.execute("INSERT INTO cached_users VALUES ('{}', '{}', '{}', '{}', '{}');".format(self.userid, self.username, self.username_safe, self.avatar, self.silenced))
	
	def updateSilence(self):
		cursor.execute("UPDATE cached_users SET silence = '{}' WHERE userid = {};".format(self.silenced, self.userid))






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
		for channel in settings["irc_srv_channels"].split(","):
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
		IRCClient.__init__(self, settings["irc_srv_addr"], settings["irc_srv_port"], usr_name, usr_token)

	def on_pubmsg(self, c, e):
		pass
	
	def on_privmsg(self, c, e):
		IRCClient.on_privmsg(self, c, e)
		#TODO: Make discord channel inside the category (Do not assume it already exist even if it is created as users can delete them at any time)


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
		for k, v, in highlight_list.iteritems():
			message = message.replace(k, v)
		
		#TODO: Forward message to discord
		try:
			#webhook = 
			#req = requests.post("{}/slack".format(webhook), data=query)
			pass
		except err:
			pass


	def on_part(self, c, e):
		#check if its one of the ircClient users and login if they left
		pass



LoadFromDatabase()

#Setup highlight table
for key in irc_clients.keys():
	if irc_clients[key].highlights != None:
		for highlight in irc_clients[key].highlights:
			highlight_list[highlight] = "<@{}>".format(key)

print("{} : {}".format(len(irc_clients), irc_clients))

for client in irc_clients.values():
	print(client)
	Thread(target=client.start).start()

print("Everything is running \\o/")
discordclient.run(settings["discord_token"])