import zulip
import requests
import os
import random
from random import randrange

# create a zulip client/bot
client = zulip.Client(config_file = '.config', verbose = True)

# call Zulip API to get all streams
def get_zulip_streams():
	response = requests.get(
		'https://api.zulip.com/v1/streams',
		auth=requests.auth.HTTPBasicAuth(os.environ['ZULIP_USERNAME'], os.environ['ZULIP_API_KEY'])
	)

	if response.status_code == 200:
		return response.json()['streams']
	elif response.status_code == 401:
		raise RuntimeError('check authentication')
	else:
		raise RuntimeError('failed to get streams\n(%s)' % response)

def subscribe_to_streams():
	streams = [{'name' : stream['name']} for stream in get_zulip_streams()]
	client.add_subscriptions(streams)

# subscribe to all streams
subscribe_to_streams()

# class to handle events and send messages
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

