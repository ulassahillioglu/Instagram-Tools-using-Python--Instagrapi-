import os

from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired, UnknownError
)
links = [""]



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
    bot.dump_settings('./ig_dump.json')
bot.handle_exception
bot.login(username="", password="") ##Enter your username and password here

text =  [""]


text2 = " "

for l in range(len(links)):
  pk = bot.media_pk_from_url(links[l])
  print(pk)
  url1 = bot.media_info(pk).video_url
  bot.video_download_by_url(url1, folder= "Images")

f = os.listdir("Images")

for v in range(len(f)):
    if f[v].endswith(".mp4"):
      
        try:
            a = "Images/" + f[v]
            bot.video_upload(
            a,
            caption=text2,
            )
        except UnknownError:
            continue
        except IndexError:
            pass
        finally:
            print("Session completed. Starting next one")
    else:
        print("File type not supported")    
