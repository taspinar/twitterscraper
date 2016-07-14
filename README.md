## Synopsis

A simple script to scrape for Tweets using the Python package Beautifullsoup (bs4). To use it, first [install bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/). 

## Code Example
TwitterScraper is very versatile and can be initialized with one or more keywords:
```
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