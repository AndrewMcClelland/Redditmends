from datetime import datetime, timedelta

class RedditCommentModel():

	def parse_comment_data(self, comment):
		self.author = comment.get('author')
		self.body = comment.get('body')
		self.post_date = datetime.fromtimestamp(comment['created_utc']).strftime('%c') if comment.get('created_utc') else None
		self.link_id = comment.get('link_id')
		self.id = comment.get('id')
		self.num_comments = comment.get('num_comments')
		self.parent_id = comment.get('parent_id')
		self.score = comment.get('score')	# note that this may change after it is fetched and stored in database
		self.flair = comment.get('link_flair_text')
		self.subreddit = comment.get('subreddit')
		self.subreddit_id = comment.get('subreddit_id')
		self.total_awards_received = comment.get('total_awards_received')

	def add_keywords(self, keywords):
		self.keywords = keywords