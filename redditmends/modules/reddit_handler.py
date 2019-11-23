import praw

class RedditHandler():

	def __init__(self, credentials):
		self.credentials = credentials
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
