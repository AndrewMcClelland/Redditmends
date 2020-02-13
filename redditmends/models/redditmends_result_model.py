from datetime import datetime

class RedditmendsResultModel():

	def parse_result_data(self, search_term, runtime, num_submissions, num_comments, num_unique_keywords, top_comments, top_comment_score, top_keywords, top_keywords_count):
		self.search_term = search_term
		self.runtime = runtime
		self.num_submissions = num_submissions
		self.num_comments = num_comments
		self.num_unique_keywords = num_unique_keywords
		self.top_comments = top_comments
		self.top_comment_score = top_comment_score
		self.top_keywords = top_keywords
		self.top_keywords_count = top_keywords_count

	# Called when 'print(RedditmendsResultModel())' is called
	def __str__(self):
		top_comments_string = ""
		top_keywords_string = ""
		for comment in self.top_comments:
			top_comments_string += "Comment id = {0} posted at {1} by {2}<br>Score = {3} and sentiment = {4}<br>'{5}'<br>".format(
										comment.id,
										datetime.fromtimestamp(comment.created_utc).strftime('%c'),
										comment.author,
										comment.score,
										comment.sentiment,
										comment.body)

		for keyword in self.top_keywords:
			top_keywords_string += "'{0}',".format(keyword.keyword)

		return """<br><br>Redditmends result for search_term: '{0}'<br>
					Runtime = \t{1}<br>
					Number of submissions parsed = \t{2}<br>
					Number of comments parsed = \t{3}<br>
					Number of unique keywords = \t{4}<br>
					Highest voted comment scores = \t{5}<br>
					Highest voted comments found = '\t{6}'<br>
					Highest common keyword count = \t{7}<br>
					Most common keywords = \t{8}<br><br>""".format(
						self.search_term,
						self.runtime,
						self.num_submissions,
						self.num_comments,
						self.num_unique_keywords,
						self.top_comment_score,
						top_comments_string,
						self.top_keywords_count,
						top_keywords_string
					)