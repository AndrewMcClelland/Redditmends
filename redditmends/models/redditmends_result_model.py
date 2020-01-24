class RedditmendsResultModel():

	def parse_result_data(self, search_term, num_submissions, num_comments, num_unique_keywords, top_comments, top_comment_score, top_keywords, top_keywords_count):
		self.search_term = search_term
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
			top_comments_string += "{0}':\t'{1}\n".format(comment.author, comment.body)

		for keyword in self.top_keywords:
			top_keywords_string += "'{0}',".format(keyword.keyword)

		return """\n\nRedditmends result for search_term: '{0}'\n
					Number of submissions parsed = \t{1}\n
					Number of comments parsed = \t{2}\n
					Number of unique keywords = \t{3}\n
					Highest voted comment scores = \t{4}\n
					Highest voted comments found = '\t{5}'\n
					Highest common keyword count = \t{6}\n
					Most common keywords = \t{7}\n\n""".format(
						self.search_term,
						self.num_submissions,
						self.num_comments,
						self.num_unique_keywords,
						self.top_comment_score,
						top_comments_string,
						self.top_keywords_count,
						top_keywords_string
					)