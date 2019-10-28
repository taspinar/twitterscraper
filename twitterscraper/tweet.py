from datetime import datetime

from bs4 import BeautifulSoup
from coala_utils.decorators import generate_ordering


@generate_ordering('timestamp', 'id', 'text', 'user', 'replies', 'retweets', 'likes')
class Tweet:
    def __init__(
        self,
        # user name & id
        screen_name, username, user_id,
        # tweet basic data
        tweet_id, tweet_url, timestamp, timestamp_epochs,
        # tweet text
        text, text_html, links, hashtags,
        # tweet media
        is_media, img_urls, video_url,
        # tweet actions numbers
        likes, retweets, replies, is_replied,
        # detail of reply to others
        is_reply_to, parent_tweet_id, reply_to_users
    ):
        # user name & id
        self.screen_name = screen_name
        self.username = username
        self.user_id = user_id
        # tweet basic data
        self.tweet_id = tweet_id
        self.tweet_url = tweet_url
        self.timestamp = timestamp
        self.timestamp_epochs = timestamp_epochs
        # tweet text
        self.text = text
        self.text_html = text_html
        self.links = links
        self.hashtags = hashtags
        # tweet media
        self.is_media = is_media
        self.img_urls = img_urls
        self.video_url = video_url
        # tweet actions numbers
        self.likes = likes
        self.retweets = retweets
        self.replies = replies
        self.is_replied = is_replied
        # detail of reply to others
        self.is_reply_to = is_reply_to
        self.parent_tweet_id = parent_tweet_id
        self.reply_to_users = reply_to_users

    @classmethod
    def from_soup(cls, tweet):
        tweet_div = tweet.find('div', 'tweet')

        # user name & id
        screen_name = tweet_div["data-screen-name"].strip('@')
        username = tweet_div["data-name"]
        user_id = tweet_div["data-user-id"]

        # tweet basic data
        tweet_id = tweet_div["data-tweet-id"]  # equal to 'data-item-id'
        tweet_url = tweet_div["data-permalink-path"]
        timestamp_epochs = int(tweet.find('span', '_timestamp')['data-time'])
        timestamp = datetime.utcfromtimestamp(timestamp_epochs)

        # tweet text
        soup_html = tweet_div \
            .find('div', 'js-tweet-text-container') \
            .find('p', 'tweet-text')
        text_html = str(soup_html) or ""
        text = soup_html.text or ""
        links, hashtags = cls.extract_links_and_hashtags(soup_html)

        # tweet media
        # --- imgs
        soup_imgs = tweet_div.find_all('div', 'AdaptiveMedia-photoContainer')
        img_urls = [
            img['data-image-url'] for img in soup_imgs
        ] if soup_imgs else []

        # --- videos
        video_div = tweet_div.find('div', 'PlayableMedia-container')
        video_url = video_div.find('a')['href'] if video_div else ''
        is_media = True if img_urls or video_url else False
        # eliminate video_url from links for duplicate
        links = [link for link in links if link != video_url]

        # tweet actions numbers
        action_div = tweet_div.find('div', 'ProfileTweet-actionCountList')

        # --- likes
        likes = int(action_div.find(
            'span', 'ProfileTweet-action--favorite').find(
            'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
        # --- RT
        retweets = int(action_div.find(
            'span', 'ProfileTweet-action--retweet').find(
            'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
        # --- replies
        replies = int(action_div.find(
            'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
            'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
        is_replied = False if replies == '0' else True

        # detail of reply to others
        # - reply to others
        parent_tweet_id = tweet_div['data-conversation-id']  # parent tweet

        if tweet_id == parent_tweet_id:
            is_reply_to = False
            parent_tweet_id = ''
            reply_to_users = []
        else:
            is_reply_to = True
            soup_reply_to_users = \
                tweet_div.find('div', 'ReplyingToContextBelowAuthor') \
                .find_all('a')
            reply_to_users = [{
                'screen_name': user.text.strip('@'),
                'user_id': user['data-user-id']
            } for user in soup_reply_to_users]

        return cls(
            # user name & id
            screen_name, username, user_id,
            # tweet basic data
            tweet_id, tweet_url, timestamp, timestamp_epochs,
            # tweet text
            text, text_html, links, hashtags,
            # tweet media
            is_media, img_urls, video_url,
            # tweet actions numbers
            likes, retweets, replies, is_replied,
            # detail of reply to others
            is_reply_to, parent_tweet_id, reply_to_users
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
                except TypeError:
                    pass  # Incomplete info? Discard!

    @staticmethod
    def extract_links_and_hashtags(soup_html):
        links = []
        hashtags = []  # 'hashflag' is hashtag + emoji

        for atag in soup_html.find_all('a'):
            class_ = atag.get('class', None)
            if 'hashtag' in atag['href']:
                # atag['href'] like '/hashtag/NBA?src=hash' -> 'NBA'
                hashtag = atag['href'].split('?')[0].split('/')[-1]
                hashtags.append(hashtag)

            elif class_:
                # for links
                if 'twitter-timeline-link' in class_ and \
                        'pic.twitter' not in atag.text:  # eliminate picture
                    expanded_url = atag.get('data-expanded-url', None)
                    link = expanded_url if expanded_url else atag['href']
                    links.append(link)

        return links, hashtags
