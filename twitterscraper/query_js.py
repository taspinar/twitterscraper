from __future__ import division

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
from twitterscraper.user import User


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
    opt.headless = False

    driver = webdriver.Firefox(profile, options=opt)
    driver.implicitly_wait(timeout)

    return driver


def get_query_url(query, lang, from_user=False):
    if from_user:
        return INIT_URL_USER.format(u=query)
    else:
        return INIT_URL.format(q=query, lang=lang)


def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i


def query_single_page(url, retry=50, from_user=False, timeout=60, use_proxy=True):
    """
    Returns tweets from the given URL.
    :param query: The query url
    :param retry: Number of retries if something goes wrong.
    :param use_proxy: Determines whether to fetch tweets with proxy
    :return: The list of tweets
    """

    logger.info('Scraping tweets from {}'.format(url))

    proxy_pool = get_proxy_pool() if use_proxy else cycle([None])

    proxy = next(proxy_pool)
    logger.info('Using proxy {}'.format(proxy))
    driver = get_driver(proxy)

    try:
        # page down until there isn't anything new
        driver.get(url)
        while True:
            if [r for r in driver.requests][-1].response is None:
                time.sleep(0.5)
                # not done loading
                continue
            relevant_requests = [
                r for r in driver.requests
                if 'json' in r.path and 'guide.json' not in r.path and
                r.response is not None and r.response.body is not None and
                isinstance(r.response.body, dict) and 'globalObjects' in r.response.body
            ]
            latest_request = relevant_requests[-1]
            try:
                latest_request.response.body['globalObjects']['tweets']
            except:
                import pdb;pdb.set_trace()
            if not latest_request.response.body['globalObjects']['tweets']:
                break
            actions = ActionChains(driver)
            for _ in range(10):
                actions.send_keys(Keys.PAGE_DOWN)
            actions.perform()
            time.sleep(1)

        # accumulate responses
        complete_relevant_requests = [
            r for r in driver.requests
            # all data responses have json in their path, but guide.json is irrelevant
            if 'json' in r.path and 'guide.json' not in r.path and
            r.response.body and isinstance(r.response.body, dict) and
            'globalObjects' in r.response.body
        ]
        data = defaultdict(dict)
        for req in complete_relevant_requests:
            for key, value in req.response.body['globalObjects'].items():
                data[key].update(value)

        return data

    except Exception as e:
        import pdb;pdb.set_trace()
        logger.exception('Exception {} while requesting "{}"'.format(
            e, url))
    finally:
        driver.quit()

    if retry > 0:
        logger.debug('Retrying... (Attempts left: {})'.format(retry))
        return query_single_page(url, retry - 1)
    logger.error('Giving up.')
    return {}


def get_user_data(from_user, limit=None, lang=''):
    url = INIT_URL_USER.format(u=from_user)
    return query_single_page(url)


def get_query_data(query, limit=None, begindate=None, enddate=None, from_user=None, poolsize=None, lang=''):
    begindate = begindate or dt.date(2006, 3, 21)
    enddate = enddate or dt.date.today()
    poolsize = poolsize or 20

    num_days = (enddate - begindate).days

    if(num_days < 0):
        sys.exit('Begin date must occur before end date.')

    if poolsize > num_days:
        # Since we are assigning each pool a range of dates to query,
        # the number of pools should not exceed tnhe number of dates.
        poolsize = num_days
    dateranges = [begindate + dt.timedelta(days=elem) for elem in linspace(0, num_days, poolsize + 1)]

    queries = ['{} since:{} until:{}'.format(query, since, until)
               for since, until in zip(dateranges[:-1], dateranges[1:])]
    logger.debug('queries: {}'.format(queries))
    urls = [
        get_query_url(query, lang, from_user=None)
        for query in queries
    ]
    return retrieve_urls(urls)


def retrieve_urls(urls, limit, poolsize):
    # send query urls to multiprocessing pool, and aggregate
    if limit and poolsize:
        limit_per_pool = (limit // poolsize) + 1
    else:
        limit_per_pool = None

    all_data = defaultdict
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


###
# TODO: REIMPLEMENT THESE FUNCTIONS WITH SELENIUM, THEY STILL USE REQUESTS AND STILL LIKELY ARE BROKEN
###
def query_user_page(url, retry=10, timeout=60, use_proxy=True):
    """
    Returns the scraped user data from a twitter user page.

    :param url: The URL to get the twitter user info from (url contains the user page)
    :param retry: Number of retries if something goes wrong.
    :return: Returns the scraped user data from a twitter user page.
    """
    proxy_pool = get_proxy_pool() if use_proxy else cycle([None])

    try:
        proxy = next(proxy_pool)
        logger.debug('Using proxy {}'.format(proxy))
        response = requests.get(url, headers=HEADER, proxies={"http": proxy})
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
        logger.debug('Retrying... (Attempts left: {})'.format(retry))
        return query_user_page(url, retry-1)

    logger.error('Giving up.')
    return None


def query_user_info(user):
    """
    Returns the scraped user data from a twitter user page.

    :param user: the twitter user to web scrape its twitter page info
    """
    try:
        query_single_page(user, lang='', from_user=True)
        user_info = query_user_page(INIT_URL_USER.format(u=user), lang='', from_user=True)
        if user_info:
            logger.info("Got user information from username {}".format(user))
            return user_info

    except KeyboardInterrupt:
        logger.exception("Program interrupted by user. Returning user information gathered so far...")
    except BaseException:
        logger.exception("An unknown error occurred! Returning user information gathered so far...")

    logger.info("Got user information from username {}".format(user))
    return user_info
