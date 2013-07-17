#nandita: added a few imports, changed get_historical_prices, added get_symbol_from_name
import urllib as u
import urllib2
import json
import string
from datetime import date
import sys

import stockretriever
import ra2616Test
from ra2616Test  import getSentiment
stocks = stockretriever.StockRetriever()

symbols = 'MSFT'

def get_symbol_from_name(name):
    name = name.replace(' ', '%20')
    response = urllib2.urlopen('http://d.yimg.com/autoc.finance.yahoo.com/autoc?query='+ name + '&callback=YAHOO.Finance.SymbolSuggest.ssCallback')
    a = response.read()
    a = a[39:-1]
    a = json.loads(a)
    try:
        return a['ResultSet']['Result'][0]['symbol']
    except:
        return None
'''
Functions from http://goldb.org/ystockquote.html
'''

def __request(symbol, stat):
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
    return u.urlopen(url).read().strip().strip('"')


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
    days = u.urlopen(url).readlines()
    data = [day[:-2].split(',') for day in days]    #removes the \n at the end of the record
    return data[:250]

try:
    #nandita: this function returns an array of [Date,Open,High,Low,Close,Volume,AdjClose] for the symbol
    data = get_historical_prices(symbols)
    if data[0][0] != 'Date':
        this_should_raise_an_error()
    for d in data:
        print d
    print len(data)
except Exception , e:
    print 'unable to get stock historical prices', e
    
try:
    #nandita: look at this function above, it returns a dictionary with many types of financial data, which goes in to the second table i mentioned
    data = get_all_financial_data(symbols)
    print data['stock_exchange']
    if data['stock_exchange'] == '"N/A"' or data['stock_exchange'] == 'N/A':
        this_should_raise_an_error()
    print data
    print len(data)
except:
    print 'unable to get financial data'
        
try:
    #nandita: gets news articles related to symbol, returns a dictionary, i have printed title and description below in the for loop
    # the dictionary has the following fields: title, link, description, pubDate
    news = stocks.get_news_feed(symbols)
    for newsitems in news:
        title = ''
        desc = ''
        if newsitems['title']:
            print 'TITLE: ', newsitems['title'].encode('utf-8')
            title = newsitems['title'] + ' '
        else:
            title = ''
            
        if newsitems['description']:
            print 'DESCRP: ', newsitems['description'].encode('utf-8')  
            desc = newsitems['description']
        ra2616Test.getSentiment(title + desc)
except:
    print 'couldnt get yahoo feed'

symbol = get_symbol_from_name('microsoft corporation')
print symbol