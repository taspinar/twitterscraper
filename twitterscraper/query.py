import json
import logging
import random
import urllib

from fake_useragent import UserAgent

from twitterscraper.tweet import Tweet


ua = UserAgent()
HEADERS_LIST = [ua.chrome, ua.google, ua['google chrome'], ua.firefox, ua.ff]

INIT_URL = "https://twitter.com/search?f=tweets&vertical=default&q={q}"
RELOAD_URL = "https://twitter.com/i/search/timeline?f=tweets&vertical=" \
             "default&include_available_features=1&include_entities=1&" \
             "reset_error_state=false&src=typd&max_position={pos}&q={q}"


def query_single_page(url, html_response=True):
    """
    Returns tweets from the given URL.

    :param url: The URL to get the tweets from
    :param html_response: False, if the HTML is embedded in a JSON
    :return: The list of tweets, the pos argument for getting the next page.
    """
    logging.info("Gathering tweets from {}".format(url))
    headers = {'User-Agent': random.choice(HEADERS_LIST)}
    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req).read().decode()
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
    except urllib.request.HTTPError as e:
        logging.exception('HTTPError {} while requesting "{}"'.format(
            e.code, url))
    except urllib.request.URLError as e:
        logging.exception('URLError {} while requesting "{}"'.format(
            e.reason, url))

    return [], None


def query_tweets(query, limit=None):
    """
    Queries twitter for all the tweets you want!

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
    while True:
        new_tweets, pos = query_single_page(
            INIT_URL.format(q=query) if pos is None
            else RELOAD_URL.format(q=query, pos=pos),
            pos is None
        )
        if len(new_tweets) == 0:
            return tweets

        tweets += new_tweets

        if limit is not None and len(tweets) >= limit:
            return tweets
