import requests, time


class SlackBot():
    URL = 'https://slack.com/api/'

    def __init__(self, token, channel):

        self.token = 'token=' + token
        self.channel = channel
        self.channel_users = self.get_users_in_this_channel

    def call(self, method, arguments=None):

        url = self.URL + method + '?' + self.token

        if arguments:

            for argument in arguments:

                url += '&' + argument

        return requests.get(url)

    def send_message(self, username, text, icon_url=None):

        channel = self.channel
        arguments = ['channel=' + channel, 'username=' + username, 'text=' + text]

        if icon_url:
            arguments.append('icon_url=' + icon_url)

        r = self.call('chat.postMessage', arguments)
        return r

    def join_channel(self, channel):

        arguments = ['name=' + channel]
        r = self.call('channels.join', arguments)
        return r

    def list_channels(self):

        return self.call('channels.list')

    def channel_info(self, channel):

        arguments = ['channel=' + channel]
        r = self.call('channels.info', arguments)
        return r.json()

    def get_user(self, user_id):

        arguments = ['user=' + user_id]
        r = self.call('users.info', arguments)
        return r.json()[unicode('user')]

    def get_users_in_this_channel(self):

        channel_user_ids = self.channel_info(self.channel)["channel"]["members"]

        user_ids = []
        usernames = []

        for user_id in channel_user_ids:
            username = self.get_user(user_id)["name"]
            user_ids.append(user_id)
            usernames.append(username)

        # doubly keyed list of the form {user_id : username}
        return dict(zip(user_ids, usernames))

    # !BLOCKING! #
    def run_listener(self, message_handler, time_of_last_message=str(time.time())):

        loops = 0  # Use this to call things we don't want to every 0.1 seconds

        while 1:

            arguments = ['channel=' + self.channel, 'inclusive=0', 'oldest=' + time_of_last_message]

            r = self.call('channels.history', arguments)

            try:
                response = r.json()
                messages = response[unicode('messages')]

                if messages:  # Has we some messages to deal with?

                    times = []

                    for message in messages:

                        message_time = message[unicode('ts')]

                        if message_time != time_of_last_message:

                            text = message[unicode('text')]
                            user_id = message[unicode('user')]
                            user_profile = self.get_user(user_id)
                            username = user_profile[unicode('name')]
                            user_image = user_profile[unicode('profile')][unicode('image_48')]

                            message_handler(text, username, user_image)
                            # handle our messages

                            del text, user_id, user_profile, username, user_image
                        # Take the timestamp of each message
                        times.append(message_time)

                    # Get the timestamp of the latest one
                    time_of_last_message = max(times)
                    del response, messages

                loops += 1

                if loops > 10:
                    self.channel_users = self.get_users_in_this_channel()
                    loops = 0

            except ValueError, e:
                print(e)
            except KeyError:
                time_of_last_message = str(time.time())

            del arguments, r
            time.sleep(0.1)
        # Run again but only check for messages later than the latest on we've already done
