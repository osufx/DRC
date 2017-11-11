from threading import Thread

from objects import glob
from objects import sqlHelper
from objects import discordbot

glob.sql = sqlHelper.Mysql("localhost", "root", "toor", "irc_forward_new")
glob.sql.LoadFromDatabase()

#Create all the irc clients
for client in glob.irc_clients.values():
	Thread(target=client.start).start()

glob.discordclient.run(glob.settings["discord_token"])