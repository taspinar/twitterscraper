from datetime import datetime

from bs4 import BeautifulSoup
from coala_utils.decorators import generate_ordering


@generate_ordering('timestamp', 'id', 'text', 'user', 'replies', 'retweets', 'likes')
class Tweet:
    def __init__(self, user, id, timestamp, fullname, text, replies, retweets, likes):
        self.user = user
        self.id = id
        self.timestamp = timestamp
        self.fullname = fullname
        self.text = text
        self.replies = replies
        self.retweets = retweets
        self.likes = likes

    @classmethod
    def from_soup(cls, tweet):
        return cls(
            user=tweet.find('span', 'username').text[1:],
            id=tweet['data-item-id'],
            timestamp=datetime.utcfromtimestamp(
                int(tweet.find('span', '_timestamp')['data-time'])),
            fullname=tweet.find('strong', 'fullname').text,
            text=tweet.find('p', 'tweet-text').text or "",
            replies = tweet.find('div', 'ProfileTweet-action--reply').find('span', 'ProfileTweet-actionCountForPresentation').text or '0',
            retweets = tweet.find('div', 'ProfileTweet-action--retweet').find('span', 'ProfileTweet-actionCountForPresentation').text or '0',
            likes = tweet.find('div', 'ProfileTweet-action--favorite').find('span', 'ProfileTweet-actionCountForPresentation').text or '0'
        )

    @classmethod
    def from_html(cls, html):
        soup = BeautifulSoup(html, "lxml")
        tweets = soup.find_all('li', 'js-stream-item')
        if tweets:
            for tweet in tweets:
                try:
                    yield cls.from_soup(tweet)
                except AttributeError:
                    pass  # Incomplete info? Discard!
