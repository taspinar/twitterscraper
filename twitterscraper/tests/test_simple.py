import datetime as dt
from twitterscraper import query_js, ts_logger
import logging


ts_logger.loggerlevel = logging.WARNING


def test_simple_js():
    call_dict = dict(begindate=dt.date(2017, 11, 11), enddate=dt.date(2017, 11, 13),
                     poolsize=3, lang='en', query='foo bar')
    res = query_js.get_query_data(**call_dict)
    assert len(res) == 20
