# Synopsis

A simple script to scrape for Tweets using the Python package Beautifullsoup (bs4). To use it, first [install bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/). 
---

# Motivation
Twitter has provided [REST API's](https://dev.twitter.com/rest/public) which can be used by developers to access and read Twitter data. They have also provided a [Streaming API](https://dev.twitter.com/streaming/overview) which can be used to access Twitter Data in real-time. 
Most of the software written to access Twitter data provide a library which functions as a wrapper around Twitters Search and Streaming API's and therefore are limited by the limitations of the API's. 


With Twitter's Search API you can only sent 180 Requests every 15 minutes. With a maximum number of 100 tweets per Request this means you can mine for 4 x 180 x 100 = 72.000 tweets per hour. By using TwitterScraper you are not limited by this number but by your internet speed/bandwith and the number of instances of TwitterScraper you are willing to start.


One of the bigger disadvantages of the Search API is that you can only access Tweets written in the **past 7 days**. This is a major bottleneck for anyone looking for older past data to make a model from. With TwitterScraper there is no such limitation.
---


# Code Example
TwitterScraper is very versatile and can be initialized with **one or more keywords**:
```python
topic = 'Trump'
topics = ['Trump', 'Clinton'] #if there are more than one keywords, use an array. 
scraper1 = Scraper(topics)

scraper1.scrape()
collecting inf number of Tweets on the topics: ['Trump', 'Clinton']
[u'@TheLegalTerms', '753638968785186816', '10:15 - 14 jul. 2016', 'Law News Blog', 'Trump\xe2\x80\x99s policies would be unconstitutional and will be challenged if adopted, ACLU says http://dlvr.it/Lp5DLn\xc2\xa0pic.twitter.com/ZsWF5Oh1II']
[u'@CovertAnonymous', '753638968466542596', '10:15 - 14 jul. 2016', 'Anonymous', 'GuardianUS: Who is potential Trump VP pick Mike Pence? http://trib.al/uibbBVk\xc2\xa0pic.twitter.com/AeFXrcyROE']
[u'@SocMediaNation', '753638968248250368', '10:15 - 14 jul. 2016', 'Social Media Nation', "Company sends Trump 6,000 bags of green tea to make him 'smarter' http://on.mash.to/29KGyVq\xc2\xa0"]
[u'@AllForLaw', '753638968009166849', '10:15 - 14 jul. 2016', 'All for Law News', 'Trump\xe2\x80\x99s policies would be unconstitutional and will be challenged if adopted, ACLU says http://dlvr.it/Lp5DLl\xc2\xa0pic.twitter.com/t55AoPQqtL']
[u'@LaMananaDigital', '753638967904382978', '10:15 - 14 jul. 2016', 'Diario La Ma\xc3\xb1ana', '#Mundo Trump anunciar\xc3\xa1 el viernes su f\xc3\xb3rmula para la vicepresidencia http://www.lamanana.com.ve/9455/trump-anunciara-el-viernes-su-formula-para-la-vicepresidencia\xc2\xa0\xe2\x80\xa6pic.twitter.com/S036zD3YkK']
...
...
```



If an upper limit is given to the **number of Tweets** to be collected, it will stop once this amount of Tweets has been collected:
```python
scraper = Scraper(topics, 100000)
scraper.scrape()
```



If an **outputfile** is given, the result will be written to file, otherwise to screen:
```python
filename = 'output.csv'
scraper = Scraper(topics, 10000, filename = filename)
scraper.scrape()
```



The **language** in which the to be collected Tweets have to be written can be specified. For a full list of the 34 supported languages go to [Twitter](https://dev.twitter.com/web/overview/languages).
```python
filename = 'output.csv'
scraper = Scraper(topics, 10000, lang='en', filename = filename)
scraper.scrape()
```



A **begin date** and/or **end date** can be specified to limit the date-range in which you want to search.
```python
filename = 'output.csv'
scraper = Scraper(topics, 10000, filename = filename, begin_date = '2016-01-01', end_date = '2016-06-16')
scraper.scrape()
```



The **author(s)** of the Tweets as well as the **recipient(s)** can be specified. 
```python
filename = 'output.csv'
author = 'realDonaldTrump'
authors = ['realDonaldTrump', 'marcorubio']
recipient = 'HillaryClinton'
recipients = ['HillaryClinton', 'billclinton']
scraper = Scraper(topics, 10000, authors=author, filename = filename)
scraper2 = Scraper(topics, 10000, authors=authors, filename = filename)
scraper3 = Scraper(topics, 10000, recipients=recipient, filename = filename)
scraper4 = Scraper(topics, 10000, recipients=recipients, filename = filename)
scraper.scrape()
```



The **location** of the Tweets can be specified. This can also be done with **longitude and latitude coordinates**. 
```python
filename = 'output.csv'
scraper = Scraper(topics, near='Florida', within='20mi', filename = filename)
scraper2 = Scraper(topics, near=[51.5073510,-0.1277580], within='20km', filename = filename)
scraper.scrape()
```
---