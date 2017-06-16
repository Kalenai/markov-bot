"""
    Configuration data for your twitter bot.
"""

# Twitter API Key and Tokens
CONSUMER_KEY = "IT'S A SECRET TO EVERYBODY."
CONSUMER_SECRET = "IT'S A SECRET TO EVERYBODY."
ACCESS_TOKEN_KEY = "IT'S A SECRET TO EVERYBODY."
ACCESS_TOKEN_SECRET = "IT'S A SECRET TO EVERYBODY."

# Database Settings
DATABASE_NAME = "Enter your database name."
DATABASE_USER = "Enter your database user."
DATABASE_URL = "Enter your Postgres URL."
DATABASE_PORT = 5432
DATABASE_PASSWORD = "Enter your database password."

# App Settings
SOURCE_ACCOUNT = ""  # The account you'll be using to train the database.
DESTINATION_ACCOUNT = ""  # The account you'll be posting tweets to.

TWEET_DATA_FILE = 'data/tweets.csv'  # The Twitter archive you'll be initially training with.
CLEAN_DATA_FILE = 'data/cleaned_tweet_data.txt'  # The location you want to save the clean data file.
BOT_DATA_FILE = 'data/bot_data.json'  # The location you want to save the bot's JSON data file.

TWEET_ODDS = 1  # The odds of tweeting each interval, calculated as 1 : TWEET_ODDS.
DEBUG = True  # Whether to show detailed debug information.
LIVE_TWEET = False  # Whether to actually post tweets to the account.
