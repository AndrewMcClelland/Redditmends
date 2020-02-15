import praw
import collections
import inflect
import operator
import json
import numpy as np
from nltk.corpus import words
from difflib import get_close_matches
from datetime import datetime, timedelta
from enum import Enum
from azure.common import AzureConflictHttpError
from azure.common import AzureMissingResourceHttpError

# Local imports
from modules.azure_keyvault_handler import KeyVaultHandler
from modules.azure_text_analytics_handler import TextAnalyticsHandler
from modules.azure_storage_handler import AzureStorageHandler
from modules.pushshift_handler import PushshiftHandler
from modules.reddit_handler import RedditHandler
from modules.praw_handler import PrawHandler
from modules.reddit_inbox_handler import InboxHandler
from modules.marker_api_handler import MarkerAPIHandler
from models.reddit_submission_model import RedditSubmissionModel
from models.reddit_comment_model import RedditCommentModel
from models.recommendation_model import RecommendationModel
from models.submission_date_model import SubmissionDateModel
from models.redditmends_result_model import RedditmendsResultModel

class CommentQueryMethod(Enum):
	PRAW = 1
	PUSHSHIFT = 2

class RedditmendsBot():
	def __init__(self, username):

		# Search related properties
		self.submission_search_params = {"subreddit": "BuyItForLife", "title": "[Request]", "size": "3", "sort": "asc"}
		self.submission_search_fields = ["author", "created_utc", "id", "link_flair_text", "subreddit", "title", "selftext"]
		self.comment_search_fields = ["author", "body", "created_utc", "link_id", "id", "num_comments", "parent_id", "score", "link_flair_text", "subreddit", "subreddit_id", "total_awards_received"]

		# Handler initiation
		self.keyvault_handler = KeyVaultHandler("https://redditmends-kv.vault.azure.net/")
		self.praw = PrawHandler(self.keyvault_handler)
		self.pushshift = PushshiftHandler()
		self.storage_account = AzureStorageHandler(self.keyvault_handler)
		self.text_analytics = TextAnalyticsHandler(self.keyvault_handler)
		# self.marker_api = MarkerAPIHandler(self.keyvault_handler)
		self.inflect = inflect.engine()

		# Load english dictionary to run keywords against later
		json_dict = open('.\\redditmends\\data\\english_alpha_words_dictionary.json')
		json_dict = json_dict.read()
		self.english_dict = json.loads(json_dict)
		self.english_dict["bifl"] = 1

		# Configuration properties

		# Trial and error for similar keywords; theoretically, max similar keywords never exceeds 1
		self.max_similar_keywords = 10
		self.similar_keyword_cutoff = 0.7

		# Flag to determine if we should be writing to Azure Storage table
		self.write_storage_enabled = True

		self.submission_fetch_delta = timedelta(weeks = 1)

	def run(self, search_term, comment_query_method, num_top_recommendations):
		# Initializes praw reddit instance
		start_time = datetime.now()

		# unread_messages = InboxHandler.read_inbox(self.reddit)
		recommendation_dict = collections.defaultdict(dict)
		existing_keywords = self.storage_account.filter_entries(table = "recommendations", filter_string = "query_word eq '{0}' and subreddit eq '{1}'".format(search_term, self.submission_search_params["subreddit"]))

		#TODO If we find a keyword that already exists in the table, we're going to try and append to the existing keyword table entry for 'query_word' and 'subreddit' even if it was for a different query_word and/or subreddit
		#TODO Don't want this because we'll have recommendation/keyword entries that are relevant to different subreddit/query_word combinations
		#TODO Then when we try and do filter_entities(), it won't pick up entries that have commas to delimit query_word/subreddit....
		for existing in existing_keywords.items:
			keyword = existing["PartitionKey"]
			recommendation_dict[keyword]["subreddit"] = [existing["subreddit"]]
			recommendation_dict[keyword]["post_id"] = [existing["post_id"]]
			recommendation_dict[keyword]["comment_id"] = [existing["comment_id"]]
			recommendation_dict[keyword]["query_word"] = [existing["query_word"]]
			recommendation_dict[keyword]["sentiment"] = existing["sentiment"]
			recommendation_dict[keyword]["count"] = existing["count"]

		# If another search occurred with same subreddit and search_term, get the most recent stored submission from that search and only retrieve submissions posted after that date
		try:
			newest_stored_sub_date = self.storage_account.get_entry("mostrecentsubdate", partition_key=self.submission_search_params["subreddit"], row_key=self.submission_search_params["title"])
			newest_stored_sub_date = newest_stored_sub_date["created_utc"]
		# If this search is new, then just set the "after" date query to 0
		except AzureMissingResourceHttpError as error:
			print(error)
			print("The mostrecentsubdate entry with subreddit = '{0}' and title = '{1}' does not exist in the database. Setting newest created_utc to 0...".format(self.submission_search_params["subreddit"], self.submission_search_params["title"]))
			newest_stored_sub_date = 0

		submission_params = [	"subreddit=" + self.submission_search_params["subreddit"],
								"title=" + self.submission_search_params["title"],
								"size=" + self.submission_search_params["size"],
								"sort=" + self.submission_search_params["sort"],
								"title=" + search_term,
								"after=" + str(newest_stored_sub_date),
								"fields=" + ",".join(map(str, self.comment_search_fields))]
		submissions = self.pushshift.fetch_submissions(params=submission_params)

		num_submissions = len(submissions)
		num_comments = 0

		# Setting up top comment score and top comment array that meet that score
		top_comment_score = -1
		top_comments = []

		for sub in submissions:
			# Add submission entry for database
			submission = RedditSubmissionModel()
			submission.parse_submission_data(sub)

			#TODO should I always use PRAW for comments to get most up to date info?
			#TODO Am I getting all the nested comments/replies here?0
			# Get comments for current looped subreddit using selected query method (PRAW [Reddit API] vs Pushshift API)
			if(comment_query_method == CommentQueryMethod.PRAW):
				submission_comments = self.praw.get_submission_comments(submission.id)
			else: # CommentQueryMethod.Pushshift
				submission_comments_params = ["link_id=" + submission.id, "size=10", "fields=" + ",".join(map(str, self.comment_search_fields))]
				submission_comments = self.pushshift.fetch_comments(params=submission_comments_params)

			num_comments += len(submission_comments)

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
			if(self.write_storage_enabled):
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
					# Check if keyword is registered as a trademark
					#TODO do we really need this trademark handler
					# keyword_trademark = self.marker_api.fetch_trademarks(keyword)

					# If it can't be pluralized/singularized, it returns a false - in that case, just make it an empty string which will NOT be in dictionary
					keyword_plural = self.inflect.plural(keyword) if self.inflect.plural(keyword) else ""
					keyword_singular = self.inflect.singular_noun(keyword) if self.inflect.singular_noun(keyword) else ""
					# Ensure it's not just a standard english word
					if((keyword not in self.english_dict) and (keyword_plural not in self.english_dict) and (keyword_singular not in self.english_dict)):
						similar_keywords = get_close_matches(keyword, recommendation_dict, self.max_similar_keywords, self.similar_keyword_cutoff)
						# if(keyword in recommendation_dict):
						if(len(similar_keywords) > 0):
							# Theoretically, this should never be more than 1 similar keyword
							existing_similar_keyword = similar_keywords[0]

							keyword_sentiment = recommendation_dict[existing_similar_keyword]["sentiment"]
							keyword_count = recommendation_dict[existing_similar_keyword]["count"]

							if self.submission_search_params["subreddit"] not in recommendation_dict[existing_similar_keyword]["post_id"]: recommendation_dict[existing_similar_keyword]["post_id"].append(self.submission_search_params["subreddit"])
							if submission.id not in recommendation_dict[existing_similar_keyword]["post_id"]: recommendation_dict[existing_similar_keyword]["post_id"].append(submission.id)
							if comment.id not in recommendation_dict[existing_similar_keyword]["comment_id"]: recommendation_dict[existing_similar_keyword]["comment_id"].append(comment.id)
							if search_term not in recommendation_dict[existing_similar_keyword]["query_word"]: recommendation_dict[existing_similar_keyword]["query_word"].append(search_term)
							recommendation_dict[existing_similar_keyword]["sentiment"] = ((keyword_sentiment * keyword_count) + sentiments["documents"][id_counter]["score"]) / (keyword_count + 1)
							recommendation_dict[existing_similar_keyword]["count"] += 1
						else:
							recommendation_dict[keyword]["subreddit"] = [self.submission_search_params["subreddit"]]
							recommendation_dict[keyword]["post_id"] = [submission.id]
							recommendation_dict[keyword]["comment_id"] = [comment.id]
							recommendation_dict[keyword]["query_word"] = [search_term]
							recommendation_dict[keyword]["sentiment"] = sentiments["documents"][id_counter]["score"]
							recommendation_dict[keyword]["count"] = 1

				id_counter +=1

			# Get largest voting for comments and select all comments that have that vote
			if(len(comment_list) > 0):
				curr_top_comment_score = max(comment.score for comment in comment_list)
				curr_top_comments = list(filter(lambda comment: comment.score == curr_top_comment_score, comment_list))
				if(curr_top_comment_score > top_comment_score):
					top_comments = curr_top_comments
					top_comment_score = curr_top_comment_score
				elif(curr_top_comment_score == top_comment_score):
					top_comments.append(curr_top_comments)

			# Insert list of comments into storage table
			if(self.write_storage_enabled):
				try:
					self.storage_account.insert_comment_entry(comment_list)
				except TypeError as error:
					print(error)
					print(f"The comment object is formatted incorrectly and was not inserted. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")
				except AzureConflictHttpError as error:
					print(error)
					print(f"The comment entry with id =  %s already exists in the database. Continuing..." % comment.id)

		#TODO add amazon or similar link to these products?
		# Create list of recommendations
		recommendation_list = []
		# ITerating through list of dict because we are deleting a dictionary entry as we iterate over it which would cause runtime error if we were simply iterating over dict
		for keyword in list(recommendation_dict):
			similar_keywords = get_close_matches(keyword, recommendation_dict, self.max_similar_keywords, self.similar_keyword_cutoff)
			if(len(similar_keywords) > 1): # > 1 since keyword already exists in dict so it will always match with itself
				curr_keyword = recommendation_dict[keyword]
				existing_keyword = similar_keywords[1] # 1 since keyword already exists in dict so it will be first one it matches with

				recommendation_dict[existing_keyword]["sentiment"] = ((recommendation_dict[existing_keyword]["sentiment"] * recommendation_dict[existing_keyword]["count"]) + (curr_keyword["sentiment"] * curr_keyword["count"])) / (recommendation_dict[existing_keyword]["count"] + curr_keyword["count"])
				if self.submission_search_params["subreddit"] not in recommendation_dict[existing_keyword]["query_word"] : recommendation_dict[existing_keyword]["query_word"].append(self.submission_search_params["subreddit"])
				if curr_keyword["query_word"] not in recommendation_dict[existing_keyword]["query_word"] : recommendation_dict[existing_keyword]["query_word"].append(curr_keyword["query_word"])
				if curr_keyword["post_id"] not in recommendation_dict[existing_keyword]["post_id"]: recommendation_dict[existing_keyword]["post_id"].append(curr_keyword["post_id"])
				if curr_keyword["comment_id"] not in recommendation_dict[existing_keyword]["comment_id"]: recommendation_dict[existing_keyword]["comment_id"].append(curr_keyword["comment_id"])
				recommendation_dict[existing_keyword]["count"] += curr_keyword["count"]

				# Remove the keyword so we don't accidentally match with it furter down the line (causing a cyclical similarity)
				del recommendation_dict[keyword]

			else:
				curr_recom = RecommendationModel(keyword)
				curr_recom.add_subreddit(recommendation_dict[keyword]["subreddit"])
				curr_recom.add_sentiment(recommendation_dict[keyword]["sentiment"])
				curr_recom.add_query_keyword(recommendation_dict[keyword]["query_word"])
				curr_recom.add_post_id(recommendation_dict[keyword]["post_id"])
				curr_recom.add_comment_id(recommendation_dict[keyword]["comment_id"])
				curr_recom.add_count(recommendation_dict[keyword]["count"])

				recommendation_list.append(curr_recom)

		# Get largest count for keywords and select all keywords that have that count
		recommendation_list.sort(key=operator.attrgetter("count"), reverse=True)
		top_keyword_counts = list(recommendation.count for recommendation in recommendation_list[:num_top_recommendations])
		top_keywords = []
		last_count = -1
		for count in top_keyword_counts:
			if(count != last_count):
				top_keywords += filter(lambda x: x.count == count, recommendation_list)
				last_count = count
		num_unique_keywords = len(recommendation_list)

		# Insert recommendations into storage table
		if(self.write_storage_enabled):
			try:
				self.storage_account.insert_recommendation_entry(recommendation_list)
			except TypeError as error:
				print(error)
				print(f"The recommendation object is formatted incorrectly and was not inserted. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")

		# Update 'mostrecentsubdate' entry for current subreddit/query search (submissions are sorted in ascending order so the last one hit will be newest, so update here)
		if(self.write_storage_enabled):
			newest_sub_date = SubmissionDateModel(self.submission_search_params["subreddit"], search_term, submission.created_utc, submission.id)
			try:
				self.storage_account.insert_sub_date_entry(newest_sub_date)
			except TypeError as error:
				print(error)
				print(f"The most recent subdate object is formatted incorrectly and was not inserted. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")

		# Get runtime
		runtime = datetime.now() - start_time

		# Create result object with relevant data
		self.result = RedditmendsResultModel()
		self.result.parse_result_data(search_term, runtime, num_submissions, num_comments, num_unique_keywords, top_comments, top_comment_score, top_keywords, top_keyword_counts[0])

if __name__ == "__main__":
	bot = RedditmendsBot("redditmends_bot")
	#TODO: allow entry of parameters with spaces
	bot.run(search_term = "blanket", comment_query_method = CommentQueryMethod.PRAW, num_top_recommendations = 5)
	print(bot.result)