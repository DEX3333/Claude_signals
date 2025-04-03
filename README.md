# Claude_signals
Twitter Crypto Listings Tracker
This Python script monitors @NewListingsFeed on Twitter for new cryptocurrency listings, checks if they are listed on Hyperliquid exchange, and uses Claude AI to evaluate potential short opportunities.
Features

Automatically monitors Twitter for new coin listing announcements
Extracts coin symbols from tweet text
Checks if coins are available on Hyperliquid exchange
Uses Claude AI to analyze short opportunities
Provides detailed analysis and rating for each opportunity
Maintains a record of processed tweets to avoid duplication

Requirements

Python 3.7 or higher
Twitter API v2 Bearer Token
Anthropic API key for Claude

Installation

Clone this repository:

Copygit clone https://github.com/yourusername/twitter-crypto-listings-tracker.git
cd twitter-crypto-listings-tracker

Install required packages:

Copypip install requests anthropic

Set up your API keys:

Replace YOUR_TWITTER_BEARER_TOKEN with your Twitter API Bearer Token
Replace YOUR_ANTHROPIC_API_KEY with your Anthropic API key



Usage

Run the script:

Copypython crypto_listings_tracker.py

The script will:

Poll Twitter for new tweets from @NewListingsFeed
Extract coin symbols from new tweets
Check if these coins are available on Hyperliquid
For matches, analyze the short opportunity using Claude
Display analysis results in the console


To stop the script:

Press Ctrl+C to exit gracefully



Configuration Options
The following constants can be modified in the script:

CHECK_INTERVAL: Time between Twitter checks in seconds (default: 600 seconds / 10 minutes)
MAX_TWEETS_TO_FETCH: Number of tweets to fetch in each request (default: 10)
PROCESSED_TWEETS_FILE: File to store processed tweet IDs (default: "processed_tweets.json")

Claude Analysis
For each matching coin, Claude provides analysis of:

Short opportunity potential
Factors making it attractive or unattractive
Potential risks
Reasonable price targets
Overall confidence rating (1-10)

Example Output
CopyStarting Twitter Crypto Listings Tracker at 2025-04-03 10:15:22
Found Twitter user ID: 1234567890 for @NewListingsFeed

Checking for new tweets at 2025-04-03 10:15:24

New tweet at 2025-04-03T10:10:00Z:
'New Listing: $XYZ will be listed on Exchange A and Exchange B'
Extracted coin symbols: ['XYZ']
MATCH FOUND: XYZ is on Hyperliquid!

----- CLAUDE ANALYSIS -----
COIN: XYZ

Analysis:
1. This appears to be a moderate short opportunity, rating 6/10.
2. Attractive factors: Multiple exchange listings often lead to price pumps followed by dumps.
3. Risks: Initial volatility could lead to liquidation if position sizing is poor.
4. Price targets: Consider taking profit at 15-20% below listing price.
5. Rating: 6/10 confidence as a short opportunity.
----------------------------

Waiting 600 seconds before next check...
Press Ctrl+C to exit the program
Enhancements & Customization
You can enhance this script by:

Adding notification systems (Discord, Telegram, email)
Incorporating historical price tracking
Connecting to Hyperliquid's trading API for automated execution
Improving the coin symbol extraction logic for better accuracy
Adding support for additional crypto exchanges

Disclaimer
This tool is for informational purposes only. Cryptocurrency trading involves significant risk. Always do your own research before making trading decisions.
License
MIT
Author
Dex33
