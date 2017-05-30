#!/usr/bin/env
import config
import psycopg2


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
            self.conn = psycopg2.connect(dbname=config.DATABASE_URL)
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            print(e, "Could not connect to database.", sep='\n')

    def _disconnect_db(self):
        """
        Close the connection to database.
        """
        self.cur.close()
        self.conn.close()

    def update_db(self):
        """
        Update the transition matrix database with the most recent tweet data.
        """
        pass

    def generate_sentence(self):
        """
        Generate a new sentence using the transition matrix.
        """
        pass
