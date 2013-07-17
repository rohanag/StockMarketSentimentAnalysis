'''
good test cases
washington fun
'''
from __future__ import division
import porter
import cgi
import datetime
import urllib
import webapp2
import re
import sys
import urllib
import urllib2
import json as simplejson
from re import split

from collections import defaultdict
from datetime import date
from google.appengine.ext import db
from google.appengine.api import users
#from pygeocoder import Geocoder
import stockretriever
import ra2616Test
from ra2616Test  import getSentiment
from xml.dom import minidom
from HTMLParser import HTMLParser
    
class Tweets(db.Model):
    """Models an individual Guestbook entry with author, content, and date."""
    company = db.StringProperty(multiline=True)
    tweetId = db.StringProperty(multiline=True)
    tweetAccount = db.StringProperty()
    tweetText = db.StringProperty(multiline=True)
        
class FacebookPost(db.Model):
    """Models an individual Guestbook entry with author, content, and date."""
    company = db.StringProperty(multiline=True)
    facebookId = db.StringProperty(multiline=True)
    facebookText = db.TextProperty()
    

class MainPage(webapp2.RequestHandler):
                      
    def get(self):
        self.response.write('<html><body style="font-family:calibri;color:black;i;background-color:orange;"><h1>Sentiment Analysis of news related to Corporations</h1><h2>Nandita Rao - nr2445 Rohan Agrawal - ra2616 Tushar Suresh - ts2762</h2>')
        self.response.write("""<b><font size = "4" >Please enter the name of the company</font></b>
        <form method = "post">
        <input type = "textarea" name = "company"></input>
        <input type = "submit" ></input>
        </form>""")

        #self.response.write('</body></html>')
		
    def post(self):
               
        tweetList = []
        facebookPostList = []
        self.response.write('<html><body style="font-family:calibri;color:blue;i;background-color:lightcyan;"><h1>What\'s going on with the company</h1>')
        topBusTwAcc = ["CNNMoney","MarketWatch","CNBC","Forbes","ft"]
		
        company = self.request.get('company')
        
        strs1="No tweets found!!! Search for something better!!"        
        strs2 = "Fetching related data from twitter"
        strs3 = "Fetching related data from facebook"
        
        #self.response.write('<p>%s</p>' %strs2)
        
        for name in topBusTwAcc:
            #self.response.write('<p>%s</p>' %name)
            tweetSearch = urllib.urlopen("http://search.twitter.com/search.json?q=from:"+name+"%20"+company+"&include_entities=true&result_type=mixed&lang%3Aen")
            dict = simplejson.loads(tweetSearch.read())
        

            if not dict["results"]:
                continue
        
            for result in dict["results"]: # result is a list of dictionaries
                tweetText =result["text"]
                tweetUserId = result["from_user_id_str"]
                tweetLanguage = result["iso_language_code"]
                if tweetLanguage == 'en':
                    self.tweet = Tweets()
                    self.tweet.company = company
                    self.tweet.tweetAccount = name
                    self.tweet.tweetId = tweetUserId
                    self.tweet.tweetText = tweetText
                    self.tweet.put()
        
        
        #self.response.write('<p>%s</p>' %strs3)
        
        facebookSearch = urllib.urlopen("https://graph.facebook.com/search?q="+company+"&type=post")
        dict = simplejson.loads(facebookSearch.read())
        
        if not dict["data"]:
            self.response.write('<p>%s</p>' % strs1)
            return
            
        for result in dict["data"]: # result is a list of dictionaries
            if "message" in result:
                facebookText = result["message"]
                if len(facebookText) > 500:
                    facebookText = facebookText[:100]
            else:
                continue
            facebookId =result["id"]
            self.facebookPost = FacebookPost()
            self.facebookPost.company = company
            self.facebookPost.facebookId = facebookId
            self.facebookPost.facebookText = facebookText
            self.facebookPost.put()
            
         
        #nandita: added a few imports, changed get_historical_prices, added get_symbol_from_name


        
        stocks = stockretriever.StockRetriever()
        
        #symbols = 'MSFT'
        
        
        #print symbols

        def get_symbol_from_name(name):
            name = name.replace(' ', '%20')
            response = urllib.urlopen('http://d.yimg.com/autoc.finance.yahoo.com/autoc?query='+ name + '&callback=YAHOO.Finance.SymbolSuggest.ssCallback')
            a = response.read()
            a = a[39:-1]
            a = simplejson.loads(a)
            try:
                return a['ResultSet']['Result'][0]['symbol']
            except:
                return None
        '''
        Functions from http://goldb.org/ystockquote.html
        '''

        def __request(symbol, stat):
            url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
            return urllib.urlopen(url).read().strip().strip('"')
                                    

        def get_all_financial_data(symbol):
            """
            Get all available quote data for the given ticker symbol.
    
            Returns a dictionary.
            """
            values = __request(symbol, 'l1c1va2xj1b4j4dyekjm3m4rr5p5p6s7').split(',')
            data = {}
            data['stock_exchange'] = values[4]
            data['ebitda'] = values[7]
            data['dividend_per_share'] = values[8]
            data['52_week_high'] = values[11]
            data['52_week_low'] = values[12]
            data['50day_moving_avg'] = values[13]
            data['200day_moving_avg'] = values[14]
            return data
            
    
        def get_historical_prices(symbol):
            """
            Get historical prices for the given ticker symbol.
            Date format is 'YYYYMMDD'
    
            Returns a nested list.
            Date,Open,High,Low,Close,Volume,AdjClose
            , '20120101', '20130101'
            """
            
            start_datee = date.today()
            end_date = str(start_datee.year) + str(start_datee.day).zfill(2) + str(start_datee.month).zfill(2) 
            start_date = str(start_datee.year-1) + str(start_datee.day).zfill(2) + str(start_datee.month).zfill(2) 
            
            url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
                'd=%s&' % str(int(end_date[4:6]) - 1) + \
                'e=%s&' % str(int(end_date[6:8])) + \
                'f=%s&' % str(int(end_date[0:4])) + \
                'g=w&' + \
                'a=%s&' % str(int(start_date[4:6]) - 1) + \
                'b=%s&' % str(int(start_date[6:8])) + \
                'c=%s&' % str(int(start_date[0:4])) + \
                'ignore=.csv'
            days = urllib.urlopen(url).readlines()
            data = [day[:-2].split(',') for day in days]    #removes the \n at the end of the record
            return data[:50]
            
        symbols = get_symbol_from_name(company)
        self.response.write('<p>%s</p>' %symbols)
        
        class HTMLStripper(HTMLParser):
            def __init__(self):
                self.reset()
                self.fed = []
            def handle_data(self, d):
                self.fed.append(d)
            def get_data(self):
                return ''.join(self.fed)

        def parseResult(result):
            '''
            This function takes in xml result of gnews and parses it.
            Returns an array of tuples in the form - [(headline1,content1),(headline2,content2),...(headline10,content10)]
            '''
    
            #To clean html tags
            s = HTMLStripper()
            root = minidom.parseString(result)
    
            newsList = root.getElementsByTagName('item')
        
            gNews = []
            prevText = ''
            for event in newsList:
                try:
                    newsTitle = event.getElementsByTagName('title')[0].firstChild.nodeValue
                    newsText = event.getElementsByTagName('description')[0].firstChild.nodeValue
                    s.feed(newsText)
                    newsText = s.get_data()
    
                    #Encoding to utf8 format because it is web data
                    newsTitle = newsTitle.encode('utf8')
                    newsText = newsText.encode('utf8')
                    if newsText.startswith(prevText):
                        newsText = newsText[len(prevText):]
                    prevText += newsText
                    gNews.append((str(newsTitle), str(newsText)))
        
                except Exception, e:
                    #Can get unicode encode error
                    self.response.write('<p>%s</p>' %e)
        
            return gNews

        def getNews(searchQuery):
            '''
            This function takes a search term and calls the google news feed.
            Calls parseResult which returns an array of news articles.
            '''
            data = {'q': searchQuery , 'output':'rss'}
            gNewsQuery = urllib.urlencode(data)
            gNewsQuery = "https://news.google.com/news/feeds?" + gNewsQuery
        
            gNewsResult = urllib2.urlopen(gNewsQuery).read()

            return parseResult(gNewsResult)

                   
        try:
            s = 'What Yahoo Finance has to say about your Company : '
            self.response.write('<p><h2><b>%s</b></h2></p>' %s)
            
            s = 'Some important data about the stocks : '
            self.response.write('<p><h3><b>%s</b></h3></p>' %s)
            
            data = get_all_financial_data(symbols)
            
            if data['stock_exchange'] == '"N/A"' or data['stock_exchange'] == 'N/A':
                raise Exception
            
            Stock_exchange = 'Stock Exchange : '+data['stock_exchange']
            TwoHun_movavg = '200 day moving average : '+data['200day_moving_avg']
            Fiftwo_whigh = '52 week high : '+data['52_week_high']
            Fifday_movavg = '50 day moving average : '+data['50day_moving_avg']
            Fiftwo_wlow = '52 week low : '+data['52_week_low']
            Ebitda = 'Ebitda : '+data['ebitda']
            Divi_per_share = 'Dividend per share : '+data['dividend_per_share']
            self.response.write('<p>%s</p>' %Stock_exchange)
            self.response.write('<p>%s</p>' %TwoHun_movavg)
            self.response.write('<p>%s</p>' %Fiftwo_whigh)
            self.response.write('<p>%s</p>' %Fifday_movavg)
            self.response.write('<p>%s</p>' %Fiftwo_wlow)
            self.response.write('<p>%s</p>' %Ebitda)
            self.response.write('<p>%s</p>' %Divi_per_share)
            
        except Exception ,e:
            strs8 = 'This company information is not available with Yahoo'
            self.response.write('<p>%s</p>' %e)
        
        try:
            
            s = 'Stocks - News feed :'
            self.response.write('<p><h3><b>%s</b></h3></p>' %s)
            news = stocks.get_news_feed(symbols)
            c = 0
            for newsitems in news:
                title = ''
                desc = ''
                if newsitems['title']:
                    print 'TITLE: ', newsitems['title'].encode('utf-8')
                    title = newsitems['title'] + ' '
                else:
                    title = ''
            
                if newsitems['description']:
                    desc = newsitems['description']
                r = ra2616Test.getSentiment(title + desc)
                
                if(r == 0):
                    c = c - 1
                else:
                    c = c + 1
                   
            if c > 0:
                s = "Overall sentiment - Positive"
            elif c < 0:
                s = "Overall sentiment - Negative"
            else:
                s = "Overall sentiment - Neutral"
            self.response.write('<p><b>%s</b></p>' %s)
            for newsitems in news:
                title = ''
                desc = ''
                if newsitems['title']:
                    print 'TITLE: ', newsitems['title'].encode('utf-8')
                    title = newsitems['title'] + ' '
                else:
                    title = ''
            
                if newsitems['description']:
                    desc = newsitems['description']
                self.response.write('<p>%s</p>' %(title+desc))
            
        except Exception,e:
            strs9 = 'This company information is not available with Yahoo'
            self.response.write('<p>%s</p>' %e)
            
        try:
            s = 'Historical data : '
            self.response.write('<p><h3><b>%s</b><h3></p>' %s)
            
            data = get_historical_prices(symbols)
            if data[0][0] != 'Date':
                raise Exception
            self.response.write('<table border="1">')
            self.response.write('<tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th><th>Adj Close</th>')
            flag = True
            for d in data:
                if(flag):
                    flag = False
                    continue
                else:
                    self.response.write('<tr><td>%s</td>' %d[0])
                    self.response.write('<td>%s</td>' %d[1])
                    self.response.write('<td>%s</td>' %d[2])
                    self.response.write('<td>%s</td>' %d[3])
                    self.response.write('<td>%s</td>' %d[4])
                    self.response.write('<td>%s</td>' %d[5])
                    self.response.write('<td>%s</td>' %d[6])
                
            self.response.write('</table>')
        except Exception , e:
            strs7 = 'This company information is not available with Yahoo'
            self.response.write('<p>%s</p>' %strs7)
            
        
        s = 'What Google News has to say about your Company'
        self.response.write('<p><h2><b>%s</b></h2></p>' %s)
        c = 0
        for newstitle,news in getNews(company):
            r = ra2616Test.getSentiment(news)
            
            if(r == 0):
                c = c - 1
            else:
                c = c + 1
            
        if c > 0:
            s = "Overall sentiment - Positive"
        elif c < 0:
                s = "Overall sentiment - Negative"
        else:
            s = "Overall sentiment - Neutral"
        self.response.write('<p><b>%s</b></p>' %s)    
            
        for newstitle,news in getNews(company):
            self.response.write('<p><i>%s</i></p>' %newstitle)
            self.response.write('<p>%s</p>' %news)
        
        class Tweet :
            def __init__(self,l,c) :
                self.label = l
                self.content = c
                self.score = 0.0
        
            def stopwordsRemover(self,c) :
                c = c.split()
                c = self.removeStopwords(c)
                self.content = " ".join(c)
                
        class Document : 
            def __init__(self) :
                self.vocabulary = []
                self.c1Prob = 0.0
                self.c0Prob = 0.0
                self.condProb = {}
    
            def removeStopwords(self, tokens) :
                pattern = '^[0-9]+$'
                stopwords = ['rt','amp','i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', '']
                
                noStopwordsText = []
                for word in tokens :
                        if word in stopwords or word[:4] == 'http' or re.match(pattern,word) or re.match('@',word):
                                noStopwordsText.append('')
                        else: 
                                noStopwordsText.append(word)
                        
                noStopwordsText = filter(None, noStopwordsText)
                return noStopwordsText
            
            def loadPriorParameters(self,priorParamFile) :
                inputFile = open(priorParamFile,"rb")
                line = inputFile.readline().strip()
                
                parameters = line.split()
                
                self.c1Prob = float(parameters[0])
                self.c0Prob = float(parameters[1])
                
                line = inputFile.readline().strip()
                
                while line :
                        parameters = line.split()
                        self.condProb[(parameters[0], int(parameters[1]))] = float(parameters[2])
                        self.vocabulary.append(parameters[0])
                        
                        line = inputFile.readline().strip()
                
                self.vocabulary = list(set(self.vocabulary))
                
            def testModel(self, tweet) :
                import math
                
                v = []
                for eachWord in tweet :
                        v.append(eachWord)
                score = []
                maxScore = float('-inf')
                maxLabel = ' '
                for c1 in range(0,2) :
                        if c1 == 0 :
                                priorProb = self.c0Prob
                        else :
                                priorProb = self.c1Prob
                        score.append(math.log(priorProb))

                        for eachTerm in self.vocabulary :
                                if eachTerm in v :
                                        score[c1] = score[c1] + math.log(self.condProb[(eachTerm,c1)])
                                        
                                else :
                                        score[c1] = score[c1] + math.log(1.0 - self.condProb[(eachTerm,c1)])

                        
                        if score[c1] > maxScore :
                                maxScore = score[c1]
                                maxLabel = str(c1)
                
                
                return maxLabel

            def scoreTweet(self, testTweet):
                testTweet = self.removeStopwords(testTweet.split())
        
                label = self.testModel(testTweet)
                return label
        
        def returnSentiment(testTweet) :
            #Call these two lines first to load the model file
            testingFile = Document()
            testingFile.loadPriorParameters("model.file")
        
            #Use the testingFile object to call scoreTweet with the test tweet as arguments.
            #It will return 1 for positive, 0 for negative
            result = testingFile.scoreTweet(testTweet)
            return result

        
        strs4 = "Buzz on twitter about your company"
        self.response.write('<p><h2><b>%s</b></h2></p>' %strs4)
        
        for name in topBusTwAcc:
            if (name == "ft"):
                strs4 = "Financial Times says : "
            else:
                strs4 = name+" says : "
            self.response.write('<p><h3><b>%s</b></h3></p>' %strs4)
            tweets = db.GqlQuery("SELECT * "
                                    "FROM Tweets "
                                    "WHERE company = :1 AND tweetAccount = :2",
                                    company,name)
                                    
            
            if tweets.count(4) == 0:
                s = "Sorry!! No news about your company here... "
                self.response.write('<p>%s</p>' %s)
                continue                
        
            
            for tweet in tweets:
                c = 0
                r = returnSentiment(tweet.tweetText)
                if(r == '0'):
                    c = c - 1
                else:
                    c = c + 1
            if c > 0:
                s = "Overall sentiment - Positive"
            elif c < 0:
                s = "Overall sentiment - Negative"
            else:
                s = "Overall sentiment - Neutral"
            self.response.write('<p><b>%s</b></p>' %s)    
                
            for tweet in tweets:
                self.response.write('<p>%s</p>' %(tweet.tweetText))
            
            
             
        
               
        posts = db.GqlQuery("SELECT * "
                                "FROM FacebookPost "
                                "WHERE company = :1",
                                company)
        
        strs5 = "General buzz on Facebook about the company : "
        self.response.write('<p><h2><b>%s</b></h2></p>' %strs5)
        c = 0
        for post in posts:
            r = returnSentiment(post.facebookText)
            if(r == '0'):
                c = c - 1
            else:
                c = c + 1
            
        if c > 0:
            s = "Overall sentiment - Positive"
        elif c < 0:
            s = "Overall sentiment - Negative"
        else:
            s = "Overall sentiment - Neutral"
        self.response.write('<p><b>%s</b></p>' %s)
        
        for post in posts:    
            self.response.write('<p>%s</p>' %(post.facebookText))
       
                                                       
        self.response.write('</body></html>')

        

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)