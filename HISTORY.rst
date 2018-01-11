# twitterscraper changelog

## 0.x.x

TBD
## 0.4.2 ( 2018-01-09 )
### Fixed
- Fixed backward compatability of the new --lang parameter by placing it at the end of all arguments.

## 0.4.1 ( 2018-01-07 )
### Fixed
- Fixed --lang functionality by passing the lang parameter from its CL argument form to the generater url. 

## 0.4 ( 2017-12-19 )
-----------
### Added
- Added "-bd / --begindate" command line arguments to set the begin date of the query
- Added "-ed / --enddate" command line arguments to set the end date of the query.
- Added "-p / --poolsize" command line arguments which can change the number of parallel processes.
  Default number of parallel processes is set to 20.

### Improved
- Outputfile is only created if tweets are actually retrieved.

### Removed
- The ´query_all_tweets' method in the Query module is removed. Since twitterscraper is starting parallel processes by default,
  this method is no longer necessary.

### Changed
- The 'query_tweets' method now takes as arguments query, limit, begindate, enddate, poolsize.
- The 'query_tweets_once' no longer has the argument 'num_tweets'
- The default value of the 'retry' argument of the 'query_single_page' method has been increased from 3 to 10.
- The ´query_tweets_once' method does not log to screen at every single scrape, but at the end of a batch.

## 0.3.3 ( 2017-12-06 )
-----------
### Added
-PR #61: Adding --lang functionality which can retrieve tweets written in a specific language. 
-PR #62: Tweet class now also contains the tweet url. This closes https://github.com/taspinar/twitterscraper/issues/59

## 0.3.2 ( 2017-11-12 )
-----------
### Improved
-PR #55: Adding --dump functionality which dumps the scraped tweets to screen, instead of an outputfile.


## 0.3.1 ( 2017-11-05 )
-----------
### Improved
-PR #49: scraping of replies, retweets and likes is improved.


## 0.3.0 ( 2017-08-01 )
-----------
### Added
- Tweet class now also includes 'replies', 'retweets' and 'likes'


## 0.2.7 ( 2017-01-10 )
-----------
### Improved
- PR #26: use ``requests`` library for HTTP requests. Makes the use of urllib2 / urllib redundant. 
### Added: 
- changelog.txt for GitHub
- HISTORY.rst for PyPi
- README.rst for PyPi

## 0.2.6 ( 2017-01-02 )
-----------
### Improved 
- PR #25: convert date retrieved from timestamp to day precision
