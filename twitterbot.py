from markov import Markov
import psycopg2
import re
import config


bot = Markov()


class TwitterBot(object):
    """
    The TwitterBot class.
    This contains methods for connecting to the Twitter API to interact with the bot account.
    """
    def __init__(self):
        pass

    def _connect_api(self):
        """
        Returns a connection to the Twitter API.
        """
        pass

    @staticmethod
    def clean_data(tweet_data):
        """
        Clean the Twitter data and space it into single-spaced clauses with no linebreaks
        """
        tweet_data = re.sub(r'\b(RT) .+', '', tweet_data) # Retweets
        tweet_data = re.sub(r'\S*(@|\#|(http)|(www\.))\S+', '', tweet_data) # URLs, emails, hashtags, usernames
        tweet_data = re.sub(r'\(\)', '', tweet_data) # Misc junk
        tweet_data = re.sub(r'\s+', ' ', tweet_data) # Replace whitespace with single spaces
        return tweet_data


if __name__ == 'main':
    pass
    