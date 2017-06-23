#!/usr/bin/env
import json
import logging
import random
import re
import time
import twitter

import config
import markov


# Setup logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
twitterbot_logger = logging.getLogger('twitterbot')
twitterbot_logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('{0}twitterbot_log_{1}.log'.format(config.LOG_DIRECTORY, time.strftime("%Y_%m_%d")))
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
twitterbot_logger.addHandler(fh)

ch = logging.StreamHandler()
if config.DEBUG:
    ch.setLevel(logging.DEBUG)
else:
    ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
twitterbot_logger.addHandler(ch)


# The JSON dump file for last IDs seen.
bot_data_file = config.BOT_DATA_FILE


class TwitterBot(object):
    """
    The TwitterBot class.
    This contains methods for connecting to the Twitter API to interact with the bot account.
    """
    def __init__(self):
        self.markov = markov.Markov()
        self.api = None
        self.last_id_seen = None
        self.last_reply_id_seen = None

        # Attempt to collect the last IDs seen from the JSON dump file.
        try:
            with open(bot_data_file, 'r') as f:
                id_data = json.load(f)
                self.last_id_seen = id_data['last_id_seen']
                self.last_reply_id_seen = id_data['last_reply_id_seen']
        except FileNotFoundError as error:
            twitterbot_logger.error("Could not find bot_data file.  Have you run the setup script yet?",
                                    exc_info=error)
            raise error

    def _connect_api(self):
        """
        Establish a connection to the Twitter API.
        """
        try:
            self.api = twitter.Api(consumer_key=config.CONSUMER_KEY,
                                   consumer_secret=config.CONSUMER_SECRET,
                                   access_token_key=config.ACCESS_TOKEN_KEY,
                                   access_token_secret=config.ACCESS_TOKEN_SECRET)
            return self.api.VerifyCredentials()
        except twitter.error.TwitterError as error:
            twitterbot_logger.error("Could not connect to the Twitter API.  Check you config file credentials.",
                                    exc_info=error)
            raise error

    def _compose_tweet(self):
        """
        Compose and return a tweet.
        """
        tweet = ""

        def _add_sentence(tweet):
            """
            Add another sentence.
            """
            fail_count = 0
            while fail_count <= 3:
                test_sentence = self.markov.generate_sentence()
                if test_sentence is None:
                    fail_count += 1
                    twitterbot_logger.warning("No test sentence returned.  Trying again.")
                elif len(tweet + " " + test_sentence) <= 140:
                    return test_sentence
            twitterbot_logger.warning("Failed to generate a sentence!")
            raise RuntimeError("Unable to generate sentences.")

        # Generate the first sentence
        tweet = tweet + " " + _add_sentence(tweet)

        # If there's room, have a chance at adding a second sentence
        if len(tweet) < 70 and random.random() < 0.65:
            twitterbot_logger.info("Adding another sentence")
            tweet = tweet + " " + _add_sentence(tweet)

            # Sometimes add one more.
            if len(tweet) < 90 and random.random() < 0.25:
                tweet = tweet + " " + _add_sentence(tweet)

        # Randomly capitalize a short tweet
        if len(tweet) < 60 and random.random() < 0.35:
            tweet = tweet.upper()

        return tweet

    def _post_tweet(self, status, reply_to=None, live_tweet=config.LIVE_TWEET):
        """
        Post a status to Twitter.
        """
        # Create a connection to the API if there isn't one already
        if self.api is None:
            self._connect_api()

        # Return the tweet text without posting it
        if not live_tweet:
            twitterbot_logger.info("Live tweeting disabled. Returning tweet without posting.")
            twitterbot_logger.info("Unposted status: %s", status)
            return status

        status = self.api.PostUpdate(status, in_reply_to_status_id=reply_to)
        twitterbot_logger.info(status.text.encode('utf-8'))

    @staticmethod
    def clean_data(tweet_data):
        """
        Clean the Twitter data and space it into single-spaced clauses with no linebreaks
        """
        tweet_data = re.sub(r'\b(RT) .+', '', tweet_data)  # Retweets
        tweet_data = re.sub(r'\S*(@|\#|(http)|(www\.))\S+', '', tweet_data)  # URLs, emails, hashtags, usernames
        tweet_data = re.sub(r'\(\)|\"', '', tweet_data)  # Misc junk
        tweet_data = re.sub(r'&gt;', '>', tweet_data)  # Fix > signs
        tweet_data = re.sub(r'&lt;', '<', tweet_data)  # Fix < signs
        tweet_data = re.sub(r'&amp;', '&', tweet_data)  # Fix ampersands
        tweet_data = re.sub(r' +', ' ', tweet_data)  # Single space it all
        tweet_data = re.sub(r'\n+', '\n', tweet_data)  # Extra newlines
        tweet_data = re.sub(r'[\t\r\f]*', '', tweet_data)  # Extra whitespace
        tweet_data = re.sub(r'^ ', '', tweet_data, flags=re.MULTILINE)  # Leading spaces
        return tweet_data

    def dump_data(self):
        """
        Dump tweet ID data to json.
        """
        with open(bot_data_file, 'w') as file:
            twitterbot_logger.info("Dumping last id seen to json: %s", self.last_id_seen)
            twitterbot_logger.info("Dumping reply last id seen to json: %s", self.last_reply_id_seen)
            json.dump({"last_id_seen": self.last_id_seen,
                       "last_reply_id_seen": self.last_reply_id_seen}, file)

    def new_tweet(self):
        """
        Compose and post a new tweet.
        """
        tweet = self._compose_tweet()
        self._post_tweet(tweet)

    def reply_tweets(self):
        """
        Get all replies and mentions and respond to them.
        """
        # Create a connection to the API if there isn't one already
        if self.api is None:
            self._connect_api()

        # Get any new replies or mentions
        replies = self.api.GetMentions(since_id=self.last_reply_id_seen)
        twitterbot_logger.info(replies)

        # Return None if there are no new replies
        if replies == []:
            twitterbot_logger.info("No new replies to respond to.")
            return replies

        # Update the bot with the latest reply ID seen
        self.last_reply_id_seen = replies[0].id

        # Post a response to each reply
        for reply in replies:
            tweet = self._compose_tweet()
            twitterbot_logger.info("Replying to tweet ID: %s", reply.id)
            if tweet:
                self._post_tweet(tweet, reply_to=reply.id)
            else:
                twitterbot_logger.warning("Unable to successfully generate a tweet to post.")

    def update_tweet_database(self):

        """
        Have the markov bot update its database with the most recent tweets.
        """
        if self.api is None:
            self._connect_api()
        tweets = self.api.GetUserTimeline(screen_name=config.SOURCE_ACCOUNT,
                                          since_id=self.last_id_seen,
                                          trim_user=True)

        if not tweets:
            twitterbot_logger.info("Database is up to date with the latest ID seen.")
            return

        self.last_id_seen = tweets[0].id
        twitterbot_logger.info("Setting last_id_seen to: %s", self.last_id_seen)

        def _tweet_data_gen(tweets):
            for status in tweets:
                tweet = self.clean_data(status.text)
                for word in tweet.split():
                    yield word

        self.markov.update_db(_tweet_data_gen(tweets))

if __name__ == "__main__":
    twitterbot_logger.info("Running TwitterBot.  Current time is %s", time.strftime("%H:%M:%S"))
    # Initialize the bot and update the database with any new tweets.
    twitterbot_logger.info("Initializing TwitterBot")
    bot = TwitterBot()
    twitterbot_logger.info("Updating tweet database.")
    bot.update_tweet_database()

    # Have a chance at posting a new tweet.
    roll = random.randrange(config.TWEET_ODDS)
    if roll == 0:
        twitterbot_logger.info("Rolled %s. Posting a new tweet", roll)
        bot.new_tweet()
    else:
        twitterbot_logger.info("Rolled %s. Not posting this time.", roll)

    # Respond to any recent replies or mentions.
    twitterbot_logger.info("Responding to new tweets and mentions.")
    bot.reply_tweets()

    # Dump update information to JSON.
    twitterbot_logger.info("Dumping bot data to JSON")
    bot.dump_data()

    twitterbot_logger.info("All finished.")
