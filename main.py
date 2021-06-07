import tweepy
import math
from PIL import Image
import urllib.request
import random
import glob
import os
import math

auth = tweepy.OAuthHandler(os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"])
auth.set_access_token(os.environ["ACCESS_TOKEN"],os.environ["ACCESS_TOKEN_SECRET"])

api = tweepy.API(auth)

max_tweets_check_limit = 3000
min_score = 10
target_username = "tdxf20".lower()
interacted_users = {}
user_profil_url = {}
count = 0

def update_interacted_users(username, value, profil_url):
    username = username.lower()

    if username in interacted_users.keys():
        interacted_users[username] += value
    else:
        interacted_users[username] = value
        user_profil_url[username] = profil_url


for status in tweepy.Cursor(api.user_timeline,screen_name=target_username,tweet_mode="extended").items():

    tweettext = str(status.full_text.lower().encode("ascii",errors="ignore"))


    if "rt @" in tweettext:
        retweet_username = tweettext.split(":")[0].split("@")[1]

        update_interacted_users(retweet_username, 3,None)
        print(f"{retweet_username} gets 3 score")

        continue

    if not status.entities["user_mentions"]:
        continue
    
    for user in status.entities["user_mentions"]:
        name = user["screen_name"]

        print(f"{name} gets 2 score")
        update_interacted_users(name ,2,None)

    if count == max_tweets_check_limit:
        break

    count += 1

try:
    for status in tweepy.Cursor(api.favorites,screen_name=target_username).items():
        print(f"{status.user.screen_name.lower()} gets 1 score")

        update_interacted_users(status.user.screen_name.lower(), 1, status.user.profile_image_url)

        if count == max_tweets_check_limit:
            break

        count += 1
except:
    pass


interacted_users = {k:v for k,v in interacted_users.items() if v >= min_score and k != target_username}
user_profil_url = {k:v for k,v in user_profil_url.items() if k in interacted_users.keys()}


urllib.request.urlretrieve(api.get_user(target_username).profile_image_url,f"{target_username}.png")

for name, url in user_profil_url.items():
    try:
        if url == None:
            user_profil_url[name] = api.get_user(name).profile_image_url
            urllib.request.urlretrieve(user_profil_url[name],f"{name}.png")
        else:
            urllib.request.urlretrieve(user_profil_url[name],f"{name}.png")
    except:
        continue


bg = Image.new("RGBA", (1000,1000),color="yellow")
img = Image.open(f"{target_username}.png")

img_w, img_h = img.size
bg_w, bg_h = bg.size

offset = ((bg_w - img_w) // 2, (bg_h - img_h) //2)

full_circle = math.pi * 2

max_score = max(list(interacted_users.values()))

def map(old_value,old_min, old_max, new_min, new_max):
    return (((old_value - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min


for name, score in interacted_users.items():
    try:
        random_angle = random.random() * full_circle

        length = 1 - score / max_score
        length = map(length, 0, 1, img_w, bg_w / 2 - img_w / 2)

        x = math.cos(random_angle) * length
        y = math.sin(random_angle) * length

        x += bg_w / 2
        y += bg_h / 2

        print(x)
        print(y)
        
        bg.paste(Image.open(f"{name}.png"),(int(x),int(y)))

    except Exception as e:
        print(e)
        print(name)
        


bg.paste(img,offset)

bg.save("result.png")

for path in glob.glob("*.png"):
    if "result" not in path:
        os.remove(path)
