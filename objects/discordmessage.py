from objects import glob

class DiscordMessage(object):
	def __init__(self, user, msg):
		self.username = glob.cached_users[user.lower()].username
		self.icon_url = glob.cached_users[user.lower()].avatar
		self.text = msg
	