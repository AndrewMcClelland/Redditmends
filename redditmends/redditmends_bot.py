import praw
from azure.common import AzureConflictHttpError
from datetime import datetime, timedelta
import collections

from modules.azure_keyvault_handler import KeyVaultHandler
from modules.azure_text_analytics_handler import TextAnalyticsHandler
from modules.azure_storage_handler import AzureStorageHandler
from modules.pushshift_handler import PushshiftHandler
from modules.reddit_praw_handler import RedditHandler
from modules.reddit_inbox_handler import InboxHandler
from models.reddit_submission_model import RedditSubmissionModel
from models.reddit_comment_model import RedditCommentModel
from models.recommendation_model import RecommendationModel

class RedditmendsBot():
	def __init__(self, username):

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

		#TODO: fix queries for submissions (flair, etc.) --> make sure it's matching up
		#TODO: only fetch submissions that we haven't seen yet
		submission_params = ["subreddit=BuyItForLife", "title=[Request]", "size=500", "title=" + search_term]
		submissions = self.pushshift.fetch_submissions(params=submission_params)

		for sub in submissions:
			# Add submission entry for database
			submission = RedditSubmissionModel()
			submission.parse_submission_data(sub)

			# Add each comment for current submission into database
			submission_comments = self.pushshift.fetch_comments(params=["link_id=" + submission.id, "size=500"])

			# Get all the comment body values and store as a list
			texts = list(map(lambda comment: comment["body"], submission_comments))

			# Insert submission title at index 0 and submission body at index 1
			texts.insert(0, submission.title)
			texts.insert(1, submission.body)

			# Get keywords/sentiments for submission title (id = 0) and submission body (id = 1), and all comments
			keywords = self.text_analytics.get_key_phrases(texts)
			sentiments = self.text_analytics.get_sentiment(texts)

			# Insert submission title and body keywords into submission object
			submission.add_title_keywords(keywords["documents"][0]["keyPhrases"])
			submission.add_body_keywords(keywords["documents"][1]["keyPhrases"])
			submission.add_title_sentiment(sentiments["documents"][0]["score"])
			submission.add_body_sentiment(sentiments["documents"][0]["score"])

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
			id_counter = 2 	# submission title keywords will be index 0 and submission comment keywords will be index 1
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
			keyword_exists = self.storage_account.get_entry("recommendations", keyword, keyword)
			if(keyword_exists != null):	# keyword already exists in storage, so update it's values
				# UPDATE ENTITY INSTEAD???
				self.storage_account.delete_entry("recommendations", keyword, keyword)

			else: # keyword doesn't exist
				curr_recom.add_sentiment(keyword["sentiment"])
				curr_recom.add_query_keyword(keyword["query_word"])
				curr_recom.add_post_id(keyword["post_id"])
				curr_recom.add_count(keyword["count"])

			recommendation_list.append(curr_recom)

		# Insert recommendations into storage table
		try:
			self.storage_account.insert_recommendation_entry(recommendation_list)
		except TypeError as error:
			print(error)
			print(f"The recommendation object is formatted incorrectly and was not inserted. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")
		except AzureConflictHttpError as error:
			print(error)
			print(f"The recommendation entry with id =  %s already exists in the database. Continuing..." % comment.id)

if __name__ == "__main__":
	bot = RedditmendsBot("redditmends_bot")
	#TODO: allow entry of parameters with spaces
	# bot.run(["subreddit=BuyItForLife", "title=[Request]", "num_comments=>1", "limit=10"]) # use ids here, seems to work for submissions - https://www.reddit.com/r/pushshift/comments/b3gvye/query_for_a_given_post_id/
	bot.run(search_term = "blanket")
	# bot.run(["ids=duv1bf"])