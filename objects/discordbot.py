import discord
from objects import glob

@glob.discordclient.event
async def on_ready():
	print("Discord bot {} with id {} has logged in.".format(glob.discordclient.user.name, glob.discordclient.user.id))

@glob.discordclient.event
async def on_message(msg):
	if msg.author.bot:  #Dont care about messages from bot accounts
		return

	#if int(msg.author.id) in 