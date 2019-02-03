from bs4 import BeautifulSoup


class User:
    def __init__(self, user=None, full_name="", location="", blog="", date_joined=None, id=None, tweets=0, 
        following=0, followers=0, likes=0, lists=0):
        self.user = user
        self.full_name = full_name
        self.location = location
        self.blog = blog
        self.date_joined = date_joined
        self.id = id
        self.tweets = tweets
        self.following = following
        self.followers = followers
        self.likes = likes
        self.lists = lists
        
    @classmethod
    def from_soup(self, tag_prof_header, tag_prof_nav):
        """
        Returns the scraped user data from a twitter user page.

        :param tag_prof_header: captures the left hand part of user info
        :param tag_prof_nav: captures the upper part of user info
        :return: Returns a User object with captured data via beautifulsoup
        """

        self.user= tag_prof_header.find('a', {'class':'ProfileHeaderCard-nameLink u-textInheritColor js-nav'})['href'].strip("/") 
        self.full_name = tag_prof_header.find('a', {'class':'ProfileHeaderCard-nameLink u-textInheritColor js-nav'}).text
        
        location = tag_prof_header.find('span', {'class':'ProfileHeaderCard-locationText u-dir'}) 
        if location is None:
            self.location = "None"
        else: 
            self.location = location.text.strip()

        blog = tag_prof_header.find('span', {'class':"ProfileHeaderCard-urlText u-dir"})
        if blog is None:
            blog = "None"
        else:
            self.blog = blog.text.strip() 

        date_joined = tag_prof_header.find('div', {'class':"ProfileHeaderCard-joinDate"}).find('span', {'class':'ProfileHeaderCard-joinDateText js-tooltip u-dir'})['title']
        if date_joined is None:
            self.data_joined = "Unknown"
        else:    
            self.date_joined = date_joined.strip()

        self.id = tag_prof_nav.find('div',{'class':'ProfileNav'})['data-user-id']
        tweets = tag_prof_nav.find('span', {'class':"ProfileNav-value"})['data-count']
        if tweets is None:
            self.tweets = 0
        else:
            self.tweets = int(tweets)

        following = tag_prof_nav.find('li', {'class':"ProfileNav-item ProfileNav-item--following"}).\
        find('span', {'class':"ProfileNav-value"})['data-count']
        if following is None:
            following = 0
        else:
            self.following = int(following)

        followers = tag_prof_nav.find('li', {'class':"ProfileNav-item ProfileNav-item--followers"}).\
        find('span', {'class':"ProfileNav-value"})['data-count']
        if followers is None:
            self.followers = 0
        else:
            self.followers = int(followers)    
        
        likes = tag_prof_nav.find('li', {'class':"ProfileNav-item ProfileNav-item--favorites"}).\
        find('span', {'class':"ProfileNav-value"})['data-count']
        if likes is None:
            self.likes = 0
        else:
            self.likes = int(likes)    
        
        lists = tag_prof_nav.find('li', {'class':"ProfileNav-item ProfileNav-item--lists"})
        if lists is None:
            self.lists = 0
        elif lists.find('span', {'class':"ProfileNav-value"}) is None:    
            self.lists = 0
        else:    
            lists = lists.find('span', {'class':"ProfileNav-value"}).text    
            self.lists = int(lists)
        return(self)

    @classmethod
    def from_html(self, html):
        soup = BeautifulSoup(html, "lxml")
        user_profile_header = soup.find("div", {"class":'ProfileHeaderCard'})
        user_profile_canopy = soup.find("div", {"class":'ProfileCanopy-nav'})
        if user_profile_header and user_profile_canopy:
            try:
                return self.from_soup(user_profile_header, user_profile_canopy)
            except AttributeError:
                pass  # Incomplete info? Discard!
            except TypeError:
                pass  # Incomplete info? Discard!
