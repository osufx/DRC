import MySQLdb
import MySQLdb.cursors
from objects import ircclient
from objects import user
from objects import glob

class Mysql(object):
	def __init__(self, host, user, passwd, db, cursorclass = MySQLdb.cursors.DictCursor):
		self.connection = MySQLdb.connect(host = host, user = user, passwd = passwd, db = db, cursorclass = cursorclass)
		self.cursor = self.connection.cursor()

	def LoadFromDatabase(self):
		#Settings
		self.cursor.execute("SELECT * FROM settings")
		rows = self.cursor.fetchall()
		for row in rows:
			glob.settings[row["name"]] = row["value_string"] if row["value_int"] == None else row["value_int"]

		#Accounts
		self.cursor.execute("SELECT * FROM accounts")
		rows = self.cursor.fetchall()
		for row in rows:
			if row["is_bot"]:
				glob.irc_clients[row["irc_username"]] = ircclient.IRCClientBot(row["irc_username"], row["irc_token"])
			else:
				glob.irc_clients[row["discord_snowflake"]] = ircclient.IRCClientUser(row["discord_snowflake"], row["irc_username"], row["irc_token"], row["allow_dm"], row["always_online"], row["highlights"])

		#Setup highlight table
		for key in glob.irc_clients.keys():
			if glob.irc_clients[key].highlights != None:
				for highlight in glob.irc_clients[key].highlights:
					glob.highlight_list[highlight] = "<@{}>".format(key)
		
		#Cached Users
		self.cursor.execute("SELECT * FROM cached_users")
		rows = self.cursor.fetchall()
		for row in rows:
			glob.cached_users[row["username_safe"]] = user.User(row["username_safe"], row["userid"], row["username"], row["avatar"], row["silenced"])