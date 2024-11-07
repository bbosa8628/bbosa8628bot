import requests
import tweepy
import language_tool_python  # Assuming this package for grammar correction
import time  # Import time module for scheduling

print ('runnning...')
print ('')
# Scarlett bot's variables
image = ""  # Set to an empty string if there's no image

# Authentication details (replace these with your own credentials)
bearer_token = "AAAAAAAAAAAAAAAAAAAAAM5jrwEAAAAAatuGI9B7nDq%2Fd3ISi6fw%2FRtBEIU%3D0RFD3tnMRjOZb10GbLcQ6ssaU1xtDR4UxytSJ1h0cw12x8gdk8"
consumer_key = "3egxky6Ftp9pwYpbDg9vUNofU"
consumer_secret = "C05f4FX7wxmWDCdSYqreEyNDvT1xKMjCQftYZZ6sfZbK8UQkBY"
access_token = "1744117039608852480-BkwFNFnquOWjjZEvQ2Zd41pCdW02x9"
access_token_secret = "t8ttiDPS58NAjDG1dBSXDxpQq6WfGQcBc8iFE0HMMMUai"

# V1 Authentication (OAuth 1.0a)
auth_v1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth_v1.set_access_token(access_token, access_token_secret)

# V1 API for uploading media (for image upload)
api_v1 = tweepy.API(auth_v1, wait_on_rate_limit=True)

# V2 Authentication (OAuth 2.0)
client_v2 = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
)

# Function to get a random controversial phrase from the API
def get_random_controversial_phrase():
    api_url = "https://scarlett-gjrx.onrender.com/"  # Update this to your actual API link
    response = requests.get(api_url)
    
    if response.status_code == 200:
        try:
            # Parse the JSON response and access "category" and "controversial_phrase"
            data = response.json()
            category = data.get("category", "Unknown")
            controversial_phrase = data.get("controversial_phrase", "No phrase available")
            print(f"Category: {category}")
            print(f"Original Phrase: {controversial_phrase}\n")
            return controversial_phrase
        except ValueError:
            print("Failed to parse JSON. The response might not be valid JSON.")
            return None
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        return None

# Function to make the phrase grammatically correct and more human-like
def generate_better_tweet(phrase):
    tool = language_tool_python.LanguageTool('en-US')  # Initialize language tool for grammar correction
    corrected_text = tool.correct(phrase)  # Correct grammatical issues
    # Ensure the tweet is within 280 characters
    if len(corrected_text) > 280:
        corrected_text = corrected_text[:277] + "..."  # Truncate and add ellipsis if too long
    print(f"Corrected Phrase (within 280 chars): {corrected_text}\n")
    return corrected_text

# Function to upload media to Twitter using API v1
def upload_image(image_path):
    try:
        media = api_v1.media_upload(image_path)
        print(f"Image uploaded successfully. Media ID: {media.media_id}")
        return media.media_id
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

# Function to post the tweet based on image and text (Twitter API v2)
def post_tweet(image, text):
    if image and text:
        media_id = upload_image(image)
        if media_id:
            client_v2.create_tweet(text=text, media_ids=[media_id])
            print(f"Tweeted with image and text: {text}")
        else:
            print("Failed to upload image, tweet not posted.")
    elif text:
        client_v2.create_tweet(text=text)
        print(f"Tweeted with text: {text}")
    elif image:
        media_id = upload_image(image)
        if media_id:
            client_v2.create_tweet(text="", media_ids=[media_id])
            print("Tweeted with image only")

# Main function to generate and post the tweet
def main():
    while True:
        random_phrase = get_random_controversial_phrase()
        if random_phrase:
            bettertweet = generate_better_tweet(random_phrase)
            text = bettertweet  # Assign the corrected phrase to the text variable
            post_tweet(image, text)
        
        print ('')
        print ('going for another...')
        # Delay before the next tweet
        time.sleep(3600)  # Run every hour (3600 seconds)

# Run the bot
main()
