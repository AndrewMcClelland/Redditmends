from datetime import datetime, timedelta

class RedditSubmissionModel():

	def parse_submission_data(self, submission):
		self.author = submission.get('author')
		# self.post_date = datetime.fromtimestamp(submission['created_utc']).strftime('%c') if submission.get('created_utc') else None
		self.created_utc = submission.get('created_utc')
		self.id = submission.get('id')
		self.flair = submission.get('link_flair_text')
		self.subreddit = submission.get('subreddit')
		self.title = submission.get('title')
		self.body = submission.get('selftext')

	def add_title_keywords(self, keywords):
		self.title_keywords = keywords

	def add_body_keywords(self, keywords):
		self.body_keywords = keywords

	def add_title_sentiment(self, sentiment):
		self.title_sentiment = sentiment

	def add_body_sentiment(self, sentiment):
		self.body_sentiment = sentiment