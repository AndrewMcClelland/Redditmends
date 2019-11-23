import requests
import csv

from data.pushshift_api_params import pushshift_api_parameters
import data.parse_pushshift_data

class PushshiftHandler():

	def __init__(self):
		self = self

	def fetch_comments(self, params):
		api_endpoint = self.__get_api_endpoint_url(params=params, api_endpoint_type="comment")
		return self.__get_pushshift_api_results(api_endpoint)

	def fetch_submissions(self, params):
		api_endpoint = self.__get_api_endpoint_url(params=params, api_endpoint_type="submission")
		return self.__get_pushshift_api_results(api_endpoint)

	def fetch_subreddits(self, params):
		api_endpoint = self.__get_api_endpoint_url(params=params, api_endpoint_type="subreddit")
		return self.__get_pushshift_api_results(api_endpoint)

	def __get_api_endpoint_url(self, params, api_endpoint_type):
		endpoint_url =  f"https://api.pushshift.io/reddit/%s/search?" % api_endpoint_type

		# params comes in form ["parameter1=value1", "parameter2=value2", etc..]
		for param in params:
			split_param = param.split("=")
			key = split_param[0].lower()
			value = split_param[1].lower()

			if(key not in pushshift_api_parameters or (pushshift_api_parameters[key][0] != "All Endpoints" and pushshift_api_parameters[key][0] != api_endpoint_type)):
				print(f"Parameter '{key}'' invalid!!!")
				exit

			endpoint_url += "&" + param

		return endpoint_url

	def __get_pushshift_api_results(self, endpoint_url):
		try:
			pushshift_results = requests.get(endpoint_url, headers = {'User-Agent': "redditmends_bot by /u/adoublemc"}, timeout=10)
			if(pushshift_results.status_code != 200):
				print("WARNING: did not receive results for GET on url: ", endpoint_url)
				return []
			return pushshift_results.json()['data']
		except:
			raise