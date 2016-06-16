from bs4 import BeautifulSoup
import json
import csv
import urllib2

class Scraper:
	def __init__(self, topics, no_tweets = float('inf'), lang = '', begin_date = '', end_date = '', authors = '', recipients = '', near = '', within = 1, filename = ''):
		self.topic = self.parse_topics(topics)
		self.no_tweets = no_tweets
		#see supported languages at https://dev.twitter.com/web/overview/languages
		self.lang = lang
		self.begin_date = begin_date
		self.end_date = end_date
		self.authors = self.parse_authors(authors)
		self.recipients = self.parse_recipients(recipients)
		self.filename = filename
		self.first_tweet_id = 0
		self.last_tweet_id = 0
		self.collected_tweets = 0
		self.location = self.parse_location(near, within)
		self.writer = csv.writer(open(filename, 'wb'), delimiter="\t")
	
	def parse_topics(*topics):
		if type(topics[1]) is str:
			topics_string = topics[1]
		elif type(topics[1]) is list:
			topics_string = ' '.join(topics[1])
		topics_string = topics_string.replace(' ', '%20')
		return topics_string
	
	def parse_authors(*authors):
		if authors[1]:
			if type(authors[1]) is str:
				authors_string = authors[1]
			elif type(authors[1]) is list:
				authors_string = "%20OR%20from%3A".join(authors[1])
			return authors_string

	def parse_recipients(*recipients):
		if recipients[1]:
			if type(recipients[1]) is str:
				recipients_string = recipients[1]
			elif type(recipients[1]) is list:
				recipients_string = "%20OR%20to%3A".join(recipients[1])
			return recipients_string

	def parse_location(self, location, within):
		if location:
			if type(location) is str:
				location_string = 'near%3A"' + location + '"%20within%3A' + within
			elif type(location) is list:
				location_string = '"geocode%3A' + str(location[0]) + '%2C' + str(location[1]) + '%2C' + within
			return location_string
		
	def is_first_iteration(self):
		if ((self.first_tweet_id == 0) and (self.last_tweet_id == 0)):
			return True
		else:
			return False
		
	def parse_url(self):
		url_1 = "https://twitter.com/search?f=tweets&vertical=default&q="
		url_2 = "https://twitter.com/i/search/timeline?vertical=default&include_available_features=1&include_entities=1&reset_error_state=false&f=tweets&"
		if self.is_first_iteration():
			url = url_1 + self.topic
		else:
			url = url_2 + "&max_position=TWEET-%s-%s&q=" % (self.last_tweet_id, self.first_tweet_id) + self.topic
		if self.lang: url += "%20lang%3A" + self.lang
		if self.begin_date: url += "%20since%3A" + self.begin_date
		if self.end_date: url+= "%20until%3A" + self.end_date
		if self.authors: url+= "%20from%3A" + self.authors
		if self.recipients: url+= "%20to%3A" + self.recipients
		if self.location: url+= '%20' + self.location
		return url

	def scrape_tweets(self):
		url = self.parse_url()
		response = urllib2.urlopen(url).read()
		if self.is_first_iteration():
			html = response
		else:
			html = json.loads(response)['items_html']
		soup = BeautifulSoup(html, "lxml")
		tweets = soup.find_all('li','js-stream-item')
		if self.is_first_iteration():
			if tweets:
				self.first_tweet_id = tweets[0]['data-item-id']
				self.last_tweet_id = tweets[-1]['data-item-id']
			else:
				self.first_tweet_id = -1 
		else:
			if tweets:
				self.last_tweet_id = tweets[-1]['data-item-id']
		return tweets

	def extract_data_from_tweet(self, tweet):
		tweet_user = tweet.find('span','username').text
		tweet_fullname = tweet.find('strong','fullname').text.encode('utf8')
		tweet_text = tweet.find('p','tweet-text')
		if tweet_text:
			tweet_text = tweet_text.text.encode('utf8')
		tweet_html = tweet.find('p','js-tweet-text')
		tweet_id = tweet['data-item-id']
		permalink_path = tweet.find('div','js-original-tweet')['data-permalink-path']
		timestamp = tweet.find('a','tweet-timestamp')['title']
		post  = [tweet_user,tweet_fullname,tweet_text,timestamp]
		return post
		
	def write(self, post):
		if self.filename:
			self.writer.writerow(post)
		else:
			print post
		
	def scrape(self):
		while self.collected_tweets < self.no_tweets and (self.is_first_iteration() or len(tweets)>0):
			tweets = self.scrape_tweets()
			for tweet in tweets:
				self.collected_tweets += 1
				post = self.extract_data_from_tweet(tweet)
				self.write(post)


			

topics = ['Trump', 'Clinton']
filename = 'output.csv'
scraper1 = Scraper(topics, filename = filename)
scraper1.scrape()