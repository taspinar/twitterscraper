"""
A simple script that scrapes all tweets from the given authors.
"""
import json
import logging
import random
import urllib

from fake_useragent import UserAgent

from twitterscraper.tweet import Tweet


ua = UserAgent()
HEADERS_LIST = [ua.chrome, ua.google, ua['google chrome'], ua.firefox, ua.ff]


def from_url(url, html_response=True):
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
            tweets = list(Tweet.from_html(response))
            pos = "TWEET-{}-{}".format(tweets[-1].id, tweets[0].id)
            return list(Tweet.from_html(response)), pos
        else:
            json_resp = json.loads(response)
            tweets = list(Tweet.from_html(json_resp['items_html']))
            return tweets, json_resp['min_position']
    except urllib.request.HTTPError as e:
        logging.error('HTTPError {} while requesting "{}"'.format(
            e.code, url))
    except urllib.request.URLError as e:
        logging.error('URLError {} while requesting "{}"'.format(
            e.reason, url))


INIT_URL = "https://twitter.com/search?f=tweets&vertical=default&q={q}"
RELOAD_URL = "https://twitter.com/i/search/timeline?f=tweets&vertical=" \
             "default&include_available_features=1&include_entities=1&" \
             "reset_error_state=false&src=typd&max_position={pos}&q={q}"


def query_tweets(query):
    pos = None
    tweets = []
    while True:
        new_tweets, pos = list(from_url(
            INIT_URL.format(q=query) if pos is None
            else RELOAD_URL.format(q=query, pos=pos),
            pos is None
        ))
        if len(new_tweets) == 0:
            break

        tweets += new_tweets

    return tweets


def authors_posts(author: str):
    return query_tweets("from:" + author)
