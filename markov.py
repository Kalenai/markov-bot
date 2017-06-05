#!/usr/bin/env
import numpy as np
import psycopg2

import testconfig


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
                dbname=testconfig.DATABASE_NAME,
                user=testconfig.DATABASE_USER
                )
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            print(e, "Could not connect to database.", sep='\n')

    def _disconnect_db(self):
        """
        Close the connection to database.
        """
        self.cur.close()
        self.conn.close()

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

    def generate_sentence(self):
        """
        Generate a new sentence using the transition matrix.
        """
        self._connect_db()

        sentence = []

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

            # Convert the frequencies into probability for numpy
            probs_sum = sum(probs)
            for index, num in enumerate(probs):
                probs[index] = num / probs_sum

            # Choose the next word and add it to the sentence
            next_word = np.random.choice(words, p=probs)
            sentence.append(next_word)

        self._disconnect_db()
        return ' '.join(sentence)
