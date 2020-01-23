class RedditmendsResultModel():

	def parse_result_data(self, top_comments, top_comment_score, top_keywords, top_keywords_count):
		self.top_comments = top_comments
		self.top_comment_score = top_comment_score
		self.top_keywords = top_keywords
		self.top_keywords_count = top_keywords_count