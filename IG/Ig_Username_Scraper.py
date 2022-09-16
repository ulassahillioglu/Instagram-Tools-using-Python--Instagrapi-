from instagrapi import Client
import json
import os, os.path
import time
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired, UnknownError, PhotoNotUpload, ChallengeUnknownStep
)
import random

from requests import JSONDecodeError
class Account:
    username = ""
    password = ""

    def get_client(self):
        """We return the client class, in which we automatically handle exceptions
        You can move the "handle_exception" above or into an external module
        """

        def handle_exception(client, e):
            if isinstance(e, BadPassword):
                client.logger.exception(e)
                client.set_proxy(self.next_proxy().href)
                if client.relogin_attempt > 0:
                    self.freeze(str(e), days=7)
                    raise ReloginAttemptExceeded(e)
                client.settings = self.rebuild_client_settings()
                return self.update_client_settings(client.get_settings())
            elif isinstance(e, LoginRequired):
                client.logger.exception(e)
                client.relogin()
                return self.update_client_settings(client.get_settings())
            elif isinstance(e, ChallengeRequired):
                api_path = client.last_json.get("challenge", {}).get("api_path")
                if api_path == "/challenge/":
                    client.set_proxy(self.next_proxy().href)
                    client.settings = self.rebuild_client_settings()
                else:
                    try:
                        client.challenge_resolve(client.last_json)
                    except ChallengeRequired as e:
                        self.freeze('Manual Challenge Required', days=2)
                        raise e
                    except (ChallengeRequired, SelectContactPointRecoveryForm, RecaptchaChallengeForm) as e:
                        self.freeze(str(e), days=4)
                        raise e
                    self.update_client_settings(client.get_settings())
                return True
            elif isinstance(e, FeedbackRequired):
                message = client.last_json["feedback_message"]
                if "This action was blocked. Please try again later" in message:
                    self.freeze(message, hours=12)
                    # client.settings = self.rebuild_client_settings()
                    # return self.update_client_settings(client.get_settings())
                elif "We restrict certain activity to protect our community" in message:
                    # 6 hours is not enough
                    self.freeze(message, hours=12)
                elif "Your account has been temporarily blocked" in message:
                    """
                    Based on previous use of this feature, your account has been temporarily
                    blocked from taking this action.
                    This block will expire on 2020-03-27.
                    """
                    self.freeze(message)
            elif isinstance(e, PleaseWaitFewMinutes):
                self.freeze(str(e), hours=1)
            raise e

        cl = Client()
        cl.handle_exception = handle_exception
        cl.login(self.username, self.password)
        return cl


bot = Client()
try:
    bot.load_settings('./ig_dump.json')  #load the settings from previous sessions to make Instagram trust you more
except Exception as e:
    print(e)
    bot.dump_settings('./ig_dump.json')   #Path could be changed depending on user

    
bot.login(username ="",password="")  ##Enter your username and password here

user_input= input("Enter the username : ")

user_id = bot.user_id_from_username(user_input) #get user ID of the given account

print(user_id)

time.sleep(60)
followers = bot.user_followers(user_id).keys() #get dict of User IDs of the followers


mySet = set()
i = 0
for follower in followers:
    # print(len(bot.user_followers(follower).keys()))
    try:
        follower_info = bot.user_info(follower).dict() #collect user info of the followers by iterating over user IDs
        mySet.add(follower_info['username'])  ## Using set to avoid duplications
        i+=1
        time.sleep(5)
        if (i%10) == 0:
            time.sleep(random.randint(75,255))
        else:
            continue
    except JSONDecodeError as jde:
        print(jde)
        time.sleep(10)
        

f = open("Usernames.txt","w",encoding="utf-8") 
for username in mySet:
    f.write(username + "\n\n")
f.close()


