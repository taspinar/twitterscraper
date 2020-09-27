import requests
from functools import lru_cache
from itertools import cycle
from bs4 import BeautifulSoup
from threading import Thread

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

import logging
logger = logging.getLogger('twitterscraper')


PROXY_URL = 'https://free-proxy-list.net/'
NYT_LOGO_URL = 'https://pbs.twimg.com/profile_images/1098244578472280064/gjkVMelR_normal.png'


def get_proxy_delay(proxy, result, max_time=10):
    try:
        response = requests.post(
            NYT_LOGO_URL,
            proxies={'https': f'https://{proxy}/'},
            timeout=max_time
        )

    except Exception:
        result[proxy] = None
    else:
        result[proxy] = response.elapsed.total_seconds()


@lru_cache(1)
def get_best_proxies(proxies):
    logger.info('Pinging twitter to find best proxies')
    threads = []
    result = {}
    # In this case 'urls' is a list of urls to be crawled.
    for proxy in proxies:
        process = Thread(target=get_proxy_delay, args=[proxy, result])
        process.start()
        threads.append(process)
    for process in threads:
        process.join()

    assert len(set(result.values())) > 1  # ensure at least one proxy took less than max_time

    result = {k: v for k, v in result.items() if v}
    best_proxies = [x[0] for x in sorted(result.items(), key=lambda x: x[1])]
    return best_proxies[:int(len(best_proxies)**0.5)]  # best sqrt(N) of N working proxies


@lru_cache(1)
def get_proxies():
    response = requests.get(PROXY_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', id='proxylisttable')
    list_tr = table.find_all('tr')
    list_td = [elem.find_all('td') for elem in list_tr]
    list_td = list(filter(None, list_td))
    list_ip = [elem[0].text for elem in list_td]
    list_ports = [elem[1].text for elem in list_td]
    list_proxies = [':'.join(elem) for elem in list(zip(list_ip, list_ports))]
    return list_proxies


def get_proxy_pool():
    # TODO: cache this on disk so reruns aren't required
    best_proxies = get_best_proxies(
        tuple(get_proxies())
    )
    return cycle(best_proxies)


@lru_cache(1)
def get_ublock():
    pass
    #download ublock here


def get_driver(proxy=None, timeout=10):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("http.response.timeout", 5)

    seleniumwire_options = {'verify_ssl': False}
    if proxy:
        seleniumwire_options['suppress_connection_errors'] = False
        seleniumwire_options['proxy'] = {
            'https': f'https://{proxy}',
            'http': f'http://{proxy}',
        }

    opt = Options()
    opt.headless = True

    driver = webdriver.Firefox(
        firefox_profile=profile,
        options=opt,
        seleniumwire_options=seleniumwire_options
    )

    """
    TODO: install ublock here
    get_ublock()
    extensions.ublock0.adminSettings = best settings for twitter here
    browser.install_addon(extension_dir + extension, temporary=True)
    """

    driver.set_page_load_timeout(timeout)

    return driver
