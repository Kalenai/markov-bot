## What is this?
This is my own version of a Twitter bot, using Markov Chains to create tweets
and post them to a Twitter account.

You can see an example of it running at https://twitter.com/kalenai_ebawks.

## Setup
This bot is designed to be run simply on a timer of some sort, such as a cron job.
Here are the basic steps to get it up and running:
1. Make sure your environment is setup to run Python 3 files and install everything from requirements.txt.
2. Start up a PostgreSQL database, if you don't already have one running.
3. Create an account for your Twitterbot.
4. Make a new Twitter app for your bot account on https://apps.twitter.com/.
5. Enter the necessary information in the config.py file.  
6. Download your full Twitter archive from the source account and place the tweets.csv file in the data folder.
7. Run the bot_setup.py file to build your transition matrix table and initially train your database.
8. Run your bot by running twitterbot.py.
9. Make sure you set LIVE_TWEET in the config to True once you're ready to start actually posting!

## Contributing and Feedback
This is my first larger project I've built from scratch.  I learned a lot and feel like it's 
fairly solid, but I would love to hear any feedback or suggestions!