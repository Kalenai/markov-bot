#!/usr/bin/env
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
else:
    logging.basicConfig(level=logging.INFO)

tweet_data_file = 'data/tweets.csv'
clean_data_file = 'data/cleaned_tweet_data.txt'
bot_data_file = 'data/bot_data.json'

markov = Markov()
twitterbot = TwitterBot()


def generate_word(clean_data):
    with open(clean_data_file, 'r') as f:
        for line in f:
            for word in line.split():
                yield word


if __name__ == '__main__':
    logging.info("Connecting to the database.")
    markov._connect_db()
    markov.cur.execute(
        """
        SELECT EXISTS(SELECT 1 FROM information_schema.tables \
        WHERE table_catalog=%(db_name)s \
        AND table_schema='public' \
        AND table_name='transition');
        """,
        {'db_name': config.DATABASE_NAME}
    )
    table_exists = markov.cur.fetchone()[0]

    if not table_exists:
        logging.info("Transition table does not exist.  Creating it now...")
        markov.cur.execute(
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
    markov.conn.commit()
    markov._disconnect_db()

    logging.info("Cleaning up Twitter data.")
    dataframe = pd.read_csv(tweet_data_file)
    with open(clean_data_file, 'r+') as f:
        for line in dataframe.text.iteritems():
            f.write(twitterbot.clean_data(line[1] + "\n"))

    logging.info("Training the database.")
    gen = generate_word(clean_data_file)
    markov.update_db(gen)

    twitterbot._connect_api()
    last_id_seen = int(dataframe.tweet_id[0])
    replies = twitterbot.api.GetMentions()
    if replies is not None:
        last_reply_id_seen = replies[0].id
    else:
        last_reply_id_seen = None
    twitterbot.last_id_seen, twitterbot.last_reply_id_seen = last_id_seen, last_reply_id_seen
    twitterbot.dump_data()
