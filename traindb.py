"""
Train the database with the tweet column of your Twitter archive.
"""
from bot import TwitterBot


if __name__ == '__main__':
    with open('data/test_tweet_data.txt', 'r') as f1:
        with open('data/cleaned_tweet_data.txt', 'w') as f2:
            f2.write(TwitterBot.clean_data(f1.read()))
