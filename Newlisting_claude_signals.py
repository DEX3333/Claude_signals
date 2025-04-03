import requests
import json
import time
from datetime import datetime
import os
from anthropic import Anthropic

# Configuration
TWITTER_BEARER_TOKEN = "your_bearer_token_here"
TWITTER_ACCOUNT = "NewListingsFeed"
ANTHROPIC_API_KEY = "your_anthropic_api_key_here"
CHECK_INTERVAL = 600  # seconds between checks (10 minutes)
MAX_TWEETS_TO_FETCH = 10

# Initialize Anthropic client
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

# Twitter API v2 endpoints
TWITTER_USER_LOOKUP_URL = "https://api.twitter.com/2/users/by/username/"
TWITTER_USER_TWEETS_URL = "https://api.twitter.com/2/users/{}/tweets"

# Hyperliquid API endpoint
HYPERLIQUID_MARKETS_URL = "https://api.hyperliquid.xyz/info"

# File to store processed tweet IDs
PROCESSED_TWEETS_FILE = "processed_tweets.json"

def get_twitter_headers():
    """Returns headers for Twitter API requests."""
    return {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

def get_twitter_user_id(username):
    """Get Twitter user ID from username."""
    url = f"{TWITTER_USER_LOOKUP_URL}{username}"
    response = requests.get(url, headers=get_twitter_headers())
    if response.status_code != 200:
        raise Exception(f"Failed to get user ID: {response.status_code} {response.text}")
    return response.json()["data"]["id"]

def get_latest_tweets(user_id):
    """Get latest tweets from a user."""
    url = TWITTER_USER_TWEETS_URL.format(user_id)
    params = {
        "max_results": MAX_TWEETS_TO_FETCH,
        "tweet.fields": "created_at",
        "exclude": "retweets,replies"
    }
    response = requests.get(url, headers=get_twitter_headers(), params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get tweets: {response.status_code} {response.text}")
    return response.json()["data"]

def get_hyperliquid_markets():
    """Get all markets available on Hyperliquid."""
    payload = {
        "type": "meta"
    }
    response = requests.post(HYPERLIQUID_MARKETS_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to get Hyperliquid markets: {response.status_code} {response.text}")
    
    data = response.json()
    return {coin["name"]: coin for coin in data["universe"]}

def extract_coin_symbols_from_tweet(tweet_text):
    """
    Extract potential coin symbols from tweet text.
    This is a basic implementation and might need refinement based on the actual tweet formats.
    """
    # Common formats in listing announcements
    # Example tweet: "New Listing: $XYZ will be listed on Exchange"
    potential_symbols = []
    
    # Look for dollar sign followed by uppercase letters
    import re
    dollar_symbols = re.findall(r'\$([A-Z]+)', tweet_text)
    potential_symbols.extend(dollar_symbols)
    
    # Look for common phrases like "will list" or "new listing"
    common_phrases = [
        r'(?:listing|lists?|listed|adding|adds?|added)\s+([A-Z]+)',
        r'([A-Z]+)\s+(?:listing|will be listed|is listed|now available)'
    ]
    
    for phrase in common_phrases:
        matches = re.findall(phrase, tweet_text, re.IGNORECASE)
        potential_symbols.extend([m for m in matches if len(m) >= 2 and m.isupper()])
    
    # Remove duplicates and filter out common words that are all caps
    common_words = ["THE", "AND", "NEW", "NOW", "LIVE", "FOR", "ON"]
    filtered_symbols = [sym for sym in set(potential_symbols) if sym not in common_words]
    
    return filtered_symbols

def analyze_with_claude(coin_symbol, tweet_text, hyperliquid_data):
    """Use Anthropic's Claude to analyze the potential short opportunity."""
    prompt = f"""
    I need your help analyzing a new cryptocurrency listing. Please evaluate it as a potential short opportunity on Hyperliquid exchange.
    
    COIN: {coin_symbol}
    
    LISTING ANNOUNCEMENT: "{tweet_text}"
    
    HYPERLIQUID DATA: {json.dumps(hyperliquid_data, indent=2) if hyperliquid_data else "Not available on Hyperliquid yet"}
    
    Please analyze:
    1. Is this likely to be a good short opportunity on Hyperliquid?
    2. What factors make it attractive or unattractive for shorting?
    3. What are the potential risks?
    4. What price targets would be reasonable?
    5. Give this opportunity a rating from 1-10 where 10 is the highest confidence short.
    
    Please be concise and direct in your evaluation.
    """
    
    response = anthropic.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

def load_processed_tweets():
    """Load IDs of already processed tweets."""
    if os.path.exists(PROCESSED_TWEETS_FILE):
        with open(PROCESSED_TWEETS_FILE, "r") as f:
            return json.load(f)
    return []

def save_processed_tweet(tweet_id):
    """Save a tweet ID as processed."""
    processed_tweets = load_processed_tweets()
    processed_tweets.append(tweet_id)
    with open(PROCESSED_TWEETS_FILE, "w") as f:
        json.dump(processed_tweets, f)

def main():
    """Main function to run the script."""
    print(f"Starting Twitter Crypto Listings Tracker at {datetime.now()}")
    
    # Get Twitter user ID
    user_id = get_twitter_user_id(TWITTER_ACCOUNT)
    print(f"Found Twitter user ID: {user_id} for @{TWITTER_ACCOUNT}")
    
    # Initial load of processed tweets
    processed_tweets = load_processed_tweets()
    
    while True:
        try:
            print(f"\nChecking for new tweets at {datetime.now()}")
            
            # Get latest tweets
            tweets = get_latest_tweets(user_id)
            
            # Get current Hyperliquid markets
            hyperliquid_markets = get_hyperliquid_markets()
            available_coins = list(hyperliquid_markets.keys())
            print(f"Found {len(available_coins)} coins on Hyperliquid")
            
            # Process new tweets
            for tweet in tweets:
                tweet_id = tweet["id"]
                
                # Skip already processed tweets
                if tweet_id in processed_tweets:
                    continue
                
                tweet_text = tweet["text"]
                created_at = tweet["created_at"]
                print(f"\nNew tweet at {created_at}:")
                print(f"'{tweet_text}'")
                
                # Extract potential coin symbols
                coin_symbols = extract_coin_symbols_from_tweet(tweet_text)
                print(f"Extracted coin symbols: {coin_symbols}")
                
                # Check if any extracted symbol is on Hyperliquid
                for symbol in coin_symbols:
                    if symbol in available_coins:
                        print(f"MATCH FOUND: {symbol} is on Hyperliquid!")
                        
                        # Analyze with Claude
                        coin_data = hyperliquid_markets.get(symbol)
                        analysis = analyze_with_claude(symbol, tweet_text, coin_data)
                        
                        print("\n----- CLAUDE ANALYSIS -----")
                        print(analysis)
                        print("----------------------------\n")
                    else:
                        print(f"{symbol} not found on Hyperliquid.")
                
                # Mark this tweet as processed
                save_processed_tweet(tweet_id)
            
            print(f"Waiting {CHECK_INTERVAL} seconds before next check...")
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Error encountered: {e}")
            print("Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()