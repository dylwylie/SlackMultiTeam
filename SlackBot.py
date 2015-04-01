import sys,requests,json,threading,time

class SlackBot():

	URL = 'https://slack.com/api/'

	def __init__(self,token,channel):

		self.token = 'token=' +  token
		self.channel = channel
		self.channel_users = usersInThisChannel()

	def call(self,method,arguments=None):

		URL = self.URL + method + '?' + self.token

		if(arguments):

			for argument in arguments:

				URL+= '&' + argument

		return requests.get(URL)∫

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

		return self.call('channels.list')

	def channelInfo(self,channel):

		arguments = ['channel='+channel]
		r = self.call('channels.info',arguments)
		return r.json()

	def getUser(self,id):

		arguments = ['user='+id]
		r = self.call('users.info',arguments)
		return(r.json()[unicode('user')])

	def usersInThisChannel(self):

		channel_user_ids = self.channelInfo(self.channel)["channel"]["members"]

		user_ids = []
		usernames = []

		for user_id in channel_user_ids:

			username = self.getUser(user_id)["name"]
			user_ids.append(user_id)
			usernames.append(username)

		#doubly keyed list of the form {user_id : username}
		return dict(zip(user_ids,usernames))



	# !BLOCKING! #
	def runListener(self,messageHandler,timeOfLastMessage=str(time.time())):

		loops = 0 #Use this to call things we don't want to every 0.1 seconds
		while(1):

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
							
							del text,user_id,user_profile,username,user_image
						#Take the timestamp of each message
						times.append(messageTime) 

					#Get the timestamp of the latest one
					timeOfLastMessage = max(times) 
					del response,messages

				loops += 1

				if(loops > 10):
					self.channel_users = usersInThisChannel()
					loops = 0

			except ValueError,e:
				print(e)
			except KeyError,e:
				timeOfLastMessage = str(time.time())

			del arguments,r
			time.sleep(0.1)
		#Run again but only check for messages later than the latest on we've already done
