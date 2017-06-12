#!/usr/bin/env
import json
import logging
import random
import re
import twitter

import config
from markov import Markov

if config.DEBUG is True:
    logging.basicConfig(level=logging.DEBUG)

bot_data = 'data/bot_data.json'


class TwitterBot(object):
    """
    The TwitterBot class.
    This contains methods for connecting to the Twitter API to interact with the bot account.
    """
    def __init__(self):
        self.markov = Markov()
        self.api = None
        self.last_id_seen = None
        self.last_reply_id_seen = None
        self.last_mention_id_seen = None

        try:
            with open(bot_data, 'r') as f:
                id_data = json.load(f)
                self.last_id_seen = id_data['last_id_seen']
                self.last_reply_id_seen = id_data['last_reply_id_seen']
                self.last_mention_id_seen = id_data['last_mention_id_seen']
        except FileNotFoundError as e:
            print(e, "Could not find bot_data file.  Have you run the setup script yet?", sep='')

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
        except twitter.error.TwitterError as e:
            print(e, "\nCould not connect to the Twitter API.  Check you config file credentials.")

    def _dump_data(self):
        """
        Dump tweet id data to json.
        """
        with open(bot_data, 'w') as f:
            logging.info("Dumping last id seen to json: " + str(self.last_id_seen))
            logging.info("Dumping reply last id seen to json: " + str(self.last_reply_id_seen))
            logging.info("Dumping mention last id seen to json: " + str(self.last_mention_id_seen))
            json.dump({"last_id_seen": self.last_id_seen,
                       "last_reply_id_seen": self.last_reply_id_seen,
                       "last_mention_id_seen": self.last_mention_id_seen}, f)

    def compose_tweet(self, debug=False):
        """
        Compose and post a tweet.
        """
        if self.api is None:
            self._connect_api()

        tweet = ""

        def add_sentence(tweet):
            """
            Add another sentence.
            """
            while True:
                test_sentence = self.markov.generate_sentence()
                if len(tweet + " " + test_sentence) <= 140:
                    return test_sentence

        # Generate the first sentence
        tweet = tweet + " " + add_sentence(tweet)

        # If there's room, have a chance at adding a second sentence
        if len(tweet) < 70 and random.random() < 0.65:
            logging.info("Adding another sentence")
            tweet = tweet + " " + add_sentence(tweet)

            # Sometimes add one more.
            if len(tweet) < 90 and random.random() < 0.25:
                tweet = tweet + " " + add_sentence(tweet)

        # Randomly capitalize a short tweet
        if len(tweet) < 60 and random.random() < 0.35:
            tweet = tweet.upper()

        # IDEA: Add a parameter to pass markov.generate_sentence() a set beginning.
        #       Use this to sometimes generate RP-type messages​

        if debug:
            logging.debug("Debug Enabled. Returning tweet without posting.")
            return tweet

        status = self.api.PostUpdate(tweet)
        print(status.text.encode('utf-8'))

    def get_tweets(self):
        """
        Get the most recent tweets and update the last ID seen.
        """
        if self.api is None:
            self._connect_api()
        tweets = self.api.GetUserTimeline(screen_name=config.SOURCE_ACCOUNT,
                                          since_id=self.last_id_seen,
                                          trim_user=True)
        if tweets:
            self.last_id_seen = tweets[0].id
            logging.info("Setting last_id_seen to: " + str(self.last_id_seen))
            self._dump_data()
        return tweets

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
            logging.info("Database is up to date with the latest ID seen.")
            return

        self.last_id_seen = tweets[0].id
        logging.info("Setting last_id_seen to: " + str(self.last_id_seen))
        self._dump_data()

        def _tweet_data_gen(tweets):
            for status in tweets:
                tweet = self.clean_data(status.text)
                for word in tweet.split():
                    yield word

        self.markov.update_db(_tweet_data_gen(tweets))

    def reply_tweets(self):
        """
        Get all replies and mentions and respond to them.
        """
        if self.api is None:
            self._connect_api()
        replies = self.api.GetReplies(since_id=self.last_reply_id_seen)
        mentions = self.api.GetMentions(since_id=self.last_mention_id_seen)

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


if __name__ == "__main__":
    bot = TwitterBot()
    bot.update_tweet_database()
    print(bot.compose_tweet(debug=True))
