import datetime as dt
import pytest
from twitterscraper import query, query_js
import logging


@pytest.mark.parametrize(
    'query_fn, is_data_request',
    [
        (query_js.get_query_data, True),
        (query.query_tweets, False),
    ]
)
def test_get_multiple_correct_count(query_fn, is_data_request):
    # expect
    expected_counts_by_date = {
        dt.date(2017, 11, 10): 0,
        dt.date(2017, 11, 11): 29,
        dt.date(2017, 11, 12): 32,
        dt.date(2017, 11, 13): 78,
        dt.date(2017, 11, 14): 55,
        dt.date(2017, 11, 15): 51,
        dt.date(2017, 11, 16): 45,
        dt.date(2017, 11, 17): 60,
        dt.date(2017, 11, 18): 40,
        dt.date(2017, 11, 19): 32,
        dt.date(2017, 11, 20): 44,
        dt.date(2017, 11, 21): 74,
        dt.date(2017, 11, 22): 0,
    }

    # retrieve
    call_dict = dict(begindate=dt.date(2017, 11, 11), enddate=dt.date(2017, 11, 22),
                     poolsize=3, lang='en')
    call_dict['query'] = 'alphabet soup'
    res = query.query_tweets(**call_dict)

    res = query_fn(**call_dict)

    # validate
    actual_counts_by_date = {
        d: len([r for r in res if r.timestamp.date() == d])
        for d in expected_counts_by_date.keys()
    }

    for k in expected_counts_by_date:
        print(k, expected_counts_by_date.get(k), actual_counts_by_date.get(k))
    assert expected_counts_by_date == actual_counts_by_date


@pytest.mark.parametrize(
    'query_fn, is_data_request',
    [
        (query_js.get_query_data, True),
        (query.query_tweets, False),
    ]
)
def test_same_count_multiple_tries(query_fn, is_data_request):
    lengths = []
    for _ in range(10):
        call_dict = dict(begindate=dt.date(2019, 2, 2), enddate=dt.date(2019, 2, 3),
                         poolsize=1, lang='en')
        call_dict['query'] = 'lapp'

        res = query_fn(**call_dict)
        if is_data_request:
            lengths.append(len(res['tweets']))
        else:
            lengths.append(len(res))

    assert len(set(lengths)) == 1  # all the same length
