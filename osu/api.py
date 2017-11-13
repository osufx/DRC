import requests
import json
from objects import glob

def GetBeatmapData(beatmap_lookup_method, beatmap_lookup):
	req = requests.get("https://osu.ppy.sh/api/get_beatmaps?k={}&{}={}".format(glob.settings["osu_api_key"], beatmap_lookup_method, beatmap_lookup))
	data = json.loads(req.text)
	return data