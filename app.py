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
    try:
        response = requests.get(api_url, timeout=10)  # Timeout added
        response.raise_for_status()  # Raise error for HTTP codes like 404, 500
        data = response.json()
        return data.get("controversial_phrase", "No phrase available")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from the API: {e}")
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
    try:
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
    except tweepy.TweepyException as e:
        print(f"Error posting tweet: {e}")

# Bot's main loop function
def main():
    while True:
        random_phrase = get_random_controversial_phrase()
        if random_phrase:
            post_tweet(image="", text=random_phrase)
        
        print('Waiting for the next interval...')
        time.sleep(3600)  # Run every hour

# Function to start the bot in a background thread
def start_bot():
    bot_thread = threading.Thread(target=main)
    bot_thread.daemon = True  # Allows thread to exit when the main program exits
    bot_thread.start()

# Root endpoint
@app.route('/')
def index():
    return "Flask API with bot is running in background."

# Endpoint to start the bot if needed (e.g., for troubleshooting)
@app.route('/start-bot')
def start_bot_route():
    start_bot()
    return "Bot started."

# Start the server and bot in production environments
if __name__ == '__main__':
    start_bot()  # Start the bot in the background
    app.run(debug=True)
