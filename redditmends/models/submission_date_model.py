from datetime import datetime, timedelta

class SubmissionDateModel():

	def __init__(self, subreddit, title, created_utc, post_id):
		self.subreddit = subreddit
		self.title = title
		self.created_utc = created_utc
		self.post_id = post_id