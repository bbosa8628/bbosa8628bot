from flask import Flask, jsonify, request
import requests
import tweepy
import time

app = Flask(__name__)

# Twitter API authentication details
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

# Endpoint to get a random controversial phrase
@app.route('/get_phrase', methods=['GET'])
def get_random_controversial_phrase():
    api_url = "https://scarlett-gjrx.onrender.com/"  # Update this to your actual API link
    response = requests.get(api_url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            category = data.get("category", "Unknown")
            controversial_phrase = data.get("controversial_phrase", "No phrase available")
            return jsonify({"category": category, "phrase": controversial_phrase})
        except ValueError:
            return jsonify({"error": "Failed to parse JSON"}), 500
    else:
        return jsonify({"error": "Failed to fetch data from the API", "status_code": response.status_code}), response.status_code

# Endpoint to upload an image
def upload_image(image_path):
    try:
        media = api_v1.media_upload(image_path)
        return media.media_id
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

# Endpoint to post a tweet
@app.route('/post_tweet', methods=['POST'])
def post_tweet():
    data = request.get_json()
    image = data.get('image', "")
    text = data.get('text', "")
    
    if image:
        media_id = upload_image(image)
        if media_id:
            client_v2.create_tweet(text=text, media_ids=[media_id])
            return jsonify({"status": "Tweeted with image and text"}), 200
        else:
            return jsonify({"error": "Failed to upload image"}), 500
    elif text:
        client_v2.create_tweet(text=text)
        return jsonify({"status": "Tweeted with text only"}), 200
    else:
        return jsonify({"error": "No text or image provided"}), 400

# Endpoint to trigger a tweet with a random phrase
@app.route('/tweet_random_phrase', methods=['POST'])
def tweet_random_phrase():
    response = get_random_controversial_phrase()
    if response.status_code == 200:
        phrase = response.json().get("phrase")
        post_tweet_data = {"text": phrase}
        return post_tweet(), 200
    else:
        return jsonify({"error": "Could not retrieve phrase"}), 500

if __name__ == '__main__':
    app.run(debug=True)
