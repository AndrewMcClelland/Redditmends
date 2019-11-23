import praw
from datetime import datetime

from modules.pushshift_handler import PushshiftHandler
from modules.reddit_handler import RedditHandler
from modules.inbox_handler import InboxHandler
from accounts.account_info import accounts

class RedditmendsBot():
	def __init__(self, username):
		try:
			self.bot = accounts[username]
		except:
			print("Invalid account username:", username)
			raise

		self.reddit = RedditHandler(self.bot)
		self.pushshift_handler = PushshiftHandler()

	def run(self):
		# Initializes praw reddit instance
		self.start_time = datetime.now()
		# unread_messages = InboxHandler.read_inbox(self.reddit)
		comments = self.pushshift_handler.fetch_comments(params=["q=hello", "limit=10"])
		print(comments[0])


if __name__ == "__main__":
	bot = RedditmendsBot("redditmends_bot")
	bot.run()