import SlackBot,threading

apiKey1 = 'FIRST SLACK API KEY'
apiKey2 = 'SECOND SLACK API KEY'

channelKey1 = 'CHANNEL IN FIRST SLACK'
channelKey2 = 'CHANNEL IN SECOND SLACK'

class ListenerHandler():

	def __init__(self,ListenerObject,SenderObject):

		self.ListenerObject = ListenerObject
		self.SenderObject = SenderObject

	def callback(self,message,username,image=None):

		self.SenderObject.sendMessage(username,message,image)

	def run(self):

		self.ListenerObject.runListener(messageHandler=self.callback)

slackBot11 = SlackBot.SlackBot(apiKey1,channelKey1)
slackBot12 = SlackBot.SlackBot(apiKey1,channelKey1)
slackBot21 = SlackBot.SlackBot(apiKey2,channelKey2)
slackBot22 = SlackBot.SlackBot(apiKey2,channelKey2)

handler1 = ListenerHandler(slackBot11,slackBot21)
handler2 = ListenerHandler(slackBot22,slackBot12)

thread1 = threading.Thread(target=handler1.run)
thread2 = threading.Thread(target=handler2.run)

thread1.start()
thread2.start()



#handler2.run()

