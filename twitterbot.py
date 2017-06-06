#!/usr/bin/env
import re
import twitter

import config
from markov import Markov

markov_bot = Markov()


class TwitterBot(object):
    """
    The TwitterBot class.
    This contains methods for connecting to the Twitter API to interact with the bot account.
    """
    def __init__(self):
        self.api = None
        self.last_id_seen = None

    def _connect_api(self):
        """
        Establish a connection to the Twitter API.
        """
        self.api = twitter.Api(consumer_key=config.CONSUMER_KEY,
                               consumer_secret=config.CONSUMER_SECRET,
                               access_token_key=config.ACCESS_TOKEN_KEY,
                               access_token_secret=config.ACCESS_TOKEN_SECRET)

    def get_tweets(self):
        """
        Get the most recent tweets, add them to the queue file, and update the last ID seen.
        """
        pass

    def compose_tweet(self):
        """
        Compose and post a tweet.
        """
        pass

    @staticmethod
    def clean_data(tweet_data):
        """
        Clean the Twitter data and space it into single-spaced clauses with no linebreaks
        """
        tweet_data = re.sub(r'\b(RT) .+', '', tweet_data)  # Retweets
        tweet_data = re.sub(r'\S*(@|\#|(http)|(www\.))\S+', '', tweet_data)  # URLs, emails, hashtags, usernames
        tweet_data = re.sub(r'\(\)', '', tweet_data)  # Misc junk
        tweet_data = re.sub(r'&gt;', '>', tweet_data)  # Fix > signs
        tweet_data = re.sub(r'&lt;', '<', tweet_data)  # Fix < signs
        tweet_data = re.sub(r'&amp;', '&', tweet_data)  # Fix ampersands
        tweet_data = re.sub(r' +', ' ', tweet_data)  # Single space it all
        tweet_data = re.sub(r'\n+', '\n', tweet_data)  # Extra newlines
        tweet_data = re.sub(r'[\t\r\f]*', '', tweet_data)  # Extra whitespace
        tweet_data = re.sub(r'^ ', '', tweet_data, flags=re.MULTILINE)  # Leading spaces
        return tweet_data


if __name__ == 'main':
    pass
