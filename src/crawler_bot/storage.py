"""Module that holds all the classes for storing information
"""
import queue
import time
import json
from diagrams import Diagram
from diagrams.alibabacloud.compute import ECS
import os
from urllib.parse import urlparse
import requests
from protego import Protego

from src.crawler_bot.config import DEFAULT_CRAWL_DELAY, DIAGRAMM_MAX_URL_LENGTH, CUSTOM_USER_AGENT
from src.crawler_bot.custom_logging import Logger


class HTMLDatabaseEntry:
  """Class to safe a single HTML database entry

  Attributes:
    url: url of the html page
    html: the html of the page
    extracted_urls: list of extracted urls
    relevant: bool that shows if entry is relevant or not
    distances: dictionary with all distances from the document to the
                possible categories
    guessed_category: the guessed category by the classifier
"""

  def __init__(self, url: str, html: str, extracted_urls: list[str],
               relevant: bool, distances: dict, relative_distances: dict,
               guessed_category: str):
    """Inits HTMLDatabaseEntry

    Args:
      url: url of the html page
      html: the html of the page
      extracted_urls: list of extracted urls
      relevant: bool that shows if entry is relevant or not
      distances: dictionary with all distances from the document to the
                  possible categories
      relative_distances: dictionary with all relative distances from the
                            document to the possible categories
      guessed_category: the guessed category by the classifier
    """
    self.url = url
    self.html = html
    self.extracted_urls = extracted_urls
    self.relevant = relevant
    self.distances = distances
    self.relative_distances = relative_distances
    self.guessed_category = guessed_category


def get_relative_distance(single_entry: HTMLDatabaseEntry) -> float:
  """Returns the relative_distance value of a single entry of the category
      the entry was classified as

  Returns:
    float of the relative_distance, 0 if entry was classified as not relevant
  """
  if not single_entry.relevant:
    return 0

  return single_entry.relative_distances[single_entry.guessed_category]


class HTMLDatabase:
  """class that stores all the HTML content

  Attributes:
    name: name of the class for logging
    database: list that contains all the HTML content
    logger: the custom_logging module to log all kinds of messages
  """

  def __init__(self, logger: Logger):
    """Inits HTMLDatabase

    Args:
      logger: instance of the custom logging module
    """
    self.name = "HTMLDatabase"
    self.database: list[HTMLDatabaseEntry] = []
    self.logger = logger
    self.logger.log_info(self.name, "initialized")

  def add_html_document(self, url: str, html_document: str, relevant: bool,
                        extracted_urls: list[str], distances: dict,
                        relative_distances: dict,
                        guessed_category: str) -> None:
    """Stores the given HTML document in the database

    Args:
      url: the url the html document belongs to
      html_document: the html document that needs to be added
      relevant: bool that shows if the html document is considered relevant
      extracted_urls: list of extracted urls
      distances: dictionary with all distances from the document to the
                  possible categories
      relative_distances: dictionary with all relative distances from the
                            document to the possible categories
      guessed_category: the guessed category by the classifier

    Returns:
      None
    """
    self.logger.log_debug(self.name, "adding HTML document for " + url)
    # create HTMLDatabaseEntry object and write to database
    self.database.append(
        HTMLDatabaseEntry(html=html_document,
                          url=url,
                          relevant=relevant,
                          extracted_urls=extracted_urls,
                          distances=distances,
                          relative_distances=relative_distances,
                          guessed_category=guessed_category))

  def is_empty(self) -> bool:
    """Checks if html database is empty

    Returns:
      boolean that shows if database is empty
    """
    return len(self.database) == 0

  def sort_after_relevance(self) -> None:
    """Sorts the database using the relative_distances

    Returns:
      None
    """
    self.database.sort(key=get_relative_distance)

  def get_list_of_relevant_urls(self) -> list[str]:
    """Returns the url of all entries that are relevant

    Returns:
      list of urls
    """
    result = [
        a.url + "," + a.guessed_category
        for a in self.database
        if a.relevant is True
    ]
    return result

  def to_json(self) -> str:
    """Returns the database in JSON format so it can be safed

    Returns:
      string of the database in JSON format
    """
    document = []
    # iterate through all items and create JSON document
    for element in self.database:
      document.append({
          "url": element.url,
          #"html document": element.html,
          "relevant": element.relevant,
          "distances": element.distances,
          "relative distances": element.relative_distances,
          "extracted urls": element.extracted_urls,
          "guessed category": element.guessed_category
      })
    return json.dumps(document)


class UnprocessedHTMLDatabase:
  """Keeps a list of unprocessed HTML documents

  Attributes:
    database: contains the list of touples (url, html content)
    logger: the custom_logging module to log all kinds of messages
    name: name of the instance for logging

"""

  def __init__(self, logger: Logger):
    """Inits UnprocessedHtmlDatabase

    Args:
      logger: instance of the custom logging module
    """
    self.database = []
    self.logger = logger
    self.name = "UnprocessedHTMLDatabase"

    self.logger.log_info(self.name, "initialized")

  def add_entry(self, url: str, is_seed: bool, html_document: str) -> None:
    """Adds a new touple of url and html document to the database

    Args:
      url: string of the crawled page
      is_seed: is url seed?
      html_document: string of the recieved html document

    Returns:
      None
    """
    self.database.append((url, is_seed, html_document))

  def get_entry(self) -> (str, bool, str):
    """Returns an entry from the database

    Returns:
      triple of (url, is_seed,html document)
    """
    # return new url if available
    if len(self.database) == 0:
      return None, None, None
    else:
      return self.database.pop()

  def is_empty(self) -> bool:
    """Checks if database is empty

    Returns:
      bool that shows if database is empty
    """
    return len(self.database) == 0

  def to_json(self) -> str:
    """Returns the database in JSON format so it can be safed

    Returns:
      string of the database in JSON format
    """
    document = []
    # iterate through all items and create JSON document
    for (url, is_seed, html) in self.database:
      document.append({
          "url": url,
          "is_seed": str(is_seed),
          "html document": html
      })
    return json.dumps(document)


class CrawledURLs:
  """Contains all the already crawled URLs

  Attributes:
    name: name of this instance for logging
    crawled_urls: list of all already crawled urls
    logger: the custom_logging module to log all kinds of messages
    crawl_limit: amount of urls that should be crawled
"""

  def __init__(self, logger: Logger, crawl_limit: int = 0):
    """Inits CrawledURLs

    Args:
      logger: the custom logging module
      crawl_limit: amount of urls that will be crawled, 0 = no limit
    """
    self.name = "CrawledURLS"
    self.crawled_urls = []
    self.logger = logger
    self.crawl_limit = crawl_limit
    self.logger.log_info(self.name,
                         "initialized, limit is " + str(self.crawl_limit))

  def add_crawled_url(self, url: str) -> None:
    """Adds the given URL to the list of already crawled URLs

    Args:
      url: string of the URL that needs to be added

    Returns:
      None
    """
    self.logger.log_info(self.name,
                         "adding following URL to the crawled list: " + url)
    self.crawled_urls.append(url)
    print("URLs crawled: " + str(len(self.crawled_urls)) + "/" +
          str(self.crawl_limit))
    if self.crawl_limit != 0 and len(self.crawled_urls) >= self.crawl_limit:
      self.logger.log_debug(self.name, "Crawling limit reached!")

  def crawl_limit_reached(self) -> bool:
    """Checks if the crawl limit is reached

    Returns:
      bool that shows if the crawl limit is reached
    """
    if self.crawl_limit == 0:
      return False
    return len(self.crawled_urls) >= self.crawl_limit

  def to_json(self) -> str:
    """Returns the database in JSON format so it can be safed

    Returns:
      string of the database in JSON format
    """
    return json.dumps(self.crawled_urls)


class DomainTimers:
  """Contains and manages all timers for crawled domains

  Attributes:
    name: name of this instance for logging
    domain_timers: list of all domain timers
    logger: the custom_logging module to log all kinds of messages
"""

  def __init__(self, logger: Logger):
    """Inits DomainTimers

    Args:
      logger: the custom logging module
    """
    self.name = "DomainTimers"
    self.domain_timers = {}
    self.logger = logger

    self.logger.log_info(self.name, "initialized")

  def time_until_next_request(self, domain: str, crawl_delay: float) -> int:
    """Calculates how much time needs to be waited until next request to domain

    Args:
      domain: the domain that needs to be checked
      crawl_delay: the delay between requests to the urls domain

    Returns:
      seconds that need to be waited until next request to this domain
    """
    if domain not in self.domain_timers:
      return 0  # no entry -> we don't have to wait
    else:
      # check if enough time went by from last request to domain
      time_passed = time.time() - self.domain_timers[domain]
      time_to_wait = crawl_delay - time_passed

      if time_to_wait > 0:
        return time_to_wait
      else:
        return 0

  def set_timer(self, domain: str) -> None:
    """Creates a new timer for a specific domain or
        resets the already existing one

    Args:
      domain: the domain a timer needs to be set up for

    Returns:
      None
    """
    self.logger.log_debug(self.name, "setting up/resetting timer for " + domain)
    self.domain_timers[domain] = time.time()

  def to_json(self) -> str:
    """Returns the database in JSON format so it can be safed

    Returns:
      string of the database in JSON format
    """

    return json.dumps(self.domain_timers)


class RobotsTXTDatabase:
  """Contains the dictionary of robotparsers for each domain
      There are empty entries for all domains that don't have robot files

      Standard: https://datatracker.ietf.org/doc/html/draft-koster-rep

  Attributes:
    database: the dictionary with robotparsers
    logger: the custom_logging module to log all kinds of messages
"""

  def __init__(self, logger: Logger):
    """Inits RobotsTXTDatabase

    Args:
      logger: the custom logging module
    """
    self.name = "RobotsTXTDatabase"
    self.database = {}
    self.logger = logger
    self.logger.log_info(self.name, "initialized")

  def retrieve_robots_txt(self, url: str) -> None:
    """Retrieves the robots txt for the domain of the given url

    Args:
      url: the url of a website of a domain where we want to get the robots.txt

    Returns:
      None
    """
    # get the domain
    parsed_url = urlparse(url)

    try:
      x = requests.get(parsed_url.scheme + "://" + parsed_url.netloc +
                       "/robots.txt")
      if x.status_code != 200:
        self.database[parsed_url.netloc] = None
      else:
        self.database[parsed_url.netloc] = Protego.parse(x.text)
    except:
      self.database[parsed_url.netloc] = None

    self.logger.log_debug(self.name,
                          "Robots.txt entry created for " + parsed_url.netloc)

  def get_crawl_delay(self, url: str) -> float:
    """Extracts the crawl delay if it exists for the according domain

    Args:
      url: the url where we need the crawl delay of the domain

    Returns:
      the crawl delay, default one if none is available
    """
    # extract the domain
    domain = urlparse(url).netloc

    # do we have an entry?
    if domain in self.database:
      # is it just a dummy entry?
      if self.database[domain] is not None:
        # is there a crawl delay defined in the robots.txt?
        if self.database[domain].crawl_delay(CUSTOM_USER_AGENT) is not None:
          return self.database[domain].crawl_delay(CUSTOM_USER_AGENT)
        else:
          return DEFAULT_CRAWL_DELAY
    else:
      # no entry, get it and then check again for crawl delay
      self.retrieve_robots_txt(url)
      return self.get_crawl_delay(url)

  def can_fetch(self, url: str) -> bool:
    """Checks if the given url is allowed to crawl

    Args:
      url: url to check

    Returns:
      bool that shows if it is allowed to crawl the url
   """
    # extract the domain
    domain = urlparse(url).netloc

    # do we have an entry?
    if domain in self.database:
      # is it just a dummy entry?
      if self.database[domain] is not None:
        return self.database[domain].can_fetch(url, CUSTOM_USER_AGENT)
      else:
        # no robots.txt, so no restrictions
        return True
    else:
      # no entry, get it and then check again for crawl delay
      self.retrieve_robots_txt(url)
      return self.can_fetch(url)

  def to_json(self) -> str:
    """Returns the database in JSON format so it can be safed

    Returns:
      string of the keys of the database as json
    """
    return json.dumps(list(self.database.keys()))


class SetQueue(queue.Queue):
  """Variation of the Queue that avoids duplicate entries

  https://stackoverflow.com/questions/16506429/check-if-element-is-already-in-a-queue
  By doing that, the queue is not sorted anymore!!!
"""

  def __init__(self):
    """Inits SetQueue"""
    super().__init__()

  def _init(self, maxsize):
    self.queue = set()

  def _put(self, item):
    self.queue.add(item)

  def _get(self):
    return self.queue.pop()


class URLQueue():
  """Contains the URLs that need to be crawled

  Attributes:
    queue: the queue of URLs that will be crawled
    logger: the custom_logging module to log all kinds of messages
"""

  def __init__(self, logger: Logger, seed: [str]):
    """Inits URLQueue

    Args:
      logger: the custom logging module
      seed: list of urls that define the seed
    """
    self.name = "URLQueue"
    self.queue = SetQueue()
    for url in seed:
      self.queue.put((url, True))
    self.logger = logger
    self.logger.log_info(self.name, "initialized")

  def get_url(self) -> str:
    """Returns a new URL from the queue

    Returns:
      A new URL from the queue
    """
    self.logger.log_debug(self.name, "returning new URL")
    if not self.queue.empty():
      return self.queue.get()
    else:
      return None

  def add_url(self, url: str) -> None:
    """Adds an URL to the queue but only if its not already in there

    Since we are using a SetQueue we can add entries without checking
    for duplicates

    Args:
      url: url that needs to be added

    Returns:
      None
    """
    self.logger.log_debug(self.name, "adding following URL to queue: " + url)
    self.queue.put((url, False))

  def is_empty(self) -> bool:
    """Checks if queue is empty

    Returns:
      bool representing if queue is empty
    """
    return self.queue.empty()


class URLMap:
  """Database to save the chain of crawled URLs

  Attributes:
    name: name of this instance for logging
    url_map: the list of url paths
    logger: instance of the custom logging module
  """

  def __init__(self, logger: Logger):
    """Inits URLMap

    Args:
      logger: instance of the custom logging module
    """
    self.name = "URLMap"
    self.url_map = []
    self.logger = logger

  def add_url_path(self, url_from: str, url_to: str) -> None:
    """Adds a new path to the url map

    Args:
      url_from: the url which was analized
      url_to: the url which was extracted from url_from

    Returns:
      None
    """
    self.url_map.append({"url from": url_from, "url to": url_to})

  def to_json(self) -> str:
    """Returns the database in JSON format so it can be safed

    Returns:
      string of the database in JSON format
    """
    return json.dumps(self.url_map)

  def draw_map(self, filename: str) -> None:
    """Draws the map of all URL conections, the png file is stored in the
        local directory

    Args:
      filename: name of the output file

    Returns:
      None
    """
    url_to_object = {}
    self.logger.log_debug(self.name, "Generating url map")
    # Opening up a new file to create diagram
    with Diagram(outformat="svg", graph_attr={"bgcolor": "white"},
                 show=False) as diag:
      # use cairo to render to embed the SVG images directly in the file
      # https://github.com/mingrammer/diagrams/issues/8
      diag.dot.renderer = "cairo"
      # transform all urls into diagram objects
      for entry in self.url_map:
        if entry["url from"] not in url_to_object:
          if len(entry["url from"]) > DIAGRAMM_MAX_URL_LENGTH:
            url_to_object[entry["url from"]] = ECS(entry["url from"][:30] +
                                                   "...")
          else:
            url_to_object[entry["url from"]] = ECS(entry["url from"])
        if entry["url to"] not in url_to_object:
          if len(entry["url to"]) > DIAGRAMM_MAX_URL_LENGTH:
            url_to_object[entry["url to"]] = ECS(entry["url to"][:30] + "...")
          else:
            url_to_object[entry["url to"]] = ECS(entry["url to"])
      # connect all the urls
      for entry in self.url_map:
        url_to_object[entry["url from"]] >> url_to_object[entry["url to"]]

    # since we use cairo as renderer, we now have to rename the file
    os.rename("diagrams_image.cairo.svg", filename + ".svg")
    self.logger.log_debug(self.name, "url map done")
