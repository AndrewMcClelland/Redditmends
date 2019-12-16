import os, uuid
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

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

			# Flatten list of keywords into comma separated string
			comment.keywords = ','.join(map(str, entry.keywords))

			self.table_service.insert_entity('comments', comment)

	def insert_recommendation_entry(self, entry):
		recommendation = Entity()

		recommendation.PartitionKey = entry.subreddit
		recommendation.RowKey = entry.id
		recommendation.flair = entry.flair
		recommendation.title = entry.title

		self.table_service.insert_entity('recommendations', recommendation)