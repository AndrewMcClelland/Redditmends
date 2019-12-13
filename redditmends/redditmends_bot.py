import praw
from azure.common import AzureConflictHttpError
from datetime import datetime, timedelta

from modules.pushshift_handler import PushshiftHandler
from modules.reddit_handler import RedditHandler
from modules.inbox_handler import InboxHandler
from modules.azure_storage_handler import AzureStorageHandler
from accounts.reddit_account_info import accounts
from models.reddit_submission_model import RedditSubmissionModel
from models.reddit_comment_model import RedditCommentModel

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

	def run(self, submission_params):
		# Initializes praw reddit instance
		self.start_time = datetime.now()
		# unread_messages = InboxHandler.read_inbox(self.reddit)

		#TODO: fix queries for submissions (flair, etc.) --> make sure it's matching up
		#TODO: only fetch submissions that we haven't seen yet
		submissions = self.pushshift_handler.fetch_submissions(params=submission_params)

		for sub in submissions:
			# Add submission entry for database
			submission = RedditSubmissionModel()
			submission.parse_submission_data(sub)

			try:
				self.storage_account.insert_submission_entry(submission)
			except AzureConflictHttpError as error:
				print(error)
				print(f"The submission entry with id =  %s already exists in the database. Continuing..." % submission.id)


			# Add each comment for current submission into database
			submission_comments = self.pushshift_handler.fetch_comments(params=["link_id=" + submission.id])

			for com in submission_comments:
				comment = RedditCommentModel()
				comment.parse_comment_data(com)

				try:
					self.storage_account.insert_comment_entry(comment)
				except AzureConflictHttpError as error:
					print(error)
					print(f"The comment entry with id =  %s already exists in the database. Continuing..." % comment.id)



if __name__ == "__main__":
	bot = RedditmendsBot("redditmends_bot")
	#TODO: allow entry of parameters with spaces
	bot.run(["subreddit=BuyItForLife", "title=[Request]", "num_comments=>1", "limit=10"]) # use ids here, seems to work for submissions - https://www.reddit.com/r/pushshift/comments/b3gvye/query_for_a_given_post_id/