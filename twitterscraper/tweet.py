from datetime import datetime

from bs4 import BeautifulSoup
from coala_utils.decorators import generate_ordering


@generate_ordering('timestamp', 'id', 'text', 'user', 'replies', 'reply_to_id', 'retweets', 'likes')
class Tweet:
    def __init__(self, user, fullname, id, url, timestamp, text, reply_to_id, replies, retweets, likes, html):
        self.user = user
        self.fullname = fullname
        self.id = id
        self.url = url
        self.timestamp = timestamp
        self.text = text
        self.replies = replies
        self.retweets = retweets
        self.likes = likes
        self.html = html
        self.reply_to_id = reply_to_id

    @classmethod
    def from_soup(cls, tweet):
        return cls(
            user=tweet.find('span', 'username').text[1:],
            fullname=tweet.find('strong', 'fullname').text,
            id=tweet['data-item-id'],
            url = tweet.find('div', 'tweet')['data-permalink-path'],
            timestamp=datetime.utcfromtimestamp(
                int(tweet.find('span', '_timestamp')['data-time'])),
            text=tweet.find('p', 'tweet-text').text or "",
            replies = tweet.find(
                'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
                    'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
            retweets = tweet.find(
                'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
                    'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
            likes = tweet.find(
                'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
                    'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
            html=str(tweet.find('p', 'tweet-text')) or "",
            reply_to_id = tweet.findChildren()[0]['data-conversation-id'] or '0',
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
