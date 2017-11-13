import discord

settings = {}
irc_clients = {}
cached_users = {}
sql = None
discordclient = discord.Client()
discordloop = discordclient.loop
ignore_categories = None
irc_snowflake_link = {}

#Used for embeds
action_color = {
		"listening":	discord.Color.from_rgb(10, 30, 120),
		"editing":		discord.Color.from_rgb(160, 60, 60),
		"playing":		discord.Color.from_rgb(140, 160, 160),
		"watching":		discord.Color.from_rgb(60, 60, 160)
	}