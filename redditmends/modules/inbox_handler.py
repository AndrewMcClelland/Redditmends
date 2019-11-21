class InboxHandler():

	@staticmethod
	def read_inbox(reddit):
		try:
			unread_messages = reddit.get_inbox_unread()
		except:
			unread_messages = []
			raise

		message_count = 0
		for message in unread_messages:
			message_count += 1
			username = str(message.author).lower()
			subject = str(message.subject).lower()
			body = str(message.body).lower()

		print("Unread messages read = ", message_count)