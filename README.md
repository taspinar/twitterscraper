# Synopsis

A simple script to scrape for Tweets using the Python package requests to
retrieve the content and Beautifullsoup4 to parse the retrieved content.


# Motivation
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

# Installation

To install **twitterscraper**:

```python
(sudo) pip install twitterscraper
```

or you can clone the repository and in the folder containing setup.py

```python
python setup.py install
```

# Code Example

You can easily use TwitterScraper from within python:

```python
from twitterscraper import query_tweets


# All tweets matching either Trump or Clinton will be returned. You will get at
# least 10 results within the minimal possible time/number of requests
for tweet in query_tweets("Trump OR Clinton", 10)[:10]:
    print(tweet.username)
```

You can use any advanced query twitter supports. Simply compile your query at
<https://twitter.com/search-advanced>.

You should get an output like this:

```text
Tweet(user='@WiseFreeman', id='797020313569689601', timestamp='02:17 - 11. Nov. 2016', fullname='Solomon Freeman', text="Chinese Internet Companies Are In Danger After Trump's Victory http://fb.me/5NfxcdTn9\xa0")
Tweet(user='@TheRoseBushes', id='797020313099927552', timestamp='02:17 - 11. Nov. 2016', fullname='The Rose Bushes', text='Democrats Wonder If Bernie Sanders Could Have Beaten Trump http://ift.tt/2fHyWDL\xa0')
Tweet(user='@TvPrefeito', id='797020312869240833', timestamp='02:17 - 11. Nov. 2016', fullname='TvPrefeito', text='Na Casa Branca, Trump diz que vai pedir conselhos a Obama http://tinyurl.com/z97ll3c\xa0pic.twitter.com/aJeAjrldnM')
Tweet(user='@portlandor_agen', id='797020312655241217', timestamp='02:17 - 11. Nov. 2016', fullname='Portland Agent', text='Portland Police Say Anti-Trump Protest Is &#039;Riot&#039; #donald https://dragplus.com/post/id/38524480\xa0…')
Tweet(user='@rpsmybb', id='797020312084905984', timestamp='02:17 - 11. Nov. 2016', fullname='Павел Афонин', text='Electoral College Electors: Electoral College Make Hillary Clinton President on December 19 - Подпишите петицию! http://fb.me/Rlv2qfWH\xa0')
Tweet(user='@Shane_Conneely', id='797020312038703104', timestamp='02:17 - 11. Nov. 2016', fullname='Shane Conneely', text="#Trump's public works scheme has odd historical symmetries, ironically tea-party fear of big gov spending may be the only restraint on him")
Tweet(user='@LavakyMohammed', id='797020311220785152', timestamp='02:17 - 11. Nov. 2016', fullname='Lavaky Mohammed', text='Usa-Un extrémiste Sioniste , milicien de Soros et anti Trump ! pic.twitter.com/PTDag2eQbO')
Tweet(user='@Isethoriginal', id='797020310641983489', timestamp='02:17 - 11. Nov. 2016', fullname='Iseth Goldstein', text='Just curious: If SJW are convinced Trump is a dictator, will they still be eager to repeal the 2nd amendment? Or will they buy mass ammo?')
Tweet(user='@italianfood_age', id='797020310134525952', timestamp='02:17 - 11. Nov. 2016', fullname='Italian Food agent', text='Portland Police Say Anti-Trump Protest Is &#039;Riot&#039; #donald https://dragplus.com/post/id/38524480\xa0…')
Tweet(user='@laurac2605', id='797020310113570817', timestamp='02:17 - 11. Nov. 2016', fullname='Laura Ceccato', text='Why Clinton’s identity politics backfired http://www.spiked-online.com/newsite/article/why-clintons-identity-politics-backfired-trump-election/18960#.WCWah68m09A.twitter\xa0…  very interesting article')
```

You can also use the command line application to get your tweets stored to JSON
right away:

`TwitterScraper "Trump OR Clinton" --limit 100 --output=tweets.json`

# TO DO

- Add caching potentially? Would be nice to be able to resume scraping if
  something goes wrong and have half of the data of a request cached or so.
- Add an example of using a thread pool/asynchio for gathering more tweets in
  parallel.
