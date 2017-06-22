import logging
import random

import config
import twitterbot

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Initialize the bot and update the database with any new tweets.
logger.info("Initializing TwitterBot")
print("jiggity")
bot = twitterbot.TwitterBot()
logger.info("Updating tweet database.")
# bot.update_tweet_database()

# Have a chance at posting a new tweet.
roll = random.randrange(config.TWEET_ODDS)
if roll == 0:
    logger.info("Rolled %s. Posting a new tweet", roll)
    bot.new_tweet()
else:
    logger.info("Rolled %s. Not posting this time.", roll)

# Respond to any recent replies or mentions.
logger.info("Responding to new tweets and mentions.")
bot.reply_tweets()

# Dump update information to JSON.
logger.info("Dumping bot data to JSON")
bot.dump_data()

logger.info("All finished.")
