from collections import defaultdict
import requests
import datetime as dt
import time
import sys

from functools import lru_cache, partial
from billiard.pool import Pool
from bs4 import BeautifulSoup
from itertools import cycle

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from twitterscraper.ts_logger import logger


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
    profile = webdriver.FirefoxProfile()
    if proxy:
        profile.set_preference("network.proxy.http", proxy)

    opt = Options()
    opt.headless = True

    driver = webdriver.Firefox(profile, options=opt)
    driver.implicitly_wait(timeout)

    return driver


def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i


def query_single_page(url, retry=50, from_user=False, timeout=60, use_proxy=True, limit=None):
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
        retries = 20
        while retries > 0 and len(data['tweets']) < limit:

            # relevant requests have completely responses, json in their path (but not guide.json), and a globalObjects key
            relevant_request_idxs = set([
                i for i, r in enumerate(driver.requests)
                if 'json' in r.path and 'guide.json' not in r.path and
                r.response is not None and isinstance(r.response.body, dict) and
                'globalObjects' in r.response.body and i not in already_idxs
            ])
            already_idxs |= relevant_request_idxs

            if not relevant_request_idxs:
                time.sleep(0.2)
                retries -= 1
                continue

            # if no relevant requests, or latest relevant request isn't done loading, wait then check again
            latest_tweets = driver.requests[max(relevant_request_idxs)].response.body['globalObjects']['tweets']
            if len(relevant_request_idxs) == 0 or not latest_tweets:
                time.sleep(0.2)
                retries -= 1
                continue

            # scroll down
            actions = ActionChains(driver)
            for _ in range(100):
                actions.send_keys(Keys.PAGE_DOWN)
            actions.perform()

            # record relevant responses
            for idx in relevant_request_idxs:
                driver.requests[idx]
                for key, value in driver.requests[idx].response.body['globalObjects'].items():
                    data[key].update(value)

            # reset retries
            retries = 20

        return data

    except Exception as e:
        logger.exception('Exception {} while requesting "{}"'.format(
            e, url))
    finally:
        driver.quit()

    if retry > 0:
        logger.debug('Retrying... (Attempts left: {})'.format(retry))
        return query_single_page(url, retry - 1)
    logger.error('Giving up.')
    return defaultdict(dict)


def get_query_data(queries, limit=None, begindate=None, enddate=None, poolsize=None, lang=''):
    begindate = begindate or dt.date(2006, 3, 21)
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
    dateranges = list(reversed([begindate + dt.timedelta(days=elem) for elem in linspace(0, num_days, num_days)]))

    urls = []
    for until, since in zip(dateranges[:-1], dateranges[1:]):
        for query in queries:
            query_str = '{} since:{} until:{}'.format(query, since, until)
            urls.append(INIT_URL.format(q=query_str, lang=lang))
            logger.info('query: {}'.format(query_str))

    return retrieve_data_from_urls(urls, limit=limit, poolsize=poolsize)


def get_user_data(from_user, *args, **kwargs):
    # include retweets
    retweet_query = f'filter:nativeretweets from:{from_user}'
    no_retweet_query = f'from:{from_user}'
    return get_query_data([retweet_query, no_retweet_query], *args, **kwargs)


def retrieve_data_from_urls(urls, limit, poolsize):
    # send query urls to multiprocessing pool, and aggregate
    if limit and poolsize:
        limit_per_pool = (limit // poolsize) + 1
    else:
        limit_per_pool = None

    all_data = defaultdict(dict)
    try:
        pool = Pool(poolsize)
        try:
            for new_data in pool.imap_unordered(partial(query_single_page, limit=limit_per_pool), urls):
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
