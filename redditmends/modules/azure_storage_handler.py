import os, uuid
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

from accounts.azure_storage_account_info import storage_account

class AzureStorageHandler():
	def __init__(self):
		try:
			self.table_service = TableService(account_name=storage_account["account_name"], account_key=storage_account["account_key"])
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

		self.table_service.insert_entity('submissions', submission)

	def insert_comment_entry(self, entry):
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

		self.table_service.insert_entity('comments', comment)

	def insert_recommendation_entry(self, entry):
		recommendation = Entity()

		recommendation.PartitionKey = entry.subreddit
		recommendation.RowKey = entry.id
		recommendation.flair = entry.flair
		recommendation.title = entry.title

		self.table_service.insert_entity('recommendations', recommendation)