# -*- coding: utf-8 -*-
"""
Created on Thu May 24 11:53:26 2018

@author: Nilesh Jorwar
"""

import sys
import json
import logging
import collections
import datetime as dt
from os.path import isfile
from twitterscraper.query import query_tweets
import csv

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        elif isinstance(obj, collections.Iterable):
            return list(obj)
        elif isinstance(obj, dt.datetime):
            return obj.isoformat()
        elif hasattr(obj, '__getitem__') and hasattr(obj, 'keys'):
            return dict(obj)
        elif hasattr(obj, '__dict__'):
            return {member: getattr(obj, member)
                    for member in dir(obj)
                    if not member.startswith('_') and
                    not hasattr(getattr(obj, member), '__call__')}

        return json.JSONEncoder.default(self, obj)

def valid_date(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        print(msg)

def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    try:
# =============================================================================
#         #query1=company[1]
#         query1='amazon'
#         limit1=1000
#         begindateString = '2006-03-21'
#         begindate1=valid_date(begindateString)
#         enddate1=dt.date.today()
#         poolsize1=20
#         lang1=None
#         output=query1+'.json'
#         tweets = query_tweets(query = query1, limit = limit1,begindate = begindate1, enddate = enddate1,poolsize = poolsize1, lang = lang1)
#
#         if tweets:
#             with open(output, "w") as output:
#                 json.dump(tweets, output, cls=JSONEncoder)
#
# =============================================================================
         with open('coname_twitter_account_users.csv', 'r',newline='') as myFile:
             readInput=csv.reader(myFile)
             for i,company in enumerate(readInput):
                 if i > 0 and company[1]:
                     print(company[1])
                     output=company[1]+'.json'
                     if isfile(output):
                         logging.error("Output file already exists! Aborting.")
                         #continue
                         sys.exit(-1)
                     query1=company[1]
                     #query1='amazon'
                     limit1=100000
                     begindateString = '2006-03-21'
                     begindate1=valid_date(begindateString)
                     enddate1=dt.date.today()
                     poolsize1=20
                     lang1='en'

                     tweets = query_tweets(query = query1, limit = limit1,
                                           begindate = begindate1, enddate = enddate1,
                                           poolsize = poolsize1, lang = lang1)

                     if tweets:
                         with open(output, "w") as output:
                             json.dump(tweets, output, cls=JSONEncoder)

    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Quitting...")


if __name__ == "__main__":
    # calling main function
    main()
