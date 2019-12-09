from datetime import datetime, timedelta

class RedditSubmissionModel():

	def parse_submission_data(self, submission):
		self.author = submission.get('author')
		self.post_date = datetime.fromtimestamp(submission['created_utc']).strftime('%c') if submission.get('created_utc') else None
		self.id = submission.get('id')
		self.flair = submission.get('link_flair_text')
		self.subreddit = submission.get('subreddit')
		self.title = submission.get('title')