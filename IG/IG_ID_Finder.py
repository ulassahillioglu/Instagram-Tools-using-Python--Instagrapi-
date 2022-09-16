from instagrapi import Client

bot = Client()
bot.handle_exception
try:
    bot.load_settings('./ig_dump.json')  #load the settings from previous sessions to make Instagram trust you more
except Exception as e:
    print(e)
    bot.dump_settings('./ig_dump.json')
bot.login(username ="",password="")

user_input= input("Enter the username : ") ##Enter your username and password here

user_id = bot.user_id_from_username(user_input)

print(user_id)
