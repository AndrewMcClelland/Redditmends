from datetime import datetime, timedelta

class RedditCommentModel():

	def parse_comment_data(self, comment):
		self.author = comment.get('author')
		self.body = comment.get('body')
		# self.post_date = datetime.fromtimestamp(comment['created_utc']).strftime('%c') if comment.get('created_utc') else None
		self.created_utc = comment.get("created_utc")
		self.link_id = comment.get('link_id')
		self.id = comment.get('id')
		self.parent_id = comment.get('parent_id')
		self.score = comment.get('score')	# note that this may change after it is fetched and stored in database
		self.subreddit = comment.get('subreddit')
		self.subreddit_id = comment.get('subreddit_id')
		self.total_awards_received = comment.get('total_awards_received')

	def add_keywords(self, keywords):
		self.keywords = keywords

	def add_sentiment(self, sentiment):
		self.sentiment = sentiment

	def __str__(self):
		top_keywords_string = ""
		for keyword in self.keywords:
			top_keywords_string += "'{0}',".format(keyword.keyword)

		return "Comment id = {0} posted at {1} by {2}\nScore = {3}, sentiment = {4}, and relevant keywords: {5}\n'{6}'".format(
			self.id,
			datetime.fromtimestamp(self.created_utc).strftime('%c'),
			self.author,
			self.score,
			self.sentiment,
			top_keywords_string,
			self.body)