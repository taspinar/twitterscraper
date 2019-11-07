from datetime import datetime

from bs4 import BeautifulSoup
from coala_utils.decorators import generate_ordering


@generate_ordering('timestamp', 'id', 'text', 'user', 'replies', 'retweets', 'likes')
class Tweet:
    def __init__(self, username, fullname, user_id, conversation_id, tweet_id, tweet_url, tweet_image, timestamp, timestamp_epochs, replies, retweets,
                 likes, is_retweet, retweeter_username, retweeter_userid, retweet_id,text, html):
        self.username = username.strip('\@')
        self.fullname = fullname
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.tweet_id = tweet_id
        self.tweet_url = tweet_url
        self.tweet_image = tweet_image
        self.timestamp = timestamp
        self.timestamp_epochs = timestamp_epochs
        self.replies = replies
        self.retweets = retweets
        self.likes = likes
        self.is_retweet = is_retweet
        self.retweeter_username = retweeter_username
        self.retweeter_userid = retweeter_userid
        self.retweet_id = retweet_id
        self.text = text
        self.html = html

    @classmethod
    def from_soup(cls, tweet):
        tweet_div = tweet.find('div', 'tweet')
        img_div = tweet.find('div', 'AdaptiveMedia-photoContainer')
        username = tweet_div["data-screen-name"]
        fullname = tweet_div["data-name"]
        user_id = tweet_div["data-user-id"]
        conversation_id = tweet_div["data-conversation-id"]
        tweet_id = tweet_div["data-tweet-id"]
        tweet_url = tweet_div["data-permalink-path"]
        tweet_image = img_div["data-img-url"]
        print('img div' + img_div)
        print('tweet image ' + tweet_image)
        timestamp_epochs = int(tweet.find('span', '_timestamp')['data-time'])
        timestamp = datetime.utcfromtimestamp(timestamp_epochs)
        try:
            retweet_id = tweet_div["data-retweet-id"]
            retweeter_username = tweet_div["data-retweeter"]
            retweeter_userid = tweet_div.find('a', "pretty-link js-user-profile-link")["data-user-id"]
            is_retweet = 1
        except:
            retweet_id = ""
            retweeter_username = ""
            retweeter_userid = ""
            is_retweet = 0

        text = tweet.find('p', 'tweet-text').text or ""
        replies = int(tweet.find(
            'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
            'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
        retweets = int(tweet.find(
            'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
            'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
        likes = int(tweet.find(
            'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
            'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
        html = str(tweet.find('p', 'tweet-text')) or ""
            
        c = cls(username, fullname, user_id, conversation_id, tweet_id, tweet_url, tweet_image, timestamp, timestamp_epochs, replies, retweets, likes,
                 is_retweet, retweeter_username, retweeter_userid, retweet_id, text, html)
        return c

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
                except TypeError:
                    pass  # Incomplete info? Discard!
