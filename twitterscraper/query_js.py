from collections import defaultdict
import requests
import datetime as dt
import time
import sys
import json

from functools import lru_cache, partial
from billiard.pool import Pool
from bs4 import BeautifulSoup
from itertools import cycle

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from twitterscraper.tweet import Tweet

import logging
logger = logging.getLogger('twitterscraper')


INIT_URL = 'https://twitter.com/search?f=live&vertical=default&q={q}&l={lang}'
INIT_URL_USER = 'https://twitter.com/{u}'
PROXY_URL = 'https://free-proxy-list.net/'


@lru_cache(1)
def get_proxy_pool():
    response = requests.get(PROXY_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', id='proxylisttable')
    list_tr = table.find_all('tr')
    list_td = [elem.find_all('td') for elem in list_tr]
    list_td = list(filter(None, list_td))
    list_ip = [elem[0].text for elem in list_td]
    list_ports = [elem[1].text for elem in list_td]
    list_proxies = [':'.join(elem) for elem in list(zip(list_ip, list_ports))]
    return cycle(list_proxies)


def get_driver(proxy=None, timeout=10):
    seleniumwire_options = {'verify_ssl': False, 'suppress_connection_errors': False}
    if proxy:
        seleniumwire_options['proxy'] = {
            'https': f'https://{proxy}',
            'http': f'http://{proxy}',
        }
    opt = Options()
    opt.headless = True

    driver = webdriver.Firefox(
        options=opt,
        seleniumwire_options=seleniumwire_options
    )

    driver.implicitly_wait(timeout)

    return driver


def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i


def decode_body(body):
    try:
        return json.loads(body)
    except (UnicodeDecodeError, json.decoder.JSONDecodeError):
        return None


def query_single_page(url, retry=50, from_user=False, timeout=60, use_proxy=True, limit=None, npasses=3):
    """
    Returns tweets from the given URL.
    :param query: The query url
    :param retry: Number of retries if something goes wrong.
    :param use_proxy: Determines whether to fetch tweets with proxy
    :param limit: Max number of tweets to get
    :return: Twitter dict containing tweets users, locations, and other metadata
    """
    limit = limit or float('inf')

    logger.info('Scraping tweets from {}'.format(url))

    proxy_pool = get_proxy_pool() if use_proxy else cycle([None])

    proxy = next(proxy_pool)
    logger.info('Using proxy {}'.format(proxy))
    driver = get_driver(proxy)

    try:
        data = defaultdict(dict)
        already_idxs = set()

        # page down, recording the results, until there isn't anything new or limit has been breached
        driver.get(url)
        retries = 100
        while retries > 0 and len(data['tweets']) < limit:

            # scroll down
            actions = ActionChains(driver)
            for _ in range(100):
                actions.send_keys(Keys.PAGE_DOWN)
                actions.pause(0.03)
            actions.perform()

            # relevant requests have completely responses, json in their path (but not guide.json), and a globalObjects key
            relevant_request_idxs = set([
                i for i, r in enumerate(driver.requests)
                if 'json' in r.path and 'guide.json' not in r.path and
                r.response is not None and isinstance(decode_body(r.response.body), dict) and
                'globalObjects' in decode_body(r.response.body) and i not in already_idxs
            ])
            already_idxs |= relevant_request_idxs

            if not relevant_request_idxs:
                # if most recent
                time.sleep(0.01)
                retries -= 1
                continue

            # if no relevant requests, or latest relevant request isn't done loading, wait then check again
            latest_tweets = decode_body(driver.requests[max(relevant_request_idxs)].response.body)['globalObjects']['tweets']
            if len(relevant_request_idxs) == 0 or not latest_tweets:
                time.sleep(0.01)
                retries -= 1
                continue

            # record relevant responses
            for idx in relevant_request_idxs:
                driver.requests[idx]
                for key, value in decode_body(driver.requests[idx].response.body)['globalObjects'].items():
                    data[key].update(value)

            # reset retries
            retries = 100

    except Exception as e:
        logger.exception('Exception {} while requesting "{}"'.format(
            e, url))
    finally:
        driver.quit()

    if npasses <= 1:
        return data
    else:
        new_pass_data = query_single_page(
            url, retry=retry, from_user=from_user, timeout=timeout,
            use_proxy=use_proxy, limit=None, npasses=npasses - 1,
        )
        for key in data.keys():
            data[key].update(new_pass_data[key])
        return data

    if retry > 0:
        logger.debug('Retrying... (Attempts left: {})'.format(retry))
        return query_single_page(
            url, retry=retry - 1, from_user=from_user, timeout=timeout,
            use_proxy=use_proxy, limit=None, npasses=npasses
        )
    logger.error('Giving up.')
    return defaultdict({})


def get_query_data(query, limit=None, begindate=None, enddate=None, poolsize=None, lang='', use_proxy=True):
    begindate = begindate or dt.date.today() - dt.timedelta(days=1)
    enddate = enddate or dt.date.today()
    poolsize = poolsize or 5

    num_days = (enddate - begindate).days

    if(num_days < 0):
        sys.exit('Begin date must occur before end date.')

    if poolsize > num_days:
        # Since we are assigning each pool a range of dates to query,
        # the number of pools should not exceed the number of dates.
        poolsize = num_days
    # query one day at a time so driver doesn't use too much memory
    dateranges = list(reversed([begindate + dt.timedelta(days=elem) for elem in linspace(0, num_days, num_days + 1)]))

    urls = []
    for until, since in zip(dateranges[:-1], dateranges[1:]):
        query_str = '{} since:{} until:{}'.format(query, since, until)
        urls.append(INIT_URL.format(q=query_str, lang=lang))
        logger.info('query: {}'.format(query_str))

    data = retrieve_data_from_urls(urls, limit=limit, poolsize=poolsize, use_proxy=use_proxy)
    tweets = get_tweets_in_daterange(data['tweets'], begindate, enddate)
    return get_tweet_objects(tweets, data['users'])


def get_tweet_objects(tweets_dict, users):
    tweets = []
    for tid, tweet_item in sorted(tweets_dict.items(), reverse=True):
        user = users[str(tweet_item['user_id'])]
        tweets.append(Tweet(
            screen_name=user['screen_name'],
            username=user['name'],
            user_id=tweet_item['user_id'],
            tweet_id=tid,
            tweet_url=f'https://twitter.com/{user["screen_name"]}/status/{tid}',  # hack?
            timestamp=timestamp_of_tweet(tweet_item),  # hack?
            timestamp_epochs=timestamp_of_tweet(tweet_item),  # hack?
            text=tweet_item['full_text'],
            text_html=None,  # hack?
            links=tweet_item['entities']['urls'],
            hashtags=tweet_item['entities']['hashtags'],
            has_media=None,  # hack?
            img_urls=None,  # hack?
            parent_tweet_id=tweet_item['in_reply_to_status_id'],
            reply_to_users=tweet_item['in_reply_to_user_id'],  # hack?
            video_url=None,  #hack?
            likes=None,  #hack?,
            retweets=None,  #hack?
            replies=None,  #hack?
            is_replied=None,  #hack?
            is_reply_to=None,  #hack?
        ))
    return tweets


def date_of_tweet(tweet):
    return dt.datetime.strptime(
        tweet['created_at'], '%a %b %d %H:%M:%S %z %Y'
    ).replace(tzinfo=None).date()


def timestamp_of_tweet(tweet):
    return dt.datetime.strptime(
        tweet['created_at'], '%a %b %d %H:%M:%S %z %Y'
    ).timestamp()


def get_tweets_in_daterange(tweets, begindate=None, enddate=None):
    begindate = begindate or dt.date(1990, 1, 1)
    enddate = enddate or dt.date(2100, 1, 1)
    return {
        tid: tweet for tid, tweet in tweets.items()
        if begindate <= date_of_tweet(tweet) <= enddate
    }


def get_user_data(from_user, *args, **kwargs):
    # include retweets
    retweet_query = f'filter:nativeretweets from:{from_user}'
    no_retweet_query = f'from:{from_user}'
    return (
        get_query_data(retweet_query, *args, **kwargs) +
        get_query_data(no_retweet_query, *args, **kwargs)
    )


def retrieve_data_from_urls(urls, limit, poolsize, use_proxy=True):
    # send query urls to multiprocessing pool, and aggregate
    if limit and poolsize:
        limit_per_pool = (limit // poolsize) + 1
    else:
        limit_per_pool = None

    all_data = defaultdict(dict)
    try:
        pool = Pool(poolsize)
        try:
            for new_data in pool.imap_unordered(partial(query_single_page, limit=limit_per_pool, use_proxy=use_proxy), urls):
                for key, value in new_data.items():
                    all_data[key].update(value)
                logger.info('Got {} data ({} new).'.format(
                    len(all_data['tweets']), len(new_data['tweets'])))
        except KeyboardInterrupt:
            logger.debug('Program interrupted by user. Returning all tweets gathered so far.')
    finally:
        pool.close()
        pool.join()

    return all_data
