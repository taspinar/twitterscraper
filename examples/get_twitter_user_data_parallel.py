from twitterscraper.query import query_user_info
import pandas as pd
from multiprocessing import Pool
from IPython.display import display
import sys

global twitter_user_info
twitter_user_info = []


def get_user_info(twitter_user):
    """
    An example of using the query_user_info method
    :param twitter_user: the twitter user to capture user data
    :return: twitter_user_data: returns a dictionary of twitter user data
    """
    user_info = query_user_info(user=twitter_user)
    twitter_user_data = {}
    twitter_user_data["user"] = user_info.user
    twitter_user_data["fullname"] = user_info.full_name
    twitter_user_data["location"] = user_info.location
    twitter_user_data["blog"] = user_info.blog
    twitter_user_data["date_joined"] = user_info.date_joined
    twitter_user_data["id"] = user_info.id
    twitter_user_data["num_tweets"] = user_info.tweets
    twitter_user_data["following"] = user_info.following
    twitter_user_data["followers"] = user_info.followers
    twitter_user_data["likes"] = user_info.likes
    twitter_user_data["lists"] = user_info.lists

    return twitter_user_data


def main(args):
    users = []

    for arg in args:
        users.append(arg)

    pool_size = len(users)
    if pool_size < 8:
        pool = Pool(pool_size)
    else:
        pool = Pool(8)

    for user in pool.map(get_user_info, users):
        twitter_user_info.append(user)

    cols = ['id', 'fullname', 'date_joined', 'location', 'blog', 'num_tweets', 'following', 'followers', 'likes',
            'lists']
    data_frame = pd.DataFrame(twitter_user_info, index=users, columns=cols)
    data_frame.index.name = "Users"
    data_frame.sort_values(by="followers", ascending=False, inplace=True, kind='quicksort', na_position='last')
    display(data_frame)


if __name__ == '__main__':
    main(sys.argv[1:])

