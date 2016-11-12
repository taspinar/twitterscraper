"""
This is a command line application that allows you to scrape twitter!
"""

from argparse import ArgumentParser
from os.path import isfile
from json import dump
import logging

from twitterscraper import query_tweets


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    try:
        parser = ArgumentParser(
            description=__doc__
        )

        parser.add_argument("query", type=str, help="Advanced twitter query")
        parser.add_argument("-o", "--output", type=str, default="tweets.json",
                            help="Path to a JSON file to store the gathered "
                                 "tweets to.")
        parser.add_argument("-l", "--limit", type=int, default=None,
                            help="Number of minimum tweets to gather.")
        args = parser.parse_args()

        if isfile(args.output):
            logging.error("Output file already exists! Aborting.")
            exit(-1)

        tweets = query_tweets(args.query, args.limit)
        with open(args.output, "w") as output:
            dump(tweets, output)
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Quitting...")
