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
		submission.post_date = entry.post_date
		submission.flair = entry.flair
		submission.title = entry.title

		# Flatten list of keywords into comma separated string
		submission.title_keywords = ','.join(map(str, entry.title_keywords))
		submission.body_keywords = ','.join(map(str, entry.body_keywords))

		submission.title_sentiment = entry.title_sentiment
		submission.body_sentiment = entry.body_sentiment

		self.table_service.insert_entity('submissions', submission)

	def insert_comment_entry(self, entries):

		for entry in entries:
			comment = Entity()

			comment.PartitionKey = entry.link_id
			comment.RowKey = entry.id
			comment.author = entry.author
			comment.body = entry.body
			comment.num_comments = entry.num_comments
			comment.post_date = entry.post_date
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
				print(f"The recommendation entry with keyword =  %s already exists in the database. Updating..." % recommendation.PartitionKey)

				# Update existing entry with duplicate entry attributes
				existing_recommendation = AzureStorageHandler.get_entry(self, "recommendations", recommendation.PartitionKey, recommendation.RowKey)
				recommendation.post_id += "," + existing_recommendation["post_id"]
				recommendation.comment_id += "," + existing_recommendation["comment_id"]
				recommendation.query_word += "," + existing_recommendation["query_word"]
				recommendation.sentiment = ((float(existing_recommendation["sentiment"]) * int(existing_recommendation["count"])) + (recommendation.sentiment * recommendation.count)) / (int(existing_recommendation["count"]) + recommendation.count)
				recommendation.count = int(recommendation.count) + int(existing_recommendation["count"])

				self.table_service.update_entity('recommendations', recommendation)

	def get_entry(self, table, partition_key, row_key):
		return self.table_service.get_entity('recommendations', partition_key, row_key)

	def delete_entry(self, table, partition_key, row_key):
		return self.table_service.delete_entity('recommendations', partition_key, row_key)