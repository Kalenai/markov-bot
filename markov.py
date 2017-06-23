#!/usr/bin/env
import logging
import psycopg2
import random

import config

markov_logger = logging.getLogger('twitterbot.markov')


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
            markov_logger.debug("Connection successful: %s", self.conn)
        except (psycopg2.Error, psycopg2.OperationalError) as error:
            markov_logger.error("Could not connect to database.",
                                exc_info=error)
            raise error

    def _disconnect_db(self):
        """
        Close the connection to database.
        """
        self.cur.close()
        self.conn.close()
        markov_logger.debug("Disconnected from database: %s", self.conn)

    def _is_sentence_end(self, word):
        """
        Wrapper to detect if a word contains a sentence end.
        """
        return not self.SENTENCE_ENDS.isdisjoint(word)

    def update_db(self, word_gen):
        """
        Update the transition matrix database with the most recent data.
        Returns 'None' if it fails to generate a sentence.
        """
        self._connect_db()

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

        markov_logger.debug("Current beginning:" + str(begin))
        sentence.append(begin[0])
        sentence.append(begin[1])

        # Loop to choose next word in the sentence
        while True:
            # Break and return the sentence if the last word contains a sentence end
            if self._is_sentence_end(sentence[-1]):
                break

            if len(sentence) > 100:
                markov_logger.warning("Sentence getting too long without returning.  Returning 'None'.")
                return None

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

            # Break out of the loop and return 'None' if no words retrieved
            if words == [] or probs == []:
                markov_logger.warning("Unable to find next word in the sentence.  Returning 'None'.")
                return None

            # Convert the frequencies into probabilities
            probs_sum = sum(probs)
            for index, num in enumerate(probs):
                probs[index] = num / probs_sum

            # Choose the next word and add it to the sentence
            choice = random.random()
            final_word = words[-1]
            for word, prob in zip(words, probs):
                choice -= prob
                if choice <= 0 or word == final_word:
                    next_word = word

            markov_logger.debug("Adding next word:" + str(next_word))
            sentence.append(next_word)

        self._disconnect_db()
        return ' '.join(sentence)
