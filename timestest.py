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

import os
import time

class MostPopularInterface:
  output_dir = ''
  def __init__(self):
    output_dir = './data/' + time.strftime("%d_%m_%Y") + '.csv'

  def popular_query_url(self, resourcetype="mostviewed", sections="all-sections", timeperiod=30, offset=0):
    return 'http://api.nytimes.com/svc/mostpopular/v2/' + resourcetype + "/" + sections + "/" + str(timeperiod) + "?" + os.environ['MOST_POPULAR_KEY'] 

  def section_list_url(self, resourcetype="mostviewed"):
    return 'http://api.nytimes.com/svc/mostpopular/v2/' + resourcetype + '/section-list?' + os.environ['MOST_POPULAR_KEY']

x = MostPopularInterface()

print x.popular_query_url()
print x.section_list_url()


