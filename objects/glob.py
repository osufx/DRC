import discord

settings = {}
irc_clients = {}
cached_users = {}
highlight_list = {}
sql = None
discordclient = discord.Client()
discordloop = discordclient.loop
ignore_categories = None
irc_snowflake_link = {}