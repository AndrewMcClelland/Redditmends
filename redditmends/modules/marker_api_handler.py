import requests
import json

# Handler for Marker Trademark API
class MarkerAPIHandler():
	def __init__(self, kv):
		self.username = kv.get_keyvault_secret("markerAPI-username")
		self.api_pass = kv.get_keyvault_secret("markerAPI-APIpass")
		self.base_url = "https://markerapi.com/api/v2/trademarks/{0}/{1}/status/{2}/start/1/username/{3}/password/{4}"

	def fetch_trademarks(self, trademark_term, is_active = True):
		active_string = "active" if is_active else "all"
		trademark_url = self.base_url.format(
			"trademark",
			trademark_term,
			active_string,
			self.username,
			self.api_pass
		)

		try:
			trademarks = requests.get(trademark_url, timeout = None)
			if(trademarks.status_code != 200):
				print("WARNING: did not receive trademark results for GET on url: ", trademark_url)
				return []
			return json.loads(trademarks.content.decode("utf-8"))
		except:
			raise