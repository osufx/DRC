import asyncio
import discord
from objects import glob
from objects import user as userObject
from osu import api

async def handle(ircclient, channel, user, message):
	#Handle bot stuff
	if user.lower() == "fokabot":
		if message.find("has been silenced for the following reason:") != -1:
			target = message.split(' ')[0]
			if target.lower() not in glob.cached_users.keys():
				userObject.User(target)
			target = glob.cached_users[target.lower()]
			target.silenced += 1
			target.updateSilence()

	return False

async def handleAction(user, message):
	try:
		message_split = message.split(" ")

		action = message_split[1]
		url = message[(message.find("[") + 1):].split(" ")[0]

		url_split = url.split("/")
		beatmap_lookup_method = url_split[-2]
		beatmap_lookup = url_split[-1]

		beatmap_data = api.GetBeatmapData(beatmap_lookup_method, beatmap_lookup)
		
		color = glob.action_color[action]
		if color is None:	#Just incase somehow its an action I am missing
			color = glob.action_color["listening"]
		
		title = "{} - {}".format(beatmap_data[0]["artist"], beatmap_data[0]["title"])
		description = "{}...".format(action.capitalize())

		author_name = user.username
		author_url = "http://ripple.moe/u/{}".format(user.userid)
		author_icon = user.avatar
		thumb = "https://b.ppy.sh/thumb/{}l.jpg".format(beatmap_data[0]["beatmapset_id"])

		#if beatmap_lookup_method == "b":	#We can get spesific data for this beatmap as its not a beatmap set
			#return

		embed = discord.Embed(title=title, description=description, url=url, color=color)
		embed.set_author(name=author_name, url=author_url, icon_url=author_icon)
		embed.set_thumbnail(url=thumb)

		if action in ["playing","watching"]:
			embed.set_footer(text=message[-(message[::-1].find("]")):])

		return embed
	except Exception as e:
		author_name = user.username
		author_url = "http://ripple.moe/u/{}".format(user.userid)
		author_icon = user.avatar

		embed = discord.Embed(description=message, color=discord.Color.from_rgb(255, 255, 255))
		embed.set_author(name=author_name, url=author_url, icon_url=author_icon)
		return embed
