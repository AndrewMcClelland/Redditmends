from datetime import datetime, timedelta

class RecommendationModel():

	def __init__(self, keyword):
		self.keyword = keyword

	def add_sentiment(self, sentiment):
		self.sentiment = sentiment

	def add_query_keyword(self, query_word):
		self.query_word = query_word

	def add_post_id(self, post_id):
		self.post_id = post_id

	def add_count(self, count):
		self.count = count