"""
Train the database with the tweet column of your Twitter archive.
"""
from twitterbot import TwitterBot
from markov import Markov


tweet_data = 'data/tweet_data.txt'
clean_data = 'data/cleaned_tweet_data.txt'
markov_bot = Markov()


def generate_word(data_file):
    with open(data_file, 'r') as f:
        for line in f:
            for word in line.split():
                yield word


if __name__ == '__main__':
    with open(clean_data, 'w') as f1:
        with open(tweet_data, 'r') as f2:
            f1.write(TwitterBot.clean_data(f2.read()))
    gen = generate_word(clean_data)
    # markov_bot.update_db(gen)
    for _ in range(10):
        print(markov_bot.generate_sentence())
        print('******')
