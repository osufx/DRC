from objects import glob

class DiscordMessage(object):
	def __init__(self, user, msg):
		self.username = user
		self.icon_url = glob.cached_users[user].avatar
		self.text = msg
	