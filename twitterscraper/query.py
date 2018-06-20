from __future__ import division
import random
import requests
import datetime as dt
import json
from functools import partial
from multiprocessing.pool import Pool

from twitterscraper.tweet import Tweet
from twitterscraper.logging import logger

HEADERS_LIST = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
                "Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13",
                "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
                "Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201",
                "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
                "Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre"]

HEADER = {'User-Agent': random.choice(HEADERS_LIST)}

INIT_URL = "https://twitter.com/search?f=tweets&vertical=default&q={q}&l={lang}"
RELOAD_URL = "https://twitter.com/i/search/timeline?f=tweets&vertical=" \
             "default&include_available_features=1&include_entities=1&" \
             "reset_error_state=false&src=typd&max_position={pos}&q={q}&l={lang}"

def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i


def query_single_page(url, html_response=True, retry=10):
    """
    Returns tweets from the given URL.

    :param url: The URL to get the tweets from
    :param html_response: False, if the HTML is embedded in a JSON
    :param retry: Number of retries if something goes wrong.
    :return: The list of tweets, the pos argument for getting the next page.
    """

    try:
        response = requests.get(url, headers=HEADER)
        if html_response:
            html = response.text or ''
        else:
            html = ''
            try:
                json_resp = json.loads(response.text)
                html = json_resp['items_html'] or ''
            except ValueError as e:
                logger.exception('Failed to parse JSON "{}" while requesting "{}"'.format(e, url))

        tweets = list(Tweet.from_html(html))

        if not tweets:
            return [], None

        if not html_response:
            return tweets, json_resp['min_position']

        return tweets, "TWEET-{}-{}".format(tweets[-1].id, tweets[0].id)
    except requests.exceptions.HTTPError as e:
        logger.exception('HTTPError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.ConnectionError as e:
        logger.exception('ConnectionError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.Timeout as e:
        logger.exception('TimeOut {} while requesting "{}"'.format(
            e, url))
    except json.decoder.JSONDecodeError as e:
        logger.exception('Failed to parse JSON "{}" while requesting "{}".'.format(
            e, url))
        
    if retry > 0:
        logger.info("Retrying... (Attempts left: {})".format(retry))
        return query_single_page(url, html_response, retry-1)

    logger.error("Giving up.")
    return [], None


def query_tweets_once(query, limit=None, lang=''):
    """
    Queries twitter for all the tweets you want! It will load all pages it gets
    from twitter. However, twitter might out of a sudden stop serving new pages,
    in that case, use the `query_tweets` method.

    Note that this function catches the KeyboardInterrupt so it can return
    tweets on incomplete queries if the user decides to abort.

    :param query: Any advanced query you want to do! Compile it at
                  https://twitter.com/search-advanced and just copy the query!
    :param limit: Scraping will be stopped when at least ``limit`` number of
                  items are fetched.
    :param num_tweets: Number of tweets fetched outside this function.
    :return:      A list of twitterscraper.Tweet objects. You will get at least
                  ``limit`` number of items.
    """
    logger.info("Querying {}".format(query))
    query = query.replace(' ', '%20').replace("#", "%23").replace(":", "%3A")
    pos = None
    tweets = []
    try:
        while True:
            new_tweets, pos = query_single_page(
                INIT_URL.format(q=query, lang=lang) if pos is None
                else RELOAD_URL.format(q=query, pos=pos, lang=lang),
                pos is None
            )
            if len(new_tweets) == 0:
                logger.info("Got {} tweets for {}.".format(
                    len(tweets), query))
                return tweets

            tweets += new_tweets

            if limit and len(tweets) >= limit:
                logger.info("Got {} tweets for {}.".format(
                    len(tweets), query))
                return tweets
    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Returning tweets gathered "
                     "so far...")
    except BaseException:
        logger.exception("An unknown error occurred! Returning tweets "
                          "gathered so far.")
    logger.info("Got {} tweets for {}.".format(
        len(tweets), query))
    return tweets


def eliminate_duplicates(iterable):
    """
    Yields all unique elements of an iterable sorted. Elements are considered
    non unique if the equality comparison to another element is true. (In those
    cases, the set conversion isn't sufficient as it uses identity comparison.)
    """
    class NoElement: pass

    prev_elem = NoElement
    for elem in sorted(iterable):
        if prev_elem is NoElement:
            prev_elem = elem
            yield elem
            continue

        if prev_elem != elem:
            prev_elem = elem
            yield elem

def query_tweets(query, limit=None, begindate=dt.date(2006,3,21), enddate=dt.date.today(), poolsize=20, lang=''):
    no_days = (enddate - begindate).days
    if poolsize > no_days:
        # Since we are assigning each pool a range of dates to query,
		# the number of pools should not exceed the number of dates.
        poolsize = no_days
    dateranges = [begindate + dt.timedelta(days=elem) for elem in linspace(0, no_days, poolsize+1)]

    if limit:
        limit_per_pool = (limit // poolsize)+1
    else:
        limit_per_pool = None

    queries = ['{} since:{} until:{}'.format(query, since, until)
               for since, until in zip(dateranges[:-1], dateranges[1:])]

    all_tweets = []
    try:
        pool = Pool(poolsize)

        try:
            for new_tweets in pool.imap_unordered(partial(query_tweets_once, limit=limit_per_pool, lang=lang), queries):
                all_tweets.extend(new_tweets)
                logger.info("Got {} tweets ({} new).".format(
                    len(all_tweets), len(new_tweets)))
        except KeyboardInterrupt:
            logger.info("Program interrupted by user. Returning all tweets "
                         "gathered so far.")
    finally:
        pool.close()
        pool.join()

    return all_tweets
