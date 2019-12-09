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
		task = Entity()
		task.PartitionKey = entry.subreddit
		task.RowKey = entry.id
		task.author = entry.author
		task.post_date = entry.post_date
		task.flair = entry.flair
		task.title = entry.title
		self.table_service.insert_entity('submissions', task)