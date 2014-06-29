# This class represents a New York Times writer, or columnist with a top article


class author:
  #articles is a dict mapping article id to a tuple (mostviewed score, mostshared score, mostemailed score)  

  def __init__(self):
    self.articles = dict()

  # Note that score should be lowestrank - docrank
  def add_article(self, resourcetype, articleid, score):
    if articeid in self.articles:
      self.articles[articleid][resourcetype] = score
    else:
      self.articles[articleid] = dict()
      self.articles[articleid][resourcetype] = score
      
  def rating(self):
    #Here are the weights I assign to different parts of an author
    viral_boost = 1
    view_boost = 3
    share_boost = 4
    email_boost = 6
    rating = 0
    for a in articles:
      if "mostviewed" in a:
        rating += a["mostviewed"] * view_boost       
      if "mostshared" in a:
        rating += a["mostshared"] * share_boost       
      if "mostemailed" in a:
        rating += a["mostemailed"] * email_boost  
      if "mostviewed" and "mostshared" and "mostemailed" in a:
        rating += ((a["mostshared"] + a["mostemailed"]) / 2) * viral_boost  
    return rating
