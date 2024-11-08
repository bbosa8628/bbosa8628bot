from flask import Flask, jsonify, request
import requests
import tweepy
import time
import threading

app = Flask(__name__)

# Twitter API authentication details (Replace with your actual details)
bearer_token = ""
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

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

# Function to get a random controversial phrase with retry logic
def get_random_controversial_phrase():
    api_url = "https://scarlett-gjrx.onrender.com/"  # Update this to your actual API link
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, timeout=20)  # Increased timeout
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            return data.get("controversial_phrase", "No phrase available")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:  # Don't delay after the final attempt
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Failed to fetch data.")
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
