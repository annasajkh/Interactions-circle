import tweepy
import math
from PIL import Image, ImageDraw
import urllib.request
import random
import glob
import os
import time

auth = tweepy.OAuthHandler("-", "-")
auth.set_access_token("-", "-")
api = tweepy.API(auth)

max_tweets_check_limit = 3200
min_score = 20
target_username = "annasVirtual".lower()
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
    if not status.entities["user_mentions"]:
        continue

    tweettext = str(status.full_text.lower().encode("ascii",errors="ignore"))

    if "rt @" in tweettext:
        retweet_username = tweettext.split(":")[0].split("@")[1]
        update_interacted_users(retweet_username, 3,None)
        continue

    
    for user in status.entities["user_mentions"]:
        update_interacted_users(user["screen_name"], 2,None)

    if count == max_tweets_check_limit:
        break

    count += 1

for status in tweepy.Cursor(api.favorites,screen_name=target_username).items():
    update_interacted_users(status.user.screen_name.lower(), 1, status.user.profile_image_url)

    if count == max_tweets_check_limit:
        break

    count += 1


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


for name, score in interacted_users.items():
    try:
        random_angle = random.uniform(0,full_circle)

        x = math.cos(random_angle) 
        y = math.sin(random_angle) 

        x *= (1 - score / max_score) * (bg_w / 2 - img_w / 2)
        y *= (1 - score / max_score) * (bg_h / 2 - img_h / 2)
        
        x += bg_w / 2 - img_w / 2
        y += bg_h / 2 - img_w / 2

        if score == max_score:
            x += img_w
            y += img_w 
        
        bg.paste(Image.open(f"{name}.png"),(int(x),int(y)))

    except Exception as e:
        print(e)
        print(name)
        


bg.paste(img,offset)

bg.save("result.png")

for path in glob.glob("*.png"):
    if "result" not in path:
        os.remove(path)
