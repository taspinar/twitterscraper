from __future__ import division

import datetime as dt
import json
import logging
import random
import sys
import urllib
from functools import partial
from itertools import cycle

import requests
from billiard.pool import Pool
from bs4 import BeautifulSoup

from twitterscraper.tweet import Tweet
from twitterscraper.user import User

logger = logging.getLogger('twitterscraper')

#from fake_useragent import UserAgent
#ua = UserAgent()
#HEADER = {'User-Agent': ua.random}
HEADERS_LIST = [
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13',
    'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre'
]

HEADER = {'User-Agent': random.choice(HEADERS_LIST), 'X-Requested-With': 'XMLHttpRequest'}
logger.info(HEADER)

INIT_URL = 'https://twitter.com/i/search/timeline?f=tweets&vertical=' \
             'default&include_available_features=1&include_entities=1&' \
             'reset_error_state=false&src=typd&max_position=-1&q={q}&l={lang}'
RELOAD_URL = 'https://twitter.com/i/search/timeline?f=tweets&vertical=' \
             'default&include_available_features=1&include_entities=1&' \
             'reset_error_state=false&src=typd&max_position={pos}&q={q}&l={lang}'
INIT_URL_USER = 'https://twitter.com/{u}'
RELOAD_URL_USER = 'https://twitter.com/i/profiles/show/{u}/timeline/tweets?' \
                  'include_available_features=1&include_entities=1&' \
                  'max_position={pos}&reset_error_state=false'
PROXY_URL = 'https://free-proxy-list.net/'

def get_proxies():
    response = requests.get(PROXY_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table',id='proxylisttable')
    list_tr = table.find_all('tr')
    list_td = [elem.find_all('td') for elem in list_tr]
    list_td = list(filter(None, list_td))
    list_ip = [elem[0].text for elem in list_td]
    list_ports = [elem[1].text for elem in list_td]
    list_proxies = [':'.join(elem) for elem in list(zip(list_ip, list_ports))]
    return list_proxies               
                  
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

proxies = get_proxies()
proxy_pool = cycle(proxies)

def query_single_page(query, lang, pos, retry=50, from_user=False, timeout=60, use_proxy=True):
    """
    Returns tweets from the given URL.

    :param query: The query parameter of the query url
    :param lang: The language parameter of the query url
    :param pos: The query url parameter that determines where to start looking
    :param retry: Number of retries if something goes wrong.
    :return: The list of tweets, the pos argument for getting the next page.
    """
    url = get_query_url(query, lang, pos, from_user)
    logger.info('Scraping tweets from {}'.format(url))

    try:
        if use_proxy:
            proxy = next(proxy_pool)
            logger.info('Using proxy {}'.format(proxy))
            response = requests.get(url, headers=HEADER, proxies={"http": proxy}, timeout=timeout)
        else:
            print('not using proxy')
            response = requests.get(url, headers=HEADER, timeout=timeout)
        if pos is None:  # html response
            json_resp = response.json()
            html = json_resp['items_html'] or ''
        else:
            html = ''
            try:
                json_resp = response.json()
                html = json_resp['items_html'] or ''
            except (ValueError, KeyError) as e:
                logger.exception('Failed to parse JSON while requesting "{}"'.format(url))

        tweets = list(Tweet.from_html(html))

        if not tweets:
            try:
                if json_resp:
                    pos = json_resp['min_position']
                    has_more_items = json_resp['has_more_items']
                    if not has_more_items:
                        logger.info("Twitter returned : 'has_more_items' ")
                        return [], None
                else:
                    pos = None
            except:
                pass
            if retry > 0:
                logger.info('Retrying... (Attempts left: {})'.format(retry))
                return query_single_page(query, lang, pos, retry - 1, from_user, use_proxy=use_proxy)
            else:
                return [], pos

        if json_resp:
            return tweets, urllib.parse.quote(json_resp['min_position'])
        if from_user:
            return tweets, tweets[-1].tweet_id
        return tweets, "TWEET-{}-{}".format(tweets[-1].tweet_id, tweets[0].tweet_id)

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
        return query_single_page(query, lang, pos, retry - 1, use_proxy=use_proxy)

    logger.error('Giving up.')
    return [], None


def query_tweets_once_generator(query, limit=None, lang='', pos=None, use_proxy=True):
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
    query = query.replace(' ', '%20').replace('#', '%23').replace(':', '%3A').replace('&', '%26')
    num_tweets = 0
    try:
        while True:
            new_tweets, new_pos = query_single_page(query, lang, pos, use_proxy=use_proxy)
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


def query_tweets(query, limit=None, begindate=dt.date(2006, 3, 21), enddate=dt.date.today(), poolsize=20, lang='', use_proxy=True):
    no_days = (enddate - begindate).days
    
    if(no_days < 0):
        sys.exit('Begin date must occur before end date.')
    
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
            for new_tweets in pool.imap_unordered(partial(query_tweets_once, limit=limit_per_pool, lang=lang, use_proxy=use_proxy), queries):
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


def query_tweets_from_user(user, limit=None, use_proxy=True):
    pos = None
    tweets = []
    try:
        while True:
           new_tweets, pos = query_single_page(user, lang='', pos=pos, from_user=True, use_proxy=use_proxy)
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


def query_user_page(url, retry=10, timeout=60, use_proxy=True):
    """
    Returns the scraped user data from a twitter user page.

    :param url: The URL to get the twitter user info from (url contains the user page)
    :param retry: Number of retries if something goes wrong.
    :return: Returns the scraped user data from a twitter user page.
    """

    try:
        if use_proxy:
            proxy = next(proxy_pool)
            logger.info('Using proxy {}'.format(proxy))
            response = requests.get(url, headers=HEADER, proxies={"http": proxy})
        else:
            response = requests.get(url, headers=HEADER)
        html = response.text or ''

        user_info = User.from_html(html)
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
        return query_user_page(url, retry-1, use_proxy)

    logger.error('Giving up.')
    return None


def query_user_info(user, use_proxy=True):
    """
    Returns the scraped user data from a twitter user page.

    :param user: the twitter user to web scrape its twitter page info
    """


    try:
        user_info = query_user_page(INIT_URL_USER.format(u=user), use_proxy=use_proxy)
        if user_info:
            logger.info("Got user information from username {}".format(user))
            return user_info

    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Returning user information gathered so far...")
    except BaseException:
        logger.exception("An unknown error occurred! Returning user information gathered so far...")

    logger.info("Got user information from username {}".format(user))
    return user_info
