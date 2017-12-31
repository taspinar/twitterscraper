"""
This is a command line application that allows you to scrape twitter!
"""
import json
import logging
import argparse
import collections
import datetime as dt
from os.path import isfile
from twitterscraper.query import query_tweets

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
        raise argparse.ArgumentTypeError(msg)

def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    try:
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
            description=__doc__
        )

        parser.add_argument("query", type=str, help="Advanced twitter query")
        parser.add_argument("-o", "--output", type=str, default="tweets.json",
                            help="Path to a JSON file to store the gathered "
                                 "tweets to.")
        parser.add_argument("-l", "--limit", type=int, default=None,
                            help="Number of minimum tweets to gather.")
        parser.add_argument("-a", "--all", action='store_true',
                            help="Set this flag if you want to get all tweets "
                                 "in the history of twitter. Begindate is set to 2006-03-01."
                                 "This may take a while. You can increase the number of parallel"
                                 "processes depending on the computational power you have.")
        parser.add_argument("--lang", type=str, default=None,
                            help="Set this flag if you want to query tweets in \na specific language. You can choose from:\n"
                                 "en (English)\nar (Arabic)\nbn (Bengali)\n"
                                 "cs (Czech)\nda (Danish)\nde (German)\nel (Greek)\nes (Spanish)\n"
                                 "fa (Persian)\nfi (Finnish)\nfil (Filipino)\nfr (French)\n"
                                 "he (Hebrew)\nhi (Hindi)\nhu (Hungarian)\n"
                                 "id (Indonesian)\nit (Italian)\nja (Japanese)\n"
                                 "ko (Korean)\nmsa (Malay)\nnl (Dutch)\n"
                                 "no (Norwegian)\npl (Polish)\npt (Portuguese)\n"
                                 "ro (Romanian)\nru (Russian)\nsv (Swedish)\n"
                                 "th (Thai)\ntr (Turkish)\nuk (Ukranian)\n"
                                 "ur (Urdu)\nvi (Vietnamese)\n"
                                 "zh-cn (Chinese Simplified)\n"
                                 "zh-tw (Chinese Traditional)"
                                 )
        parser.add_argument("-d", "--dump", action="store_true", 
                            help="Set this flag if you want to dump the tweets \nto the console rather than outputting to a file")
        parser.add_argument("-bd", "--begindate", type=valid_date, default="2017-01-01",
                            help="Scrape for tweets starting from this date. Format YYYY-MM-DD. \nDefault value is 2017-01-01", metavar='\b')
        parser.add_argument("-ed", "--enddate", type=valid_date, default=dt.date.today(),
                            help="Scrape for tweets until this date. Format YYYY-MM-DD. \nDefault value is the date of today.", metavar='\b')
        parser.add_argument("-p", "--poolsize", type=int, default=20, help="Specify the number of parallel process you want to run. \n"
                            "Default value is set to 20. \nYou can change this number if you have more computing power available. \n"
                            "Set to 1 if you dont want to run any parallel processes.", metavar='\b')
        args = parser.parse_args()

        if isfile(args.output) and not args.dump:
            logging.error("Output file already exists! Aborting.")
            exit(-1)
        
        if args.lang:
            args.query = "{}&l={}".format(args.query, args.lang)
        
        if args.all:
            args.begindate = dt.date(2006,3,1)

        tweets = query_tweets(args.query, args.limit, args.begindate, args.enddate, args.poolsize)

        if args.dump:
            print(json.dumps(tweets, cls=JSONEncoder))
        else:
            if tweets:
                with open(args.output, "w") as output:
                    json.dump(tweets, output, cls=JSONEncoder)
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Quitting...")
