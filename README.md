# Synopsis

A simple script to scrape for Tweets using the Python package requests to
retrieve the content and Beautifullsoup4 to parse the retrieved content.


# 1. Motivation
Twitter has provided [REST API's](https://dev.twitter.com/rest/public) which can
be used by developers to access and read Twitter data. They have also provided
a [Streaming API](https://dev.twitter.com/streaming/overview) which can be used
to access Twitter Data in real-time.

Most of the software written to access Twitter data provide a library which
functions as a wrapper around Twitters Search and Streaming API's and therefore
are limited by the limitations of the API's.

With Twitter's Search API you can only sent 180 Requests every 15 minutes. With
a maximum number of 100 tweets per Request this means you can mine for
4 x 180 x 100 = 72.000 tweets per hour. By using TwitterScraper you are not
limited by this number but by your internet speed/bandwith and the number of
instances of TwitterScraper you are willing to start.


One of the bigger disadvantages of the Search API is that you can only access
Tweets written in the **past 7 days**. This is a major bottleneck for anyone
looking for older past data to make a model from. With TwitterScraper there is
no such limitation.

Per Tweet it scrapes the following information:
+ Username and Full Name
+ Tweet-id
+ Tweet text
+ Tweet timestamp
+ No. of likes
+ No. of replies
+ No. of retweets
 

# 2. Installation and Usage

To install **twitterscraper**:

```python
(sudo) pip install twitterscraper
```

or you can clone the repository and in the folder containing setup.py

```python
python setup.py install
```

## 2.2 The CLI

You can use the command line application to get your tweets stored to JSON
right away:

`twitterscraper Trump --limit 100 --output=tweets.json`

`twitterscraper Trump -l 100 -o tweets.json`

Omit the limit to retrieve all tweets. You can at any time abort the scraping
by pressing Ctrl+C, the scraped tweets will be stored safely in your JSON file.


## 2.3 Composing advanced queries
You can use any advanced query twitter supports. Simply compile your query at
<https://twitter.com/search-advanced>. After you compose your advanced search, copy the part of the URL 
between q= and the first subsequent &. 

For example, from the URL
`https://twitter.com/search?l=&q=Trump%20near%3A%22Seattle%2C%20WA%22%20within%3A15mi%20since%3A2017-05-02%20until%3A2017-05-05&src=typd&lang=en`

you need to copy the following part:
`Trump%20near%3A%22Seattle%2C%20WA%22%20within%3A15mi%20since%3A2017-05-02%20until%3A2017-05-05`



You can use the CLI with the advanced query, the same way as a simple query:

+ based on a daterange: 
```twitterscraper Trump%20since%3A2017-01-03%20until%3A2017-01-04 -o tweets.json```

+ based on a daterange and location: 
```twitterscraper Trump%20near%3A"Seattle%2C%20WA"%20within%3A15mi%20since%3A2017-05-02%20until%3A2017-05-05 -o tweets.json```

+ based on a specific author: 
```twitterscraper Trump%20from%3AAlWest13 -o tweets.json```



# 3. Output

All of the retrieved Tweets are stored in the indicated output file. The contents of the output file will look like:
```
[{"fullname": "Rupert Meehl", "id": "892397793071050752", "likes": "1", "replies": "0", "retweets": "0", "text": "Latest: Trump now at lowest Approval and highest Disapproval ratings yet. Oh, we're winning bigly here ...\n\nhttps://projects.fivethirtyeight.com/trump-approval-ratings/?ex_cid=rrpromo\u00a0\u2026", "timestamp": "2017-08-01T14:53:08", "user": "Rupert_Meehl"}, {"fullname": "Barry Shapiro", "id": "892397794375327744", "likes": "0", "replies": "0", "retweets": "0", "text": "A former GOP Rep quoted this line, which pretty much sums up Donald Trump. https://twitter.com/davidfrum/status/863017301595107329\u00a0\u2026", "timestamp": "2017-08-01T14:53:08", "user": "barryshap"}, (...)
]
```

## 3.1 Opening the output file
In order to correctly handle all possible characters in the tweets (think of chinese or arabic characters), the output is saved as utf-8 encoded bytes. That is why you could see text like ""\u30b1\u30f3\u3055\u307e\u30fe ..." in the output file. 

What you should do is open the file with the proper encoding:
```
import codecs, json
filename = 'output.json'
with codecs.open(filename, 'r', 'utf-8') as f:
    tweets = json.load(f, encoding='utf-8')
```

![Example of output with chinese characters](https://user-images.githubusercontent.com/4409108/30702318-f05bc196-9eec-11e7-8234-a07aabec294f.PNG)

# TO DO

- Add caching potentially? Would be nice to be able to resume scraping if
  something goes wrong and have half of the data of a request cached or so.
- Add an example of using a thread pool/asynchio for gathering more tweets in
  parallel.
- Use RegExp for retrieving the information from the scraped page (instead of Beautifullsoup4). 
  This might solve the problem of the HTML parser not working properly on some linux distributions.
