#!/usr/bin/env
import psycopg2

import testconfig


CLAUSE_ENDS = ['.', ',', '?', '!', ':', ';']


class Markov(object):
    """
    The core Markov Bot class.
    It includes methods for constructing and using the transition matrix.
    """

    def __init__(self):
        self.conn = None
        self.cur = None

    def _connect_db(self):
        """
        Return a connection to the database.
        """
        try:
            self.conn = psycopg2.connect(dbname=testconfig.DATABASE_NAME, user=testconfig.DATABASE_USER)
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            print(e, "Could not connect to database.", sep='\n')

    def _disconnect_db(self):
        """
        Close the connection to database.
        """
        self.cur.close()
        self.conn.close()

    def update_db(self, word_gen):
        """
        Update the transition matrix database with the most recent tweet data.
        """
        self._connect_db()

        # Add the row if it doesn't exist, else iterate the frequency counter by 1
        upsert_db = """
                    INSERT INTO transition (first_word, second_word, result_word, frequency) \
                    VALUES (%(first)s, %(second)s, %(result)s, 1) \
                    ON CONFLICT (first_word, second_word) DO UPDATE \
                    SET frequency = transition.frequency + 1
                    """

        # Iterate over the words in the training corpus
        first, second, result = next(word_gen), next(word_gen), next(word_gen)
        self.cur.execute(upsert_db, {'first': first, 'second': second, 'result': result})

        for word in word_gen:
            first, second, result = second, result, word
            self.cur.execute(upsert_db, {'first': first, 'second': second, 'result': result})

        self.conn.commit()
        self._disconnect_db()

    def generate_sentence(self):
        """
        Generate a new sentence using the transition matrix.
        """
        pass
