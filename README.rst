|Downloads| |Downloads_month| |PyPI version| |GitHub contributors|

.. |Downloads| image:: https://pepy.tech/badge/twitterscraper
   :target: https://pepy.tech/project/twitterscraper
.. |Downloads_month| image:: https://pepy.tech/badge/twitterscraper/month
   :target: https://pepy.tech/project/twitterscraper/month
.. |PyPI version| image:: https://badge.fury.io/py/twitterscraper.svg
   :target: https://badge.fury.io/py/twitterscraper
.. |GitHub contributors| image:: https://img.shields.io/github/contributors/taspinar/twitterscraper.svg
   :target: https://github.com/taspinar/twitterscraper/graphs/contributors


Synopsis
========

A simple script to scrape for Tweets using the Python package requests
to retrieve the content and Beautifulsoup4 to parse the retrieved
content.

1. Motivation
=============

Twitter has provided `REST
API's <https://dev.twitter.com/rest/public>`__ which can be used by
developers to access and read Twitter data. They have also provided a
`Streaming API <https://dev.twitter.com/streaming/overview>`__ which can
be used to access Twitter Data in real-time.

Most of the software written to access Twitter data provide a library
which functions as a wrapper around Twitters Search and Streaming API's
and therefore are limited by the limitations of the API's.

With Twitter's Search API you can only sent 180 Requests every 15
minutes. With a maximum number of 100 tweets per Request this means you
can mine for 4 x 180 x 100 = 72.000 tweets per hour. By using
TwitterScraper you are not limited by this number but by your internet
speed/bandwith and the number of instances of TwitterScraper you are
willing to start.

One of the bigger disadvantages of the Search API is that you can only
access Tweets written in the **past 7 days**. This is a major bottleneck
for anyone looking for older past data to make a model from. With
TwitterScraper there is no such limitation.

Per Tweet it scrapes the following information:
 + Tweet-id
 + Tweet-url
 + Tweet text
 + Tweet html
 + Links inside Tweet
 + Hashtags inside Tweet
 + Image URLS inside Tweet
 + Video URL inside Tweet
 + Tweet timestamp
 + Tweet Epoch timestamp
 + Tweet No. of likes
 + Tweet No. of replies
 + Tweet No. of retweets
 + Username
 + User Full Name / Screen Name
 + User ID
 + Tweet is an reply to
 + Tweet is replied to
 + List of users Tweet is an reply to
 + Tweet ID of parent tweet

 
In addition it can scrape for the following user information:
 + Date user joined
 + User location (if filled in)
 + User blog (if filled in)
 + User No. of tweets
 + User No. of following
 + User No. of followers
 + User No. of likes
 + User No. of lists
 + User is verified


2. Installation and Usage
=========================

To install **twitterscraper**:

.. code:: python

    (sudo) pip install twitterscraper

or you can clone the repository and in the folder containing setup.py

.. code:: python

    python setup.py install

If you prefer more isolation you can build a docker image

.. code:: python

    docker build -t twitterscraper:build .

and run your container with:

.. code:: python


    docker run --rm -it -v/<PATH_TO_SOME_SHARED_FOLDER_FOR_RESULTS>:/app/data twitterscraper:build <YOUR_QUERY>

2.2 The CLI
-----------

You can use the command line application to get your tweets stored to
JSON right away. Twitterscraper takes several arguments:

-  ``-h`` or ``--help`` Print out the help message and exits.

-  ``-l`` or ``--limit`` TwitterScraper stops scraping when *at least*
   the number of tweets indicated with ``--limit`` is scraped. Since
   tweets are retrieved in batches of 20, this will always be a multiple
   of 20. Omit the limit to retrieve all tweets. You can at any time abort the
   scraping by pressing Ctrl+C, the scraped tweets will be stored safely
   in your JSON file.

-  ``--lang`` Retrieves tweets written in a specific language. Currently
   30+ languages are supported. For a full list of the languages print
   out the help message.

-  ``-bd`` or ``--begindate`` Set the date from which TwitterScraper
   should start scraping for your query. Format is YYYY-MM-DD. The
   default value is set to 2006-03-21. This does not work in combination with ``--user``.

-  ``-ed`` or ``--enddate`` Set the enddate which TwitterScraper should
   use to stop scraping for your query. Format is YYYY-MM-DD. The
   default value is set to today. This does not work in combination with ``--user``.

-  ``-u`` or ``--user`` Scrapes the tweets from that users profile page.
   This also includes all retweets by that user. See section 2.2.4 in the examples below
   for more information.

-  ``--profiles`` : Twitterscraper will in addition to the tweets, also scrape for the profile
   information of the users who have written these tweets. The results will be saved in the
   file userprofiles_<filename>.

-  ``-p`` or ``--poolsize`` Set the number of parallel processes
   TwitterScraper should initiate while scraping for your query. Default
   value is set to 20. Depending on the computational power you have,
   you can increase this number. It is advised to keep this number below
   the number of days you are scraping. For example, if you are
   scraping from 2017-01-10 to 2017-01-20, you can set this number to a
   maximum of 10. If you are scraping from 2016-01-01 to 2016-12-31, you
   can increase this number to a maximum of 150, if you have the
   computational resources. Does not work in combination with ``--user``.

-  ``-o`` or ``--output`` Gives the name of the output file. If no
   output filename is given, the default filename 'tweets.json' or 'tweets.csv'
   will be used.

-  ``-c`` or ``--csv`` Write the result to a CSV file instead of a JSON file.

-  ``-d`` or ``--dump``: With this argument, the scraped tweets will be
   printed to the screen instead of an outputfile. If you are using this
   argument, the ``--output`` argument doe not need to be used.

-  ``-ow`` or ``--overwrite``: With this argument, if the output file already exists
   it will be overwritten. If this argument is not set (default) twitterscraper will
   exit with the warning that the output file already exists.


2.2.1 Examples of simple queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below is an example of how twitterscraper can be used:

``twitterscraper Trump --limit 1000 --output=tweets.json``

``twitterscraper Trump -l 1000 -o tweets.json``

``twitterscraper Trump -l 1000 -bd 2017-01-01 -ed 2017-06-01 -o tweets.json``



2.2.2 Examples of advanced queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use any advanced query Twitter supports. An advanced query
should be placed within quotes, so that twitterscraper can recognize it
as one single query.

Here are some examples:

-  search for the occurence of 'Bitcoin' or 'BTC':
   ``twitterscraper "Bitcoin OR BTC" -o bitcoin_tweets.json -l 1000``
-  search for the occurence of 'Bitcoin' and 'BTC':
   ``twitterscraper "Bitcoin AND BTC" -o bitcoin_tweets.json -l 1000``
-  search for tweets from a specific user:
   ``twitterscraper "Blockchain from:VitalikButerin" -o blockchain_tweets.json -l 1000``
-  search for tweets to a specific user:
   ``twitterscraper "Blockchain to:VitalikButerin" -o blockchain_tweets.json -l 1000``
-  search for tweets written from a location:
   ``twitterscraper "Blockchain near:Seattle within:15mi" -o blockchain_tweets.json -l 1000``

You can construct an advanced query on `Twitter Advanced Search <https://twitter.com/search-advanced?lang=en>`__ or use one of the operators shown on `this page <https://lifehacker.com/search-twitter-more-efficiently-with-these-search-opera-1598165519>`__.
Also see `Twitter's Standard operators <https://developer.twitter.com/en/docs/tweets/search/guides/standard-operators.html>`__



2.2.3 Examples of scraping user pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also scraped all tweets written or retweetet by a specific user.
This can be done by adding the boolean argument ``-u / --user`` argument.
If this argument is used, the search term should be equal to the username.

Here is an example of scraping a specific user:

``twitterscraper realDonaldTrump --user -o tweets_username.json``

This does not work in combination with ``-p``, ``-bd``, or ``-ed``.

The main difference with the example "search for tweets from a specific user" in section 2.2.2 is that this method really scrapes
all tweets from a profile page (including retweets).
The example in 2.2.2 scrapes the results from the search page (excluding retweets).


2.3 From within Python
----------------------

You can easily use TwitterScraper from within python:

::

    from twitterscraper import query_tweets

    if __name__ == '__main__':
        list_of_tweets = query_tweets("Trump OR Clinton", 10)

        #print the retrieved tweets to the screen:
        for tweet in query_tweets("Trump OR Clinton", 10):
            print(tweet)

        #Or save the retrieved tweets to file:
        file = open(“output.txt”,”w”)
        for tweet in query_tweets("Trump OR Clinton", 10):
            file.write(tweet.encode('utf-8'))
        file.close()


2.4 Scraping for retweets
----------------------

A regular search within Twitter will not show you any retweets.
Twitterscraper therefore does not contain any retweets in the output.

To give an example: If user1 has written a tweet containing ``#trump2020`` and user2 has retweetet this tweet,
a search for ``#trump2020`` will only show the original tweet.

The only way you can scrape for retweets is if you scrape for all tweets of a specific user with the ``-u / --user`` argument.


2.5 Scraping for User Profile information
----------------------
By adding the argument ``--profiles`` twitterscraper will in addition to the tweets, also scrape for the profile information of the users who have written these tweets.
The results will be saved in the file "userprofiles_<filename>".

Try not to use this argument too much. If you have already scraped profile information for a set of users, there is no need to do it again :)
It is also possible to scrape for profile information without scraping for tweets.
Examples of this can be found in the examples folder.


3. Output
=========

All of the retrieved Tweets are stored in the indicated output file. The
contents of the output file will look like:

::

    [{"fullname": "Rupert Meehl", "id": "892397793071050752", "likes": "1", "replies": "0", "retweets": "0", "text": "Latest: Trump now at lowest Approval and highest Disapproval ratings yet. Oh, we're winning bigly here ...\n\nhttps://projects.fivethirtyeight.com/trump-approval-ratings/?ex_cid=rrpromo\u00a0\u2026", "timestamp": "2017-08-01T14:53:08", "user": "Rupert_Meehl"}, {"fullname": "Barry Shapiro", "id": "892397794375327744", "likes": "0", "replies": "0", "retweets": "0", "text": "A former GOP Rep quoted this line, which pretty much sums up Donald Trump. https://twitter.com/davidfrum/status/863017301595107329\u00a0\u2026", "timestamp": "2017-08-01T14:53:08", "user": "barryshap"}, (...)
    ]

3.1 Opening the output file
---------------------------

In order to correctly handle all possible characters in the tweets
(think of Japanese or Arabic characters), the output is saved as utf-8
encoded bytes. That is why you could see text like
"\u30b1 \u30f3 \u3055 \u307e \u30fe ..." in the output file.

What you should do is open the file with the proper encoding:

.. figure:: https://user-images.githubusercontent.com/4409108/30702318-f05bc196-9eec-11e7-8234-a07aabec294f.PNG

   Example of output with Japanese characters

3.1.2 Opening into a pandas dataframe
---------------------------

After the file has been opened, it can easily be converted into a pandas DataFrame

::

    import pandas as pd
    df = pd.read_json('tweets.json', encoding='utf-8')
