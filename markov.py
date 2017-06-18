#!/usr/bin/env
import logging
import psycopg2
import random

import config


class Markov(object):
    """
    The core Markov Bot class.
    It includes methods for constructing and using the transition matrix.
    """

    SENTENCE_ENDS = {'.', '?', '!'}

    def __init__(self):
        self.conn = None
        self.cur = None

    def _connect_db(self):
        """
        Return a connection to the database.
        """
        try:
            self.conn = psycopg2.connect(
                dbname=config.DATABASE_NAME,
                user=config.DATABASE_USER,
                password=config.DATABASE_PASSWORD,
                host=config.DATABASE_URL,
                port=config.DATABASE_PORT
                )
            self.cur = self.conn.cursor()
            logging.debug("Connection successful: %s", self.conn)
        except psycopg2.Error as e:
            print(e, "Could not connect to database.", sep='')

    def _disconnect_db(self):
        """
        Close the connection to database.
        """
        self.cur.close()
        self.conn.close()
        logging.debug("Disconnected from database: %s", self.conn)

    def _is_sentence_end(self, word):
        """
        Wrapper to detect if a word contains a sentence end.
        """
        return not self.SENTENCE_ENDS.isdisjoint(word)

    def update_db(self, word_gen):
        """
        Update the transition matrix database with the most recent data.
        """
        self._connect_db()
        if self.conn is None or self.cur is None:
            logging.error("Was not able to establish connection to the database. Check your config file.")
            return

        # Add the row if it doesn't exist, else iterate the frequency counter by 1
        upsert_db = """
                    INSERT INTO transition (first_word, second_word, result_word, frequency, beginning) \
                    VALUES (%(first)s, %(second)s, %(result)s, 1, %(beginning)s) \
                    ON CONFLICT (first_word, second_word, result_word) DO UPDATE \
                    SET frequency = transition.frequency + 1;
                    """

        # Iterate over the words in the training corpus
        first, second, result = next(word_gen), next(word_gen), next(word_gen)
        beginning = True
        self.cur.execute(upsert_db, {
            'first': first,
            'second': second,
            'result': result,
            'beginning': beginning
            })
        beginning = False

        for word in word_gen:
            if self._is_sentence_end(first):
                beginning = True
            first, second, result = second, result, word
            self.cur.execute(upsert_db, {
                'first': first,
                'second': second,
                'result': result,
                'beginning': beginning
                })
            beginning = False

        self.conn.commit()
        self._disconnect_db()

    def generate_sentence(self, beginning=None):
        """
        Generate a new sentence using the transition matrix.
        """
        self._connect_db()

        sentence = []

        if beginning is None:
            # Choose a starting pair of words.
            self.cur.execute(
                """
                SELECT first_word, second_word \
                FROM transition \
                WHERE beginning = True \
                ORDER BY RANDOM() \
                LIMIT 1;
                """
            )
            begin = self.cur.fetchone()

        logging.debug("Current beginning:" + str(begin))
        print(begin)
        sentence.append(begin[0])
        sentence.append(begin[1])

        # Loop to choose next word in the sentence
        while True:
            # Break and return the sentence if the last word contains a sentence end
            if self._is_sentence_end(sentence[-1]):
                break

            # Query the database for possible next words and their frequencies
            self.cur.execute(
                """
                SELECT result_word, frequency \
                FROM transition
                WHERE first_word = %(first)s AND second_word = %(second)s;
                """,
                {'first': sentence[-2],
                 'second': sentence[-1]}
                )
            words, probs = zip(*self.cur.fetchall())
            words = list(words)
            probs = list(probs)
            print("Probs before conversion: " + str(probs))

            # Convert the frequencies into probabilities
            probs_sum = sum(probs)
            for index, num in enumerate(probs):
                probs[index] = num / probs_sum

            print(words)
            print(probs)

            # Choose the next word and add it to the sentence
            choice = random.random()
            final_word = words[-1]
            for word, prob in zip(words, probs):
                choice -= prob
                if choice <= 0 or word == final_word:
                    next_word = word

            logging.debug("Adding next word:" + str(next_word))
            sentence.append(next_word)

        self._disconnect_db()
        return ' '.join(sentence)
