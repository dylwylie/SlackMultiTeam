import SlackBot
import config
import threading


class ListenerHandler():

	def __init__(self, ListenerObject, SenderObject):

		self.ListenerObject = ListenerObject
		self.SenderObject = SenderObject

	def callback(self, message, username, image=None):

		self.SenderObject.send_message(username, message, image)

	def run(self):

		self.ListenerObject.run_listener(message_handler=self.SenderObject)

slackBot11 = SlackBot.SlackBotReceiver(config.apiKey1, config.channelKey1)
slackBot22 = SlackBot.SlackBotReceiver(config.apiKey2, config.channelKey2)
slackBot12 = SlackBot.SlackBotSender(config.apiKey1, config.channelKey1)
slackBot21 = SlackBot.SlackBotSender(config.apiKey2, config.channelKey2)

handler1 = ListenerHandler(slackBot11, slackBot21)
handler2 = ListenerHandler(slackBot22, slackBot12)

thread1 = threading.Thread(target=handler1.run)
thread2 = threading.Thread(target=handler2.run)

thread1.start()
thread2.start()

