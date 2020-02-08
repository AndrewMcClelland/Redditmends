import praw
import collections

from models.reddit_comment_model import RedditCommentModel

class PrawHandler():

	def __init__(self, kv):


		self.credentials = {
							"appKey" : kv.get_keyvault_secret("reddit-appKey"),
							"secret" : kv.get_keyvault_secret("reddit-secret"),
							"username" : kv.get_keyvault_secret("reddit-username"),
							"password" : kv.get_keyvault_secret("reddit-password"),
							"userAgent" : kv.get_keyvault_secret("reddit-userAgent")
							}

		self.reddit = self.connect()

	def connect(self):
		try:
			reddit = praw.Reddit(client_id = self.credentials["appKey"],
										client_secret = self.credentials["secret"],
										password = self.credentials["password"],
										user_agent = self.credentials["userAgent"],
										username = self.credentials["username"])
			return reddit
		except:
			print("Error connecting to Reddit")
			raise

	def get_submission_comments(self, submission_id):
		result = []
		comments = self.reddit.submission(id = submission_id).comments
		for comment in comments:
			comment_dict = collections.defaultdict(dict)
			comment_dict["author"] = comment.author.name if (comment.author != None and comment.author.name != None) else None
			comment_dict["body"] = comment.body if comment.body != None else None
			comment_dict["created_utc"] = comment.created_utc if comment.created_utc != None else None
			comment_dict["link_id"] = comment.link_id if comment.link_id != None else None
			comment_dict["id"] = comment.id if comment.id != None else None
			comment_dict["parent_id"] = comment.parent_id if comment.parent_id != None else None
			comment_dict["score"] = comment.score if comment.score != None else None
			comment_dict["subreddit"] = comment.subreddit.display_name if (comment.subreddit != None and comment.subreddit.display_name != None) else None
			comment_dict["subreddit_id"] = comment.subreddit_id if comment.subreddit_id != None else None
			comment_dict["total_awards_received"] = comment.total_awards_received if comment.total_awards_received != None else None

			result.append(comment_dict)

		return result


	def get_inbox_all(self):
		messages = self.reddit.inbox.all(limit=None)
		ret = []

		for message in messages:
			ret.append(message)

		# Sort by ascending date
		return ret.reverse()

	def get_inbox_unread(self):
		unreads = self.reddit.inbox.unread(limit=None)
		messages = []

		for unread in unreads:
			messages.append(unread)

		# Sort by ascending date
		return messages.reverse()
