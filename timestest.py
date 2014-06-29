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
import sys

class author:
  #articles is a dict mapping article url to a tuple (mostviewed score, mostshared score, mostemailed score)  
  viral_boost = 1
  view_boost = 100
  share_boost = 100
  email_boost = 100
  rec_boost = 5
  comment_boost = 15

  def __init__(self, name):
    self.articles = dict()
    self.article_comments = dict()
    self.article_recs = dict()    
    self.name = name

  # Note that score should be lowestrank - docrank
  def add_article(self, resourcetype, articleurl, score):
    if articleurl in self.articles:
      self.articles[articleurl][resourcetype] = score
    else:
      self.articles[articleurl] = dict()
      self.articles[articleurl][resourcetype] = score

  def scrape_article_comments(self, articleurl):
    #if articleurl in self.articles:
    cdata = requests.get(self.comments_url(articleurl))
    print(str(cdata))
    try: 
      commentdata = cdata.json()['results']
      print(articleurl)
      print('Num comments = ' + str(commentdata['totalCommentsFound']))
      self.article_comments[articleurl] = commentdata['totalCommentsFound']
      self.article_recs[articleurl] = 0
      for c in commentdata['comments']:
        self.article_recs[articleurl] += c['recommendations']
      print('Num recommendations = ' + str(self.article_recs[articleurl]))
    except ValueError:
      print('Couldnt find community data for article by ' + self.name + '  ' + articleurl)
      
  def comments_url(self, articleurl, sort='recommended'):
    return 'http://api.nytimes.com/svc/community/v2/comments/url/exact-match.json?url=' + articleurl + "&sort=" + sort + "&api-key=" + os.environ['COMMUNITY_API_KEY2']

  def rating(self):
    #Here are the weights I assign to different parts of an author
    rating = 0
    for art in self.articles:
      a = self.articles[art]
      if "mostviewed" in a:
        rating += a["mostviewed"] * self.view_boost       
      if "mostshared" in a:
        rating += a["mostshared"] * self.share_boost       
      if "mostemailed" in a:
        rating += a["mostemailed"] * self.email_boost  
      if "mostviewed" in a and "mostshared" in a and "mostemailed" in a:
        if a["mostviewed"] < (a["mostshared"] + a["mostemailed"]) / 2:
          rating += (((a["mostshared"] + a["mostemailed"]) / 2) - a["mostviewed"]) * self.viral_boost  
      if art in self.article_comments:
        rating += self.article_comments[art] * self.comment_boost
      if art in self.article_recs:
        rating += self.article_recs[art] * self.rec_boost
  
    return rating

  def export(self):
    score = self.rating()
    top_articles = 0
    total_comments = 0
    total_recs = 0
    for url  in self.articles:
      if url in self.article_comments:
        total_comments += self.article_comments[url]
      if url in self.article_recs:
        total_recs += self.article_recs[url]
      top_articles += 1
    return str(self.name) + "," + str(score) + "," + str(top_articles) + "," + str(total_comments) + "," + str(total_recs)

class NYTimes:

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
    if not os.path.exists('./data/authors'):
      os.makedirs('./data/authors')
    if not os.path.exists('./data/' + time.strftime("%Y")):
      os.makedirs('./data/' + time.strftime("%Y"))
    if not os.path.exists('./data/' + time.strftime("%Y")  + '/' + time.strftime("%m")):
      os.makedirs('./data/' + time.strftime("%Y")+ '/' + time.strftime("%m"))
    self.todays_directory = './data/'+ time.strftime("%Y") + "/" + time.strftime("%m") + '/' 
    dur = tframe
    if dur is 1:
      self.todays_file = self.todays_directory + 'today.csv'
    if dur is 7:
      self.todays_file = self.todays_directory + 'thisweek.csv'
    if dur is 30:
      self.todays_file = self.todays_directory + 'thismonth.csv'
    self.output_file = open(self.todays_file, "w+")
    self.author_file = open('./data/authors/' + time.strftime('%d_%m_%Y') +'tf' + str(dur) +'.csv', "w+")

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
      try:
        for key in requests.get(self.popular_query_url(resourcetype, sections, timeperiod, c * 20)).json()['results']:
          try: 
            r.append(key)
          except ValueError:
            print('Failed while trying to decode json object from request to popular api\n')
        c += 1
        if c % 8 == 0:
          time.sleep(0.95)
      except ValueError:
        print('Fuck this')
    return r

  def get_sections(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    r = requests.get(self.section_list_url(resourcetype))
    return r.json()['results'] 

  def article_tags(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    for article in self.make_request(resourcetype, sections, timeperiod, offset,4):
      self.output_dir.write('Article URL: ' + str(article['url']) + ', ')
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
      if 'url' in article:
        for aut in auts:
          if aut not in self.authors:
            self.authors[aut] = author(aut)
            self.authors[aut].add_article(resourcetype, article['url'], ((calls * 20) - i) / (calls * 20))
          else:
            self.authors[aut].add_article(resourcetype, article['url'], ((calls * 20) - i)/(calls*20))
          self.authors[aut].scrape_article_comments(article['url'])

  def rate_authors(self):
    score_authors = [] 
    for aut in self.authors:
      score_authors.append((aut, self.authors[aut].rating()))
    for (a, s) in sorted(score_authors, key=lambda tup: tup[1], reverse=True)[:100]: 
      self.output_file.write(str(a) + ', ' + str(s) + '\n')
      self.author_file.write(self.authors[a].export() + '\n')

  def analyze(self, tp=30, cs=10):
    x.scrape_authors(resourcetype="mostviewed", timeperiod=tp, calls=cs)
    x.scrape_authors(resourcetype="mostshared", timeperiod=tp, calls=cs)
    x.scrape_authors(resourcetype="mostemailed", timeperiod=tp, calls=cs)
    x.rate_authors()
#    x.export_author_data()

#dur = 1

#if len(sys.argv) > 1:
#  dur = sys.argv[1]

#print(str(dur))
x = NYTimes(1)
x.analyze(tp=1, cs=10)
y = NYTimes(7)
y.analyze(tp=7, cs=10)
z = NYTimes(30)
z.analyze(tp=30, cs=10)
