"""
Setup the application with your Twitter archive file.
"""
import pandas as pd
import json
import logging

import config
from twitterbot import TwitterBot
from markov import Markov

if config.DEBUG is True:
    logging.basicConfig(level=logging.DEBUG)


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
    logging.info("Connecting to the database.")
    markov_bot._connect_db()
    table_exists = markov_bot.cur.execute(
        """
        SELECT EXISTS(SELECT 1 FROM information_schema.tables \
        WHERE table_catalog=%(db_name)s \
        AND table_schema='public' \
        AND table_name='transition');
        """,
        {'db_name': config.DATABASE_NAME}
    )
    if not table_exists:
        logging.info("Transition table does not exist.  Creating it now...")
        markov_bot.cur.execute(
            """
            CREATE TABLE transition ( \
            first_word VARCHAR, \
            second_word VARCHAR, \
            result_word VARCHAR, \
            frequency INTEGER, \
            beginning BOOLEAN, \
            PRIMARY KEY(first_word, second_word, result_word) \
            );
            """
        )
    markov_bot.conn.commit()
    markov_bot._disconnect_db()

    logging.info("Cleaning up Twitter data.")
    dataframe = pd.read_csv(tweet_data)
    with open(clean_data, 'r+') as f:
        for line in dataframe.text.iteritems():
            f.write(TwitterBot.clean_data(line[1] + "\n"))

    logging.info("Training the database.")
    gen = generate_word(clean_data)
    markov_bot.update_db(gen)

    with open(bot_data, 'w') as f:
        last_id_seen = int(dataframe.tweet_id[0])
        logging.info("Dumping last id seen to json: " + str(last_id_seen))
        json.dump({"last_id_seen": last_id_seen}, f)
