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
# Just to get my feet wet, I'm going to start by finding the most popular authors
#

from __future__ import print_function
import os
import time
import requests
import simplejson
import sys

class author:
  #articles is a dict mapping article id to a tuple (mostviewed score, mostshared score, mostemailed score)  

  def __init__(self):
    self.articles = dict()

  # Note that score should be lowestrank - docrank
  def add_article(self, resourcetype, articleid, score):
    if articleid in self.articles:
      self.articles[articleid][resourcetype] = score
    else:
      self.articles[articleid] = dict()
      self.articles[articleid][resourcetype] = score
      
  def rating(self):
    #Here are the weights I assign to different parts of an author
    viral_boost = 2
    view_boost = 5
    share_boost = 5
    email_boost = 5
    rating = 0
    for art in self.articles:
      a = self.articles[art]
      if "mostviewed" in a:
        rating += a["mostviewed"] * view_boost       
      if "mostshared" in a:
        rating += a["mostshared"] * share_boost       
      if "mostemailed" in a:
        rating += a["mostemailed"] * email_boost  
      if "mostviewed" and "mostshared" and "mostemailed" in a:
              if a["mostviewed"] < (a["mostshared"] + a["mostemailed"]) / 2:
          rating += (((a["mostshared"] + a["mostemailed"]) / 2) - a["mostviewed"]) * viral_boost  
    return rating

class MostPopularInterface:

  todays_file = "./data/" + time.strftime("%d_%m_%Y") + ".csv"
  calls_today = 0
  today_began = time
  authors = dict()
  shared_authors = dict()
  emailed_authors = dict()

  def __init__(self, tframe=1):
    calls_today = 0
    today_began = time
    if not os.path.exists('./data'):
      os.makedirs('./data')
    if not os.path.exists('./data/daily'):
      os.makedirs('./data/daily')
    if not os.path.exists('./data/monthly'):
      os.makedirs('./data/monthly')
    if len(sys.argv) > 1:
      dur = sys.argv[1]
    else:
      dur = tframe
    if dur == 1:
      self.todays_file = "./data/daily/" + time.strftime("%d_%m_%Y") + ".csv"
    if dur == 7:
      self.todays_file = "./data/monthly/" + time.strftime("%m_%Y") + ".csv"
    self.output_file = open(self.todays_file, "w+")
    self.author_file = open("./data/authors" + time.strftime("%d_%m_%Y") + ".csv", "w+")

  def __del__(self):
    self.output_file.close()
    self.author_file.close()

  def popular_query_url(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    return 'http://api.nytimes.com/svc/mostpopular/v2/' + resourcetype + "/" + sections + "/" + str(timeperiod) + "?api-key=" + os.environ['MOST_POPULAR_KEY2'] + '&offset=' + str(offset)

  def section_list_url(self, resourcetype="mostviewed"):
    return 'http://api.nytimes.com/svc/mostpopular/v2/' + resourcetype + '/sections-list?api-key=' + os.environ['MOST_POPULAR_KEY2']

  def make_request(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0, calls=1):
    r = list()
    c = 0
    for x in range(calls):
      for key in simplejson.loads(requests.get(self.popular_query_url(resourcetype, sections, timeperiod, c * 20)).text)['results']:
        r.append(key)
      c += 1
      if c % 8 == 0:
        time.sleep(0.95)
    return r

  def get_sections(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    r = requests.get(self.section_list_url(resourcetype))
    return simplejson.loads(r.text)['results'] 

  def article_tags(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    for article in self.make_request(resourcetype, sections, timeperiod, offset,4):
      self.output_dir.write('Article ID: ' + str(article['id']) + ', ')
      self.output_dir.write('Title: '+ article['title'].encode('utf-8') + " Author(s): " + article['byline'].strip('By ').lower().replace(' and ', ', ').title().encode('utf-8') + "\n")
      keywords = '\tKeywords: '
      for des in article['des_facet']:
        keywords += des.encode('utf-8') + ' '
      people = '\tPeople: '
      for person in article['per_facet']:
        people += person.encode('utf-8') + ' ' 
      orgs = '\tOrganizations: '
      for org in article['org_facet']:
        orgs += org.encode('utf-8') + ' '
      places = '\tPlaces: '
      for loc in article['geo_facet']:
        places += loc.encode('utf-8') + ' '
      self.output_dir.write(keywords + '\n' + people + '\n' + orgs + '\n' + places + '\n')

  def scrape_authors(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0, calls=1):
    for i, article in enumerate(self.make_request(resourcetype, sections, timeperiod, offset, calls)):
      auts = article['byline'].strip('By ').replace('and ', ',').replace(', ,', ',').replace(', ', ',').title().encode('utf-8').split(',')
      if ',' in auts: auts.remove(',')
      if '' in auts: auts.remove('')
      if 'id' in article:
        for aut in auts:
          if aut not in self.authors:
            self.authors[aut] = author()
            self.authors[aut].add_article(resourcetype, article['id'], (calls * 20) - i)
          else:
            self.authors[aut].add_article(resourcetype, article['id'], (calls * 20) - i)
            #self.authors[aut][str(article['id'])] = (calls * 20) - i

  def rate_authors(self):
    score_authors = [] 
    for aut in self.authors:
      score_authors.append((aut, self.authors[aut].rating()))
    for (a, s) in sorted(score_authors, key=lambda tup: tup[1], reverse=True)[:100]: 
      self.output_file.write(str(a) + ', ' + str(s) + '\n')

  def analyze(self, tp=30, cs=10):
    x.scrape_authors(resourcetype="mostviewed", timeperiod=tp, calls=cs)
    x.scrape_authors(resourcetype="mostshared", timeperiod=tp, calls=cs)
    x.scrape_authors(resourcetype="mostemailed", timeperiod=tp, calls=cs)
    x.rate_authors()

dur = 1

if len(sys.argv) > 1:
  dur = sys.argv[1]

#print(str(dur))
x = MostPopularInterface()
x.analyze(tp=dur, cs=25)

