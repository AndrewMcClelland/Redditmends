import praw
import collections
from datetime import datetime, timedelta
from azure.common import AzureConflictHttpError
from azure.common import AzureMissingResourceHttpError

# Local imports
from modules.azure_keyvault_handler import KeyVaultHandler
from modules.azure_text_analytics_handler import TextAnalyticsHandler
from modules.azure_storage_handler import AzureStorageHandler
from modules.pushshift_handler import PushshiftHandler
from modules.reddit_praw_handler import RedditHandler
from modules.reddit_inbox_handler import InboxHandler
from models.reddit_submission_model import RedditSubmissionModel
from models.reddit_comment_model import RedditCommentModel
from models.recommendation_model import RecommendationModel
from models.submission_date_model import SubmissionDateModel

class RedditmendsBot():
	def __init__(self, username):

		self.submission_search_params = {"subreddit": "BuyItForLife", "title": "[Request]", "size": "3", "sort": "asc"}
		self.submission_search_fields = ["author", "created_utc", "id", "link_flair_text", "subreddit", "title", "selftext"]
		self.comment_search_fields = ["author", "body", "created_utc", "link_id", "id", "num_comments", "parent_id", "score", "link_flair_text", "subreddit", "subreddit_id", "total_awards_received"]

		self.keyvault_handler = KeyVaultHandler("https://redditmends-kv.vault.azure.net/")
		self.reddit = RedditHandler(self.keyvault_handler)
		self.pushshift = PushshiftHandler()
		self.storage_account = AzureStorageHandler(self.keyvault_handler)
		self.text_analytics = TextAnalyticsHandler(self.keyvault_handler)

	def run(self, search_term):
		# Initializes praw reddit instance
		self.start_time = datetime.now()
		# unread_messages = InboxHandler.read_inbox(self.reddit)

		recommendation_dict = collections.defaultdict(dict)

		# If another search occurred with same subreddit and search_term, get the most recent stored submission from that search and only retrieve submissions posted after that date
		try:
			newest_stored_sub_date = self.storage_account.get_entry("mostrecentsubdate", partition_key=self.submission_search_params["subreddit"], row_key=self.submission_search_params["title"])
			newest_stored_sub_date = newest_stored_sub_date["created_utc"]
		# If this search is new, then just set the "after" date query to 0
		except AzureMissingResourceHttpError as error:
			print(error)
			print("The mostrecentsubdate entry with subreddit =  '{0}' and title = '{1}' does not exist in the database. Setting newest created_utc to 0...".format(self.submission_search_params["subreddit"], self.submission_search_params["title"]))
			newest_stored_sub_date = 0

		submission_params = ["subreddit=" + self.submission_search_params["subreddit"], "title=" + self.submission_search_params["title"], "size=" + self.submission_search_params["size"], "sort=" + self.submission_search_params["sort"], "title=" + search_term, "after=" + str(newest_stored_sub_date), "fields=" + ",".join(map(str, self.comment_search_fields))]
		submissions = self.pushshift.fetch_submissions(params=submission_params)

		for sub in submissions:
			# Add submission entry for database
			submission = RedditSubmissionModel()
			submission.parse_submission_data(sub)

			# Add each comment for current submission into database
			submission_comments_params = ["link_id=" + submission.id, "size=10", "fields=" + ",".join(map(str, self.comment_search_fields))]
			submission_comments = self.pushshift.fetch_comments(params=submission_comments_params)

			# Get all the comment body values and store as a list
			texts = list(map(lambda comment: comment["body"], submission_comments))

			# Insert submission title at index 0 and submission body at index 1
			texts.insert(0, submission.title)
			sub_body_is_empty = submission.body == ""
			if not sub_body_is_empty:
				texts.insert(1, submission.body)

			# Get keywords/sentiments for submission title (id = 0) and submission body (id = 1), and all comments
			keywords = self.text_analytics.get_key_phrases(texts)
			sentiments = self.text_analytics.get_sentiment(texts)

			# Convert keywords to lower case to avoid duplicates due to case insensitivity of table storage
			for entry in keywords["documents"]:
				word_count = 0
				for word in entry["keyPhrases"]:
					keywords["documents"][int(entry["id"])]["keyPhrases"][word_count] = word.lower()
					word_count += 1

			# Insert submission title and body keywords into submission object
			submission.add_title_keywords(keywords["documents"][0]["keyPhrases"])
			submission.add_title_sentiment(sentiments["documents"][0]["score"])
			if not sub_body_is_empty:
				submission.add_body_keywords(keywords["documents"][1]["keyPhrases"])
				submission.add_body_sentiment(sentiments["documents"][1]["score"])

			# Insert submission into storage table
			try:
				self.storage_account.insert_submission_entry(submission)
			except TypeError as error:
				print(error)
				print(f"The submission object is formatted incorrectly and was not inserted. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")
			except AzureConflictHttpError as error:
				print(error)
				print(f"The submission entry with id =  %s already exists in the database. Continuing..." % submission.id)

			# List of RedditCommentModel() objects
			comment_list = []
			id_counter = 1 if sub_body_is_empty else 2 	# submission title keywords will be index 0 and submission comment keywords will be index 1 (set counter to 1 if no body)
			for com in submission_comments:
				# Handle comments
				comment = RedditCommentModel()
				comment.parse_comment_data(com)
				comment.add_keywords(keywords["documents"][id_counter]["keyPhrases"])
				comment.add_sentiment(sentiments["documents"][id_counter]["score"])

				comment_list.append(comment)

				# Handle recommendations
				for keyword in keywords["documents"][id_counter]["keyPhrases"]:
					if(keyword in recommendation_dict):
						keyword_sentiment = recommendation_dict[keyword]["sentiment"]
						keyword_count = recommendation_dict[keyword]["count"]
						recommendation_dict[keyword]["post_id"].append(submission.id)
						recommendation_dict[keyword]["comment_id"].append(comment.id)
						recommendation_dict[keyword]["query_word"].append(search_term)
						recommendation_dict[keyword]["sentiment"] = ((keyword_sentiment * keyword_count) + sentiments["documents"][id_counter]["score"]) / (keyword_count + 1)
						recommendation_dict[keyword]["count"] += 1
					else:
						recommendation_dict[keyword]["post_id"] = [submission.id]
						recommendation_dict[keyword]["comment_id"] = [comment.id]
						recommendation_dict[keyword]["query_word"] = [search_term]
						recommendation_dict[keyword]["sentiment"] = sentiments["documents"][id_counter]["score"]
						recommendation_dict[keyword]["count"] = 1

				id_counter +=1

			# Insert list of comments into storage table
			try:
				self.storage_account.insert_comment_entry(comment_list)
			except TypeError as error:
				print(error)
				print(f"The comment object is formatted incorrectly and was not inserted. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")
			except AzureConflictHttpError as error:
				print(error)
				print(f"The comment entry with id =  %s already exists in the database. Continuing..." % comment.id)

		# Create list of recommendations
		recommendation_list = []
		for keyword in recommendation_dict:
			curr_recom = RecommendationModel(keyword)
			curr_recom.add_sentiment(recommendation_dict[keyword]["sentiment"])
			curr_recom.add_query_keyword(recommendation_dict[keyword]["query_word"])
			curr_recom.add_post_id(recommendation_dict[keyword]["post_id"])
			curr_recom.add_comment_id(recommendation_dict[keyword]["comment_id"])
			curr_recom.add_count(recommendation_dict[keyword]["count"])

			recommendation_list.append(curr_recom)

		# Insert recommendations into storage table
		try:
			self.storage_account.insert_recommendation_entry(recommendation_list)
		except TypeError as error:
			print(error)
			print(f"The recommendation object is formatted incorrectly and was not inserted. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")

		# Update 'mostrecentsubdate' entry for current subreddit/query search
		newest_sub_date = SubmissionDateModel(self.submission_search_params["subreddit"], self.submission_search_params["title"], submission.created_utc, submission.id)
		try:
			self.storage_account.insert_sub_date_entry(newest_sub_date)
		except TypeError as error:
			print(error)
			print(f"The mostrecentsubdate object is formatted incorrectly and was not inserted. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")

if __name__ == "__main__":
	bot = RedditmendsBot("redditmends_bot")
	#TODO: allow entry of parameters with spaces
	# bot.run(["subreddit=BuyItForLife", "title=[Request]", "num_comments=>1", "limit=10"]) # use ids here, seems to work for submissions - https://www.reddit.com/r/pushshift/comments/b3gvye/query_for_a_given_post_id/
	bot.run(search_term = "blanket")
	# bot.run(["ids=duv1bf"])