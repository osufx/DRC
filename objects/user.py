import requests
import json
from objects import glob

def getID(u):
		url = "http://{}/api/v1/users/whatid?name={}".format(glob.settings["osu_srv_frontend"], u)
		res = requests.get(url)
		json_data = json.loads(res.text)
		return json_data["id"]

def getUsername(i):
	url = "http://{}/api/v1/users?id={}".format(glob.settings["osu_srv_frontend"], i)
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
		glob.cached_users[username_safe.lower()] = self

	def lookup(self):
		self.userid = getID(self.username_safe)
		self.username = getUsername(self.userid)
		self.avatar = "http://a.{}/{}".format(glob.settings["osu_srv_frontend"], self.userid)
		glob.cached_users[self.username_safe.lower()] = self
		glob.sql.cursor.execute("INSERT INTO cached_users VALUES ('{}', '{}', '{}', '{}', '{}');".format(self.userid, self.username, self.username_safe, self.avatar, self.silenced))
	
	def updateSilence(self):
		glob.sql.cursor.execute("UPDATE cached_users SET silenced = '{}' WHERE userid = {};".format(self.silenced, self.userid))