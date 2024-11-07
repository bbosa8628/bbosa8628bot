from flask import Flask, jsonify, request
import requests
import tweepy
import time
import threading

app = Flask(__name__)

# Twitter API authentication details (Replace with your actual details)
bearer_token = "AAAAAAAAAAAAAAAAAAAAAM5jrwEAAAAAatuGI9B7nDq%2Fd3ISi6fw%2FRtBEIU%3D0RFD3tnMRjOZb10GbLcQ6ssaU1xtDR4UxytSJ1h0cw12x8gdk8"
consumer_key = "3egxky6Ftp9pwYpbDg9vUNofU"
consumer_secret = "C05f4FX7wxmWDCdSYqreEyNDvT1xKMjCQftYZZ6sfZbK8UQkBY"
access_token = "1744117039608852480-BkwFNFnquOWjjZEvQ2Zd41pCdW02x9"
access_token_secret = "t8ttiDPS58NAjDG1dBSXDxpQq6WfGQcBc8iFE0HMMMUai"

# V1 Authentication for media upload
auth_v1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth_v1.set_access_token(access_token, access_token_secret)
api_v1 = tweepy.API(auth_v1, wait_on_rate_limit=True)

# V2 Authentication for tweet posting
client_v2 = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
)

# Function to get a random controversial phrase
def get_random_controversial_phrase():
    api_url = "https://scarlett-gjrx.onrender.com/"  # Update this to your actual API link
    response = requests.get(api_url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            category = data.get("category", "Unknown")
            controversial_phrase = data.get("controversial_phrase", "No phrase available")
            return controversial_phrase
        except ValueError:
            print("Failed to parse JSON. The response might not be valid JSON.")
            return None
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        return None

# Function to upload media to Twitter
def upload_image(image_path):
    try:
        media = api_v1.media_upload(image_path)
        return media.media_id
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

# Function to post the tweet
def post_tweet(image, text):
    if image and text:
        media_id = upload_image(image)
        if media_id:
            client_v2.create_tweet(text=text, media_ids=[media_id])
            print(f"Tweeted with image and text: {text}")
    elif text:
        client_v2.create_tweet(text=text)
        print(f"Tweeted with text: {text}")
    elif image:
        media_id = upload_image(image)
        if media_id:
            client_v2.create_tweet(text="", media_ids=[media_id])
            print("Tweeted with image only")

# Bot's main loop function
def main():
    while True:
        random_phrase = get_random_controversial_phrase()
        if random_phrase:
            post_tweet(image="", text=random_phrase)
        
        print('Waiting for the next hour...')
        time.sleep(600)  # Run every hour

# Function to start the bot in a background thread
def start_bot():
    bot_thread = threading.Thread(target=main)
    bot_thread.daemon = True  # Allows thread to exit when the main program exits
    bot_thread.start()

# Root endpoint
@app.route('/')
def index():
    return "Flask API with bot is running in background."

# Start the bot when the server starts
if __name__ == '__main__':
    start_bot()  # Start the bot in the background
    app.run(debug=True)
