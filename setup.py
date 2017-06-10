"""
Setup the application with your Twitter archive file.
"""
import pandas as pd
import json

from twitterbot import TwitterBot
from markov import Markov


tweet_data = 'data/tweets.csv'
clean_data = 'data/cleaned_tweet_data.txt'
bot_data = 'data/bot_data.json'

markov_bot = Markov()


def generate_word(clean_data):
    with open(clean_data, 'r') as f:
        for line in f:
            for word in line.split():
                yield word


if __name__ == '__main__':
    # TODO: Add checks to see if the database and table is created yet

    dataframe = pd.read_csv(tweet_data)
    with open(clean_data, 'r+') as f:
        for line in dataframe.text.iteritems():
            f.write(TwitterBot.clean_data(line[1] + "\n"))
    gen = generate_word(clean_data)
    # markov_bot.update_db(gen)

    with open(bot_data, 'w') as f:
        json.dump({"last_id_seen": int(dataframe.tweet_id[0])}, f)
