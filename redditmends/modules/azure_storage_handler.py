import os, uuid
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from azure.common import AzureConflictHttpError

class AzureStorageHandler():
	def __init__(self, kv):
		try:
			self.table_service = TableService(account_name=kv.get_keyvault_secret("storageAccount-name"), account_key=kv.get_keyvault_secret("storageAccount-key"))
			# Quick start code goes here
		except Exception as ex:
			print('Exception:')
			print(ex)

	def insert_submission_entry(self, entry):
		submission = Entity()

		submission.PartitionKey = entry.subreddit
		submission.RowKey = entry.id
		submission.author = entry.author
		submission.created_utc = entry.created_utc
		submission.flair = entry.flair
		submission.title = entry.title

		# Flatten list of keywords into comma separated string
		submission.title_keywords = ','.join(map(str, entry.title_keywords))
		submission.title_sentiment = entry.title_sentiment
		try:
			submission.body_keywords = ','.join(map(str, entry.body_keywords))
			submission.body_sentiment = entry.body_sentiment
		except AttributeError:
			submission.body_keywords = ""
			submission.body_sentiment = ""

		self.table_service.insert_entity('submissions', submission)

	def insert_comment_entry(self, entries):

		for entry in entries:
			comment = Entity()

			comment.PartitionKey = entry.link_id
			comment.RowKey = entry.id
			comment.author = entry.author
			comment.body = entry.body
			comment.num_comments = entry.num_comments
			comment.created_utc = entry.created_utc
			comment.parent_id = entry.parent_id
			comment.score = entry.score
			comment.flair = entry.flair
			comment.subreddit = entry.subreddit
			comment.subreddit_id = entry.subreddit_id
			comment.total_awards_received = entry.total_awards_received
			comment.sentiment = entry.sentiment

			# Flatten list of keywords into comma separated string
			comment.keywords = ','.join(map(str, entry.keywords))

			self.table_service.insert_entity('comments', comment)

	def insert_recommendation_entry(self, entries):

		for entry in entries:
			recommendation = Entity()

			recommendation.PartitionKey = entry.keyword
			recommendation.RowKey = entry.keyword
			recommendation.post_id = ','.join(map(str, entry.post_id))
			recommendation.comment_id = ','.join(map(str, entry.comment_id))
			recommendation.query_word = ','.join(map(str, entry.query_word))
			recommendation.sentiment = entry.sentiment
			recommendation.count = entry.count

			try:
				self.table_service.insert_entity('recommendations', recommendation)
			except AzureConflictHttpError as error:
				print(error)
				print("The recommendation entry with keyword =  '{0}' already exists in the database. Updating...".format(recommendation.PartitionKey))

				# Update existing entry with duplicate entry attributes
				existing_recommendation = AzureStorageHandler.get_entry(self, "recommendations", recommendation.PartitionKey, recommendation.RowKey)
				recommendation.post_id += "," + existing_recommendation["post_id"]
				recommendation.comment_id += "," + existing_recommendation["comment_id"]
				recommendation.query_word += "," + existing_recommendation["query_word"]
				recommendation.sentiment = ((float(existing_recommendation["sentiment"]) * int(existing_recommendation["count"])) + (recommendation.sentiment * recommendation.count)) / (int(existing_recommendation["count"]) + recommendation.count)
				recommendation.count = int(recommendation.count) + int(existing_recommendation["count"])

				self.table_service.update_entity('recommendations', recommendation)

	def insert_sub_date_entry(self, entry):
		sub_date = Entity()

		sub_date.PartitionKey = entry.subreddit
		sub_date.RowKey = entry.title
		sub_date.created_utc = entry.created_utc
		sub_date.post_id = entry.post_id

		try:
			self.table_service.insert_or_replace_entity('mostrecentsubdate', sub_date)
		except TypeError as error:
			print(error)
			print(f"The mostrecentsubdate object is formatted incorrectly and was not updated. One of the parameters is not an int, str, bool or datetime, or defined custom EntityProperty. Continuing...")

	def get_entry(self, table, partition_key, row_key):
		return self.table_service.get_entity(table, partition_key, row_key)

	def update_entry(self, table, entity):
		return self.table_service.update_entity(table, entity)

	def delete_entry(self, table, partition_key, row_key):
		return self.table_service.delete_entity(table, partition_key, row_key)