import sys,requests,json,threading,time

class SlackBot():

	URL = 'https://slack.com/api/'

	def __init__(self,token,channel):

		self.token = 'token=' +  token
		self.channel = channel

	def call(self,method,arguments=None):

		URL = self.URL + method + '?' + self.token

		if(arguments):

			for argument in arguments:

				URL+= '&' + argument

		return requests.get(URL)

	def sendMessage(self,username,text,icon_url=None):

		channel = self.channel 
		arguments = ['channel='+channel, 'username='+username, 'text='+text]

		if(icon_url):

			arguments.append('icon_url='+icon_url)

		r = self.call('chat.postMessage',arguments)

	def joinChannel(self,channel):

		arguments = ['name='+channel]
		r = self.call('channels.join',arguments)
	def listChannels(self):

		r = self.call('channels.list')

	def getUser(self,id):

		arguments = ['user='+id]
		r = self.call('users.info',arguments)
		return(r.json()[unicode('user')])

	# !BLOCKING! #
	def runListener(self,messageHandler,timeOfLastMessage=str(time.time())):

		arguments = ['channel='+self.channel,'inclusive=0']
		arguments.append('oldest='+timeOfLastMessage)

		r = self.call('channels.history',arguments)

		try:
			response = r.json()
			messages = response[unicode('messages')]

			if(messages): #Has we some messages to deal with?

				times = []

				for message in messages:
					messageTime = message[unicode('ts')]

					if(messageTime != timeOfLastMessage):

						text = message[unicode('text')]
						user_id = message[unicode('user')]
						user_profile = self.getUser(user_id)
						username = user_profile[unicode('name')]
						user_image = user_profile[unicode('profile')][unicode('image_48')]

						messageHandler(text,username,user_image)
						#handle our messages
						

					#Take the timestamp of each message
					times.append(messageTime) 

				#Get the timestamp of the latest one
				timeOfLastMessage = max(times) 

		except ValueError,e:
			print(e)
		except KeyError,e:
			timeOfLastMessage = time.time()

		#Run again but only check for messages later than the latest on we've already done
		self.runListener(messageHandler,str(timeOfLastMessage)) 
