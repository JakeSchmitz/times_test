# This is a test of the NYTimes MostPopular API
# Documentation on the API can be found here: 
# http://developer.nytimes.com/docs/most_popular_api/
#
# API Key should be defined in the local environment as MOST_POPULAR_KEY
# Call the API as follows: ([] indicates optional params, {} are required)
#
# http://api.nytimes.com/svc/mostpopular/v2/{mostviewed | mostemailed | mostshared}
# /{all-sections | list of section names }[/share-types]/{1 | 7 | 30}[.response-format]
# ?api-key={your-API-key}
#
#
# Eventually, the goal is to collect data from all 3 popularity vectors and look
# for "weird" things. To start, the goal is to look for a trend in the ratio between
# shares/ emails/ and views, and then look for articles that deviate from the trend
# Look at the authors of articles that deviate from this pattern and try to discern
# the popularity of the author.
#
# If an abnormal percentage of viewers for an article are converted into sharers,
# that would be particularly interesting.
#

from __future__ import print_function
import os
import time
import requests
import json

class MostPopularInterface:
  todays_file = "./data/" + time.strftime("%d_%m_%Y") + ".csv"
  output_dir = open(todays_file, "w+")
  calls_today = 0
  today_began = time
  def __init__(self):
    calls_today = 0
    today_began = time

  def __del__(self):
    self.output_dir.close()

  def popular_query_url(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    return 'http://api.nytimes.com/svc/mostpopular/v2/' + resourcetype + "/" + sections + "/" + str(timeperiod) + "?api-key=" + os.environ['MOST_POPULAR_KEY'] 

  def section_list_url(self, resourcetype="mostviewed"):
    return 'http://api.nytimes.com/svc/mostpopular/v2/' + resourcetype + '/sections-list?api-key=' + os.environ['MOST_POPULAR_KEY']

  def make_request(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    r = requests.get(self.popular_query_url(resourcetype, sections, timeperiod, offset))
    return json.loads(r.text)['results']

  def get_sections(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    r = requests.get(self.section_list_url(resourcetype))
    return json.loads(r.text)['results'] 

  def top_articles(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    for article in self.make_request(resourcetype, sections, timeperiod, offset):
      self.output_dir.write('Article ID: ' + str(article['id']) + ', ')
      self.output_dir.write('Title: '+ article['title'].encode('utf-8') + "\n")

x = MostPopularInterface()

x.top_articles()


