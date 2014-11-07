import zulip
import os
import random
from random import randrange

# create a zulip client/bot
client = zulip.Client(config_file = '.config', verbose = True)

# subscribe to bot-test
client.add_subscriptions([{u'stream_id': 26025, u'description': u'', u'name': u'bot-test', u'invite_only': False}])

class PotatoHandler(object):
	def __init__(self, client):
		self.client = client
		self.surprises = [':fireworks:', ':tada:', ':confetti_ball:', ':sparkler:']
		self.count = randrange(2, 5)

	def __call__(self, event):
		# if the event is a message
		if event['type'] == 'message':
			self.handle_message(event['message'])

	def send_stream_message(self, to, subject, content):
		self.client.send_message({
		"type" : 'stream',
		"to" : to,
		"subject" : subject,
		"content" : content
		})

	def send_pm(self, to, content):
		self.client.send_message({
		"type" : 'private',
		"to" : to,
		"content" : content
		})

	def handle_message(self, message):
		# if the message is from the bot itself, do nothing
		if message['sender_email'] == self.client.email:
		 	return None

		# otherwise get message information
		content = message['content']
		sender  = message['sender_email']
		subject = message['subject']

		# if it's a private message
		if message['type'] == 'private':
			if self.count > 0:
				content = ':cookie:'
				self.count -= 1
			else:
				content = random.choice(self.surprises)
				self.count = randrange(2, 5)

			self.send_pm(sender, content)

		# else if it's a stream message
		elif message['type'] == 'stream':
			if content.startswith( '@**Hot Potato**' ):
				if self.count > 0:
					content = ':cookie:'
					self.count -= 1
				else:
					content = random.choice(self.surprises)
					self.count = randrange(2, 5)

				self.send_stream_message( 'bot-test', subject, content )

client.call_on_each_event(PotatoHandler(client))

