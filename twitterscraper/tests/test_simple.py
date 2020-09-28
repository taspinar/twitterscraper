import datetime as dt
from twitterscraper import query_js

# TODO: fix logging
import logging
logger = logging.getLogger('twitterscraper')
logger.setLevel(logging.DEBUG)


def test_simple_js():
    call_dict = dict(begindate=dt.date(2018, 5, 5), enddate=dt.date(2018, 5, 7),
                     poolsize=2, lang='en', query='donald john trump', use_proxy=True)
    res = query_js.get_query_data(**call_dict)
    assert len(res) == 78
