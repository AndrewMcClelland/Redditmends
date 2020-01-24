import requests

class RedditHandler():

	def __init__(self, kv):

		base_url = "https://reddit.com/"

		data = {"grant_type": "password",
						"username": kv.get_keyvault_secret("reddit-username"),
						"password": kv.get_keyvault_secret("reddit-password")}

		auth = requests.auth.HTTPBasicAuth(kv.get_keyvault_secret("reddit-appKey"),
												kv.get_keyvault_secret("reddit-secret"))

		req = requests.post(base_url + "api/v1/access_token",
							data = data,
							headers = {"user-agent": kv.get_keyvault_secret("reddit-userAgent")},
							auth = auth).json()

		token = "bearer" + req["access_token"]

		self.base_url = "https://oauth.reddit.com/"
		self.headers = {"Authorization": token, "User-Agent": kv.get_keyvault_secret("reddit-userAgent")}