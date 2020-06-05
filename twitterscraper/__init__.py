# TwitterScraper
# Copyright 2016-2019 Ahmet Taspinar
# See LICENSE for details.
"""
Twitter Scraper tool
"""

__version__ = '1.4.0'
__author__ = 'Ahmet Taspinar'
__license__ = 'MIT'


from twitterscraper.query_js import get_user_data, get_query_data
from twitterscraper.user import User
from twitterscraper.ts_logger import logger as ts_logger
