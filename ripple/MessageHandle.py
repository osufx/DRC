import asyncio
from objects import glob
from objects import user as userObject

async def handle(ircclient, channel, user, message):
	if user.lower() == "fokabot":
		if message.find("has been silenced for the following reason:") != -1:
			target = message.split(' ')[0]
			if target.lower() not in glob.cached_users.keys():
				userObject.User(target)
			target = glob.cached_users[target.lower()]
			target.silenced += 1
			target.updateSilence()

	if user.lower() in ["fokabot"]:
		return True
	return False