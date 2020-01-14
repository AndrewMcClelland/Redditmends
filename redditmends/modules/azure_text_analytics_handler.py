#https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/quickstarts/python

import requests

class TextAnalyticsHandler():
	def __init__(self, kv):
		self.key = kv.get_keyvault_secret("textAnalytics-key")
		self.endpoint = kv.get_keyvault_secret("textAnalytics-endpoint")

	def get_languages(self, texts):
		api_url = self.endpoint + "/text/analytics/v2.1/languages"

		id_count = 0

		documents = {"documents": []}
		for text in texts:
			doc = {"id": f"{id_count}", "text": f"{text}"}
			documents["documents"].append(doc)
			id_count += 1

		return self.__send_text_analytics_request(api_url, documents)

	def get_sentiment(self, texts):
		api_url = self.endpoint + "/text/analytics/v2.1/sentiment"

		# Need to get languages for texts to hit keyphrase endpoint
		# texts_langs = self.get_languages(texts)

		documents = {"documents": []}
		count = 0
		for text in texts:
			text_id = str(count)
			text_string = text
			# language = text["detectedLanguages"][0]["iso6391Name"]
			language = "en"
			doc = {"id": f"{text_id}", "language": f"{language}", "text": f"{text_string}"}
			documents["documents"].append(doc)

			count += 1

		return self.__send_text_analytics_request(api_url, documents)

	def get_key_phrases(self, texts):
		api_url = self.endpoint + "/text/analytics/v2.1/keyphrases"

		# Need to get languages for texts to hit keyphrase endpoint
		# texts_langs = self.get_languages(texts)

		documents = {"documents": []}
		count = 0
		for text in texts:
			text_id = str(count)
			text_string = text
			# language = text["detectedLanguages"][0]["iso6391Name"]
			language = "en"
			doc = {"id": f"{text_id}", "language": f"{language}", "text": f"{text_string}"}
			documents["documents"].append(doc)

			count += 1

		return self.__send_text_analytics_request(api_url, documents)

	def get_entities(self, texts):
		api_url = self.endpoint + "/text/analytics/v2.1/entities"

		id_count = 0

		documents = {"documents": []}
		for text in texts:
			doc = {"id": f"{id_count}", "text": f"{text}"}
			documents["documents"].append(doc)
			id_count += 1

		return self.__send_text_analytics_request(api_url, documents)

	def __send_text_analytics_request(self, url, body):
		headers = {"Ocp-Apim-Subscription-Key": self.key}
		response = requests.post(url, headers=headers, json=body)
		return response.json()