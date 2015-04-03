import requests
import time
import re


class SlackBot():
    URL = 'https://slack.com/api/'

    def __init__(self, token, channel):

        self.token = token
        self.channel = channel
        self.channel_users = self.get_users_in_this_channel()
        self.inverse_channel_users = self.get_users_in_this_channel(inverse=True)

    def call(self, method, arguments=None):

        url = self.URL + method

        if arguments:

            payload = arguments
            payload["token"] = self.token

        else:

            payload = {"token": self.token}

        return requests.get(url, params=payload)

    def join_channel(self, channel):

        arguments = {"name": channel}
        r = self.call('channels.join', arguments)
        return r

    def list_channels(self):

        return self.call('channels.list')

    def channel_info(self, channel):

        arguments = {"channel": channel}
        r = self.call('channels.info', arguments)
        return r.json()

    def get_user(self, user_id):

        arguments = {"user": user_id}
        r = self.call('users.info', arguments)
        return r.json()[unicode('user')]

    def get_users_in_this_channel(self, inverse=False):

        channel_user_ids = self.channel_info(self.channel)["channel"]["members"]

        user_ids = []
        usernames = []

        for user_id in channel_user_ids:
            username = self.get_user(user_id)["name"]
            user_ids.append(user_id)
            usernames.append(username)

        if not inverse:
            zipped = zip(user_ids, usernames)
        else:
            zipped = zip(usernames, user_ids)
        # doubly keyed list of the form {user_id : username}
        return dict(zipped)


class SlackBotSender(SlackBot):

    def send_message(self, username, text, icon_url=None):

        text = self.check_for_tag_and_replace(text)
        channel = self.channel
        arguments = {"channel": channel, "username": username, "text": text}

        if icon_url:

            arguments["icon_url"] = icon_url

        r = self.call('chat.postMessage', arguments)
        return r

    def check_for_tag_and_replace(self, text):

        found_users = re.findall("(?:^|\W)@(\w+)(?!\w)", text)

        if found_users:

            for found_user_name in found_users:

                user_id = self.inverse_channel_users.get(unicode(found_user_name))

                if user_id:
                    text = text.replace('@' + found_user_name, '<@' + user_id + '|' + found_user_name + '>')

        return text


class SlackBotReceiver(SlackBot):

    def get_message_history(self, time_of_last_message):

        arguments = {"channel": self.channel, "inclusive" : 0, "oldest": time_of_last_message}
        return self.call('channels.history', arguments).json()

    def parse_message_for_sending(self, text):

        # text = text.replace("&amp", "&")
        # text = text.replace("&lt", "<")
        # text = text.replace("&gt", ">")

        found_users = re.findall("<@U........>", text)

        for found_user_id in found_users:
            name = self.channel_users.get(found_user_id[2:][:-1])

            if name:
                text = text.replace(found_user_id, "@" + name)

        return text

    def listen(self, message_handler, time_of_last_message):

        try:

            message_history = self.get_message_history(time_of_last_message)
            messages = message_history[unicode('messages')]

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

                        # Look for tags

                        text = self.parse_message_for_sending(text)
                        message_handler.send_message(username,text,user_image)
                        # handle our messages

                        del text, user_id, user_profile, username, user_image

                    # Take the timestamp of each message
                    times.append(message_time)

                # Get the timestamp of the latest one
                time_of_last_message = max(times)

                del message_history, messages

        except ValueError, e:
            print(e)
        except KeyError:
            time_of_last_message = str(time.time())

        return time_of_last_message

    def run_listener(self, message_handler):

        loops = 0  # Use this to call things we don't want to every 0.1 seconds
        time_of_last_message=str(time.time())

        while 1:

            time_of_last_message = self.listen(message_handler, time_of_last_message)

            loops += 1

            if loops > 10:
                self.channel_users = self.get_users_in_this_channel()
                message_handler.inverse_channel_users = message_handler.get_users_in_this_channel(inverse=True)

            loops = 0

            time.sleep(0.1)

