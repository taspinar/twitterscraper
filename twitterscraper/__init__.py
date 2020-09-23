# TwitterScraper
# Copyright 2016-2020 Ahmet Taspinar
# See LICENSE for details.
"""
Twitter Scraper tool
"""

__version__ = '1.6.1'
__author__ = 'Ahmet Taspinar'
__license__ = 'MIT'


from twitterscraper.query import query_tweets, query_tweets_from_user, query_user_info
from twitterscraper.query_js import get_user_data, get_query_data
from twitterscraper.user import User
