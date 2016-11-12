import json
import logging
import random
import sys
if sys.version_info[0] == 2:
    from urllib2 import urlopen, Request, HTTPError, URLError
else:
    from urllib.request import urlopen, Request, HTTPError, URLError

from fake_useragent import UserAgent

from twitterscraper.tweet import Tweet


ua = UserAgent()
HEADERS_LIST = [ua.chrome, ua.google, ua['google chrome'], ua.firefox, ua.ff]

INIT_URL = "https://twitter.com/search?f=tweets&vertical=default&q={q}"
RELOAD_URL = "https://twitter.com/i/search/timeline?f=tweets&vertical=" \
             "default&include_available_features=1&include_entities=1&" \
             "reset_error_state=false&src=typd&max_position={pos}&q={q}"


def query_single_page(url, html_response=True, retry=3):
    """
    Returns tweets from the given URL.

    :param url: The URL to get the tweets from
    :param html_response: False, if the HTML is embedded in a JSON
    :param retry: Number of retries if something goes wrong.
    :return: The list of tweets, the pos argument for getting the next page.
    """
    headers = {'User-Agent': random.choice(HEADERS_LIST)}
    req = Request(url, headers=headers)
    try:
        response = urlopen(req).read().decode('utf-8')
        if html_response:
            html = response
        else:
            json_resp = json.loads(response)
            html = json_resp['items_html']

        tweets = list(Tweet.from_html(html))
        if not tweets:
            return [], None

        if not html_response:
            return tweets, json_resp['min_position']

        return tweets, "TWEET-{}-{}".format(tweets[-1].id, tweets[0].id)
    except HTTPError as e:
        logging.exception('HTTPError {} while requesting "{}"'.format(
            e.code, url))
    except URLError as e:
        logging.exception('URLError {} while requesting "{}"'.format(
            e.reason, url))

    if retry > 0:
        logging.info("Retrying...")
        return query_single_page(url, html_response, retry-1)

    logging.error("Giving up.")
    return [], None


def query_tweets(query, limit=None):
    """
    Queries twitter for all the tweets you want!

    Note that this function catches the KeyboardInterrupt so it can return
    tweets on incomplete queries if the user decides to abort.

    :param query: Any advanced query you want to do! Compile it at
                  https://twitter.com/search-advanced and just copy the query!
    :param limit: Scraping will be stopped when at least ``limit`` number of
                  items are fetched.
    :return:      A list of twitterscraper.Tweet objects. You will get at least
                  ``limit`` number of items.
    """
    query = query.replace(' ', '%20').replace("#", "%23")
    pos = None
    tweets = []
    try:
        while True:
            new_tweets, pos = query_single_page(
                INIT_URL.format(q=query) if pos is None
                else RELOAD_URL.format(q=query, pos=pos),
                pos is None
            )
            if len(new_tweets) == 0:
                return tweets

            tweets += new_tweets
            logging.info("Got {} tweets ({} new).".format(len(tweets),
                                                          len(new_tweets)))

            if limit is not None and len(tweets) >= limit:
                return tweets
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Returning tweets gathered "
                     "so far...")
    except BaseException:
        logging.exception("An unknown error occurred! Returning tweets "
                          "gathered so far.")

    return tweets