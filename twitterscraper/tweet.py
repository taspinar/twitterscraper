from collections import namedtuple

from bs4 import BeautifulSoup


class Tweet(namedtuple("Tweet", "user id timestamp fullname text")):
    @classmethod
    def from_soup(cls, tweet):
        return cls(
            user=tweet.find('span', 'username').text[1:],
            id=tweet['data-item-id'],
            timestamp=tweet.find('a', 'tweet-timestamp')['title'],
            fullname=tweet.find('strong', 'fullname').text,
            text=tweet.find('p', 'tweet-text').text
            if tweet.find('p', 'tweet-text') else ""
        )

    @classmethod
    def from_html(cls, html):
        soup = BeautifulSoup(html, "lxml")
        tweets = soup.find_all('li', 'js-stream-item')
        if tweets:
            for tweet in tweets:
                yield cls.from_soup(tweet)
