"""
This is a command line application that allows you to scrape twitter!
"""
import csv
import json
import argparse
import collections
import datetime as dt
from os.path import isfile
from pprint import pprint
from twitterscraper import query_js, query
from twitterscraper.ts_logger import logger


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
        parser.add_argument("-c", "--csv", action='store_true',
                            help="Set this flag if you want to save the results to a CSV format.")
        parser.add_argument("-j", "--javascript", action='store_true',
                            help="Set this flag if you want to request using javascript via Selenium.")
        parser.add_argument("-u", "--user", action='store_true',
                            help="Set this flag to if you want to scrape tweets from a specific user"
                                 "The query should then consist of the profilename you want to scrape without @")
        parser.add_argument("--profiles", action='store_true',
                            help="Set this flag to if you want to scrape profile info of all the users where you"
                            "have previously scraped from. After all of the tweets have been scraped it will start"
                            "a new process of scraping profile pages.")
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
        parser.add_argument("-ow", "--overwrite", action="store_true",
                            help="Set this flag if you want to overwrite the existing output file.")
        parser.add_argument("-bd", "--begindate", type=valid_date, default="2006-03-21",
                            help="Scrape for tweets starting from this date. Format YYYY-MM-DD. \nDefault value is 2006-03-21", metavar='\b')
        parser.add_argument("-ed", "--enddate", type=valid_date, default=dt.date.today(),
                            help="Scrape for tweets until this date. Format YYYY-MM-DD. \nDefault value is the date of today.", metavar='\b')
        parser.add_argument("-p", "--poolsize", type=int, default=20, help="Specify the number of parallel process you want to run. \n"
                            "Default value is set to 20. \nYou can change this number if you have more computing power available. \n"
                            "Set to 1 if you dont want to run any parallel processes.", metavar='\b')
        args = parser.parse_args()

        if isfile(args.output) and not args.dump and not args.overwrite:
            logger.error("Output file already exists! Aborting.")
            exit(-1)

        if args.all:
            args.begindate = dt.date(2006, 3, 1)

        if args.user:
            if args.javascript:
                tweets = query_js.get_user_data(
                    from_user=args.query, limit=args.limit,
                    begindate=args.begindate, enddate=args.enddate,
                    poolsize=args.poolsize, lang=args.lang
                )['tweets']
            else:
                tweets = query.query_tweets_from_user(user=args.query, limit=args.limit)

        else:
            if args.javascript:
                tweets = query_js.get_query_data(
                    query=args.query, limit=args.limit,
                    begindate=args.begindate, enddate=args.enddate,
                    poolsize=args.poolsize, lang=args.lang
                )
            else:
                tweets = query.query_tweets(
                    query=args.query, limit=args.limit,
                    begindate=args.begindate, enddate=args.enddate,
                    poolsize=args.poolsize, lang=args.lang
                )

        if args.dump:
            pprint([tweet.__dict__ for tweet in tweets])
        else:
            if tweets:
                with open(args.output, "w", encoding="utf-8") as output:
                    if args.csv:
                        f = csv.writer(output, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
                        f.writerow([
                            "screen_name", "username", "user_id", "tweet_id",
                            "tweet_url", "timestamp", "timestamp_epochs",
                            "text", "text_html", "links", "hashtags",
                            "has_media", "img_urls", "video_url", "likes",
                            "retweets", "replies", "is_replied", "is_reply_to",
                            "parent_tweet_id", "reply_to_users"
                        ])
                        for t in tweets:
                            f.writerow([
                                t.screen_name, t.username, t.user_id,
                                t.tweet_id, t.tweet_url, t.timestamp,
                                t.timestamp_epochs, t.text, t.text_html,
                                t.links, t.hashtags, t.has_media, t.img_urls,
                                t.video_url, t.likes, t.retweets, t.replies,
                                t.is_replied, t.is_reply_to, t.parent_tweet_id,
                                t.reply_to_users
                            ])
                    else:
                        json.dump(tweets, output, cls=JSONEncoder)
            if args.profiles and tweets:
                list_users = list(set([tweet.username for tweet in tweets]))
                # Note: this has no query_js equivalent!
                list_users_info = [query.query_user_info(elem) for elem in list_users]
                filename = 'userprofiles_' + args.output
                with open(filename, "w", encoding="utf-8") as output:
                    json.dump(list_users_info, output, cls=JSONEncoder)
    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Quitting...")
