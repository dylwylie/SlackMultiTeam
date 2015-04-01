from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
import sys

class IRCBot(irc.IRCClient):

	def __init__(self,nickname):

		self.nickname = nickname

	def connectionMade(self):

		irc.IRCClient.connectionMade(self)
		print('Connection Made!')

	def connectionLost(self, reason):

		irc.IRCClient.connectionLost(self, reason)
		print('Connection Lost! ' + str(reason))

	def command_ping(self, respt):
		return 'Pong.'

	def signedOn(self):

		print('Joining Channel')
		self.join(self.factory.channel)

	def joined(self, channel):

		print("Joined: " + str(channel))

	def parseIRC(self,text):
		print(text)
		splitMessage = text.split(' ')
		parsed = dict()

		try:
			parsed['prefix'] = splitMessage[0]
			parsed['command'] = splitMessage[1]
			parsed['parameters'] = splitMessage[2]
			parsed['trailing'] = ' '.join(splitMessage[3:])
			parsed['username'] = ((parsed['prefix'][1:]).split('!'))[0]

			if(parsed['command'] == 'PRIVMSG'):

				parsed['message'] = parsed['trailing'][1:]

		except IndexError:
			pass

		return parsed

	def lineReceived(self,line):

		parsedIRC = self.parseIRC(line)

		try:
			if (parsedIRC['command'] == 'PRIVMSG'):
				self.factory.messageHandler(parsedIRC['message'],parsedIRC['username'])

		except IndexError:
			pass	

		irc.IRCClient.lineReceived(self,line)

	def sendMessage(self,username,message):

		messageToSend = username + ': ' + message
		irc.IRCClient.msg(self,self.factory.channel,str(messageToSend))


class BotFactory(protocol.ClientFactory):

	def __init__(self,nickname,channel,messageHandler):

		self.nickname = nickname
		self.channel = channel
		self.messageHandler = messageHandler

	def buildProtocol(self,addr):

		self.ircBot = IRCBot(self.nickname)
		self.ircBot.factory = self
		return self.ircBot

	def clientConnnectionLost(self,connector,reason):

		print('Lost connection: ' + str(reason))
		print('Reconnecting...')
		connector.connect()
		print('Connected!')

	def clientConnectionFailed(self,connector,reason):

		print("Can't connect :( : " + str(reason))
		reactor.stop()

	def sendMessage(self,username,text):

		self.ircBot.sendMessage(username,text)

class IRCBotRunner():

	def __init__(self,nickname,channel):

		self.nickname = nickname
		self.channel = channel

	def runListener(self,messageHandler):

		self.factory = BotFactory(self.nickname,self.channel,messageHandler)
		reactor.connectTCP("irc.freenode.net",6667,self.factory)
		print("Connected..... ")
		reactor.run()
		print("Done!")

	def sendMessage(self,username,text,icon_url=None):

		self.factory.sendMessage(username,text)



	#slackBot = SlackBot('test')
	#slackBotListener = SlackBotListener()
	#thread = threading.Thread(target = slackBotListener.run)

	#slackBot.sendMessage('test','SlackBot','text!')
	#slackBot.listChannels()
