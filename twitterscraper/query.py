from __future__ import division
import random
import requests
import datetime as dt
import json
from functools import partial
# from multiprocessing.pool import Pool
from billiard.pool import Pool

from twitterscraper.tweet import Tweet
from twitterscraper.ts_logger import logger
from twitterscraper.user import User
import urllib

HEADERS_LIST = [
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13',
    'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre'
]

HEADER = {'User-Agent': random.choice(HEADERS_LIST)}

INIT_URL = 'https://twitter.com/search?f=tweets&vertical=default&q={q}&l={lang}'
RELOAD_URL = 'https://twitter.com/i/search/timeline?f=tweets&vertical=' \
             'default&include_available_features=1&include_entities=1&' \
             'reset_error_state=false&src=typd&max_position={pos}&q={q}&l={lang}'
INIT_URL_USER = 'https://twitter.com/{u}'
RELOAD_URL_USER = 'https://twitter.com/i/profiles/show/{u}/timeline/tweets?' \
                  'include_available_features=1&include_entities=1&' \
                  'max_position={pos}&reset_error_state=false'


def get_query_url(query, lang, pos, from_user = False):
    if from_user:
        if pos is None:
            return INIT_URL_USER.format(u=query)
        else:
            return RELOAD_URL_USER.format(u=query, pos=pos)
    if pos is None:
        return INIT_URL.format(q=query, lang=lang)
    else:
        return RELOAD_URL.format(q=query, pos=pos, lang=lang)


def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i



def query_single_page(query, lang, pos, retry=50, from_user=False):
    """
    Returns tweets from the given URL.

    :param query: The query parameter of the query url
    :param lang: The language parameter of the query url
    :param pos: The query url parameter that determines where to start looking
    :param retry: Number of retries if something goes wrong.
    :return: The list of tweets, the pos argument for getting the next page.
    """
    url = get_query_url(query, lang, pos, from_user)

    try:
        response = requests.get(url, headers=HEADER)
        if pos is None:  # html response
            html = response.text or ''
            json_resp = None
        else:
            html = ''
            try:
                json_resp = json.loads(response.text)
                html = json_resp['items_html'] or ''
            except ValueError as e:
                logger.exception('Failed to parse JSON "{}" while requesting "{}"'.format(e, url))

        tweets = list(Tweet.from_html(html))

        if not tweets:
            if json_resp:
                pos = json_resp['min_position']
            else:
                pos = None
            if retry > 0:
                return query_single_page(query, lang, pos, retry - 1, from_user)
            else:
                return [], pos

        if json_resp:
            return tweets, urllib.parse.quote(json_resp['min_position'])
        if from_user:
            return tweets, tweets[-1].id
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
        logger.info('Retrying... (Attempts left: {})'.format(retry))
        return query_single_page(query, lang, pos, retry - 1)

    logger.error('Giving up.')
    return [], None


def query_tweets_once_generator(query, limit=None, lang='', pos=None):
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
    :param pos: Field used as a "checkpoint" to continue where you left off in iteration
    :return:      A list of twitterscraper.Tweet objects. You will get at least
                  ``limit`` number of items.
    """
    logger.info('Querying {}'.format(query))
    query = query.replace(' ', '%20').replace('#', '%23').replace(':', '%3A')
    num_tweets = 0
    try:
        while True:
            new_tweets, new_pos = query_single_page(query, lang, pos)
            if len(new_tweets) == 0:
                logger.info('Got {} tweets for {}.'.format(
                    num_tweets, query))
                return

            for t in new_tweets:
                yield t, pos

            # use new_pos only once you have iterated through all old tweets
            pos = new_pos

            num_tweets += len(new_tweets)

            if limit and num_tweets >= limit:
                logger.info('Got {} tweets for {}.'.format(
                    num_tweets, query))
                return

    except KeyboardInterrupt:
        logger.info('Program interrupted by user. Returning tweets gathered '
                     'so far...')
    except BaseException:
        logger.exception('An unknown error occurred! Returning tweets '
                          'gathered so far.')
    logger.info('Got {} tweets for {}.'.format(
        num_tweets, query))


def query_tweets_once(*args, **kwargs):
    res = list(query_tweets_once_generator(*args, **kwargs))
    if res:
        tweets, positions = zip(*res)
        return tweets
    else:
        return []


def query_tweets(query, limit=None, begindate=dt.date(2006, 3, 21), enddate=dt.date.today(), poolsize=20, lang=''):
    no_days = (enddate - begindate).days
    if poolsize > no_days:
        # Since we are assigning each pool a range of dates to query,
		# the number of pools should not exceed the number of dates.
        poolsize = no_days
    dateranges = [begindate + dt.timedelta(days=elem) for elem in linspace(0, no_days, poolsize+1)]

    if limit and poolsize:
        limit_per_pool = (limit // poolsize)+1
    else:
        limit_per_pool = None

    queries = ['{} since:{} until:{}'.format(query, since, until)
               for since, until in zip(dateranges[:-1], dateranges[1:])]

    all_tweets = []
    try:
        pool = Pool(poolsize)
        logger.info('queries: {}'.format(queries))
        try:
            for new_tweets in pool.imap_unordered(partial(query_tweets_once, limit=limit_per_pool, lang=lang), queries):
                all_tweets.extend(new_tweets)
                logger.info('Got {} tweets ({} new).'.format(
                    len(all_tweets), len(new_tweets)))
        except KeyboardInterrupt:
            logger.info('Program interrupted by user. Returning all tweets '
                         'gathered so far.')
    finally:
        pool.close()
        pool.join()

    return all_tweets


def query_tweets_from_user(user, limit=None):
    pos = None
    tweets = []
    try:
        while True:
           new_tweets, pos = query_single_page(user, lang='', pos=pos, from_user=True)
           if len(new_tweets) == 0:
               logger.info("Got {} tweets from username {}".format(len(tweets), user))
               return tweets

           tweets += new_tweets

           if limit and len(tweets) >= limit:
               logger.info("Got {} tweets from username {}".format(len(tweets), user))
               return tweets

    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Returning tweets gathered "
                     "so far...")
    except BaseException:
        logger.exception("An unknown error occurred! Returning tweets "
                          "gathered so far.")
    logger.info("Got {} tweets from username {}.".format(
        len(tweets), user))
    return tweets


def query_user_page(url, retry=10):
    """
    Returns the scraped user data from a twitter user page.

    :param url: The URL to get the twitter user info from (url contains the user page)
    :param retry: Number of retries if something goes wrong.
    :return: Returns the scraped user data from a twitter user page.
    """

    try:
        response = requests.get(url, headers=HEADER)
        html = response.text or ''

        user = User()
        user_info = user.from_html(html)
        if not user_info:
            return None

        return user_info

    except requests.exceptions.HTTPError as e:
        logger.exception('HTTPError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.ConnectionError as e:
        logger.exception('ConnectionError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.Timeout as e:
        logger.exception('TimeOut {} while requesting "{}"'.format(
            e, url))

    if retry > 0:
        logger.info('Retrying... (Attempts left: {})'.format(retry))
        return query_user_page(url, retry-1)

    logger.error('Giving up.')
    return None


def query_user_info(user):
    """
    Returns the scraped user data from a twitter user page.

    :param user: the twitter user to web scrape its twitter page info
    """


    try:
        user_info = query_user_page(INIT_URL_USER.format(u=user))
        if user_info:
            logger.info(f"Got user information from username {user}")
            return user_info

    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Returning user information gathered so far...")
    except BaseException:
        logger.exception("An unknown error occurred! Returning user information gathered so far...")

    logger.info(f"Got user information from username {user}")
    return user_info
