Sample Usage Of New York Times Most Popular API
===============================================

Documentation on the use of this api can be found here:
http://developer.nytimes.com/docs

Timestest currently scrapes the most popular API
and can then build a model of popular authors and
their recent, popular articles, and then use this
to find the most popular author over the last month,
week, or day. 

To use this class, import timestest

x = timestest.MostPopularInterface()

x.analyze(timeframe=[1,7,30], calls=[1-50])

timeframe refers to whether you want top authors from
the last day, week or month

calls refers to how many batches of atricles to request
If calls=10, we will make 10 requests to the mostpopular 
API, each of which will return the next top 20 articles
(after a little bit of offsetting).

