import config
import twitterbot
import logging
from random import randrange

logger = logging.getLogger()

if config.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


def handler(context, event):
    """
    The handler function to be used by AWS Lambda.
    """
    logger.info("Got event: %s", event)
    # Initialize the bot and update the database with any new tweets.
    logger.info("Initializing TwitterBot")
    bot = twitterbot.TwitterBot()
    logger.info("Updating tweet database.")
    bot.update_tweet_database()

    # Have a chance at posting a new tweet.
    roll = randrange(config.TWEET_ODDS)
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
