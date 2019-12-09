import praw
from datetime import datetime, timedelta

from modules.pushshift_handler import PushshiftHandler
from modules.reddit_handler import RedditHandler
from modules.inbox_handler import InboxHandler
from modules.azure_storage_handler import AzureStorageHandler
from accounts.reddit_account_info import accounts
from models.reddit_submission_model import RedditSubmissionModel

class RedditmendsBot():
	def __init__(self, username):
		try:
			self.bot = accounts[username]
		except:
			print("Invalid account username:", username)
			raise

		self.reddit = RedditHandler(self.bot)
		self.pushshift_handler = PushshiftHandler()
		self.storage_account = AzureStorageHandler()

	def run(self):
		# Initializes praw reddit instance
		self.start_time = datetime.now()
		# unread_messages = InboxHandler.read_inbox(self.reddit)
		comments = self.pushshift_handler.fetch_comments(params=["q=hello", "limit=10"])
		submissions_data = self.pushshift_handler.fetch_submissions(params=["subreddit=buildapcsales", "link_flair_text=CPU", "limit=10"])

		for sub in submissions_data:
			submission = RedditSubmissionModel()
			submission.parse_submission_data(sub)
			self.storage_account.insert_submission_entry(submission)


if __name__ == "__main__":
	bot = RedditmendsBot("redditmends_bot")
	bot.run()