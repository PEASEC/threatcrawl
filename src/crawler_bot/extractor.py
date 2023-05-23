"""Contains classes for the extraction process
"""

import time
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse

from src.crawler_bot import custom_logging, monitoring, storage, classification
from src.crawler_bot.tools import extract_main_domain, extract_main_domain_plus_tld
from src.crawler_bot.config import GROUND_TRUTH_VECTORS_FILE

DOMAIN_FORMAT = re.compile(
    r"(?:^(\w{1,255}):(.{1,255})@|^)"  # http basic authentication [optional]
    r"(?:(?:(?=\S{0,253}(?:$|:))"  # check full domain length to be less than or equal to 253 (starting after http basic auth, stopping before port)
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"  # check for at least one subdomain (maximum length per subdomain: 63 characters), dashes in between allowed
    r"(?:[a-z0-9]{1,63})))"  # check for top level domain, no dashes allowed
    r"|localhost)"  # accept also "localhost" only
    r"(:\d{1,5})?",  # port [optional]
    re.IGNORECASE)
SCHEME_FORMAT = re.compile(
    r"^(http|hxxp|ftp|fxp)s?$",  # scheme: http(s) or ftp(s)
    re.IGNORECASE)
DOMAIN_PLUS_TLD_FORMAT = re.compile(r"[^.]+\.[^.]+$")
MAIN_DOMAIN_ONLY_FORMAT = re.compile(r"([^.]+)\.[^.]+$")


class Extractor:
  """Decides if websites are relevant and extracts the URLs out of it

  Attributes:
    state: describes the state of the thread (running, stopped, idle)
    id_number: id of this specific instance of extractor
    name: name of this specific instance of extractor for logging
    logger: instance of the logging module
    html_database: instance of the html database
    unprocessed_html_database: instance of the unprocessed html database
    url_queue: instance of the url queue
    crawled_urls: instance of the list of crawled urls
    url_map: instance of the url map
    monitor: the global monitor to check stop requirements
    classifier: the used classifier
"""

  def __init__(self, id_number: int, logger: custom_logging.Logger,
               html_database: storage.HTMLDatabase,
               unprocessed_html_database: storage.UnprocessedHTMLDatabase,
               url_queue: storage.URLQueue, crawled_urls: storage.CrawledURLs,
               url_map: storage.URLMap, monitor: monitoring.GlobalMonitor):
    """Inits Extractor

    Args:
      id_number: id of this specific instance of extractor
      logger: instance of the logging module
      html_database: instance of the html database
      unprocessed_html_database: instance of the unprocessed html database
      url_queue: instance of the url queue
      crawled_urls: instance of the list of crawled urls
      url_map: instance of the url map
      monitor: the global monitor to check stop requirements

    """
    self.state = monitoring.ThreadState.RUNNING
    self.id_number = id_number
    self.name = "Extractor#" + str(self.id_number)
    self.logger = logger
    self.html_database = html_database
    self.unprocessed_html_database = unprocessed_html_database
    self.url_queue = url_queue
    self.crawled_urls = crawled_urls
    self.url_map = url_map
    self.monitor = monitor
    self.classifier = classification.Classifier(id_number, logger)
    self.classifier.load_parameters_from_file(GROUND_TRUTH_VECTORS_FILE)

    # load blacklist
    with open("assets/blacklist.json", encoding="utf-8") as f:
      self.blacklist = json.load(f)

    self.logger.log_debug(self.name, "initialized")

  def nofollow_tag_present(self, crawled_url: str,
                           parsed_html_document: BeautifulSoup) -> bool:
    """Checks if there is a nofollow robots meta tag in the given document

    https://developers.google.com/search/docs/advanced/robots/robots_meta_tag

    Examples:
      <meta content="noindex,nofollow" name="robots"/>
      <meta content="follow" name="robots"/>

    Args:
      crawled_url: the url the content comes from
      parsed_html_document: BeautifulSoup object which may contain the nofollow
                              robots meta tag

    Returns:
      boolean indicating if the given document has the nofollow robots meta tag
    """
    for tag in parsed_html_document.find_all("meta", attrs={"name": "robots"}):
      if not "content" in tag:
        return False
      for content in tag["content"].split(","):
        if content.strip() in ["nofollow", "none"]:
          self.logger.log_debug(
              self.name, "url " + crawled_url + " contains a nofollow meta tag")
          return True
    return False

  def is_valid(self, url: str) -> bool:
    """Checks if the given url is valid

    https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not

    Args:
      url: string that needs to be checked

    Returns:
      bool that shows if given url is valid
    """
    if url is None or url == "":
      return False

    url = url.strip()

    # no url given
    if not url:
      self.logger.log_debug(self.name, "empty url detected => Invalid")
      return False

    # url too long
    if len(url) > 2048:
      self.logger.log_debug(self.name, "url too long (" + url + ")")
      return False

    result = urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    # url has no scheme
    if not scheme:
      self.logger.log_debug(self.name,
                            "url has no scheme (" + url + ") => Invalid")
      return False

    # url has no valid scheme
    if not re.fullmatch(SCHEME_FORMAT, scheme):
      self.logger.log_debug(self.name,
                            "url has no valid scheme (" + url + ") => Invalid")
      return False

    # url has no domain
    if not domain:
      self.logger.log_debug(self.name,
                            "url has no domain (" + url + ") => Invalid")
      return False

    # domain is malformed
    if not re.fullmatch(DOMAIN_FORMAT, domain):
      self.logger.log_debug(self.name,
                            "url is malformed (" + url + ") => Invalid")
      return False

    # if all tests are negative, URL is probably valid
    return True

  def is_on_blacklist(self, url: str) -> bool:
    """Checks if URL or parts of it is on blacklist

    Args:
      url: string of the url to check

    Returns:
      bool that indicates if url is on blacklist
    """
    # check if on blacklist
    # check if main domain is on blacklist
    if extract_main_domain(url) in self.blacklist["main_domains"]:
      self.logger.log_debug(self.name, "domain is on blacklist (" + url + ")")
      return True
    # check if tld + main domain is on blacklist
    if extract_main_domain_plus_tld(url) in self.blacklist["main_domains+tlds"]:
      self.logger.log_debug(self.name,
                            "domain+tld is on blacklist (" + url + ")")
      return True
    # check if extension is on blacklist
    for extension in self.blacklist["extensions"]:
      if urlparse(url).path[-(len(extension)):] == extension:
        self.logger.log_debug(self.name,
                              "extension is on blacklist (" + url + ")")
        return True

    # if every test is passed, url is not on blacklist
    return False

  def relative_to_absolute_url(self, relative_url: str, parent_url: str) -> str:
    """Attempts to transform a relative url to an absolute url

    Args:
      relative_url: the url that needs to be transformed
      parent_url: the url of the website that contained url

    Returns:
      an attempt of an absolute url, not nessecarily a valid url

    Example:
      parent_url = https://www.google.com/testpath/test.html?myparameter=1

      /mytest.html => https://www.google.com/mytest.html
      mytest.html => https://www.google.com/testpath/mytest.html

    """
    # parse the parent url
    parsed_parent = urlparse(parent_url)
    scheme_and_domain = parsed_parent.scheme + "://" + parsed_parent.netloc
    if relative_url[0] == "/":
      # url starts with a slash, so it just has to be appended to the main url
      absolute_url = scheme_and_domain + relative_url
    else:
      # url doesn't start with slash, so it might be just the last part of the
      # url (e.g. file.html)
      if parsed_parent.path == "":
        # no path, so just add it to the domain
        absolute_url = scheme_and_domain + "/" + relative_url
      else:
        # attach to domain and path but cut away everything after the last slash
        absolute_url = scheme_and_domain + parsed_parent.path[:parsed_parent.
                                                              path.rindex("/") +
                                                              1] + relative_url

    self.logger.log_debug(
        self.name, "Transformed URL " + relative_url + " to " + absolute_url)
    return absolute_url

  def extract_urls(self, parsed_html_document: BeautifulSoup,
                   crawled_url: str) -> list[str]:
    """Extracts all urls out of a given html document

    Args:
      parsed_html_document: BeautifulSoup object where urls should be extracted
      crawled_url: string of the url the html document belongs to

    Returns:
      a list of extracted urls
    """
    # extract href property from all a elements that have it and don't start
    # with javascript:
    hrefs = [
        item["href"].strip()
        for item in parsed_html_document.find_all("a", href=True)
    ]

    urls = []

    # remove all hrefs that are empty, just anchors (#) or refer to other
    # protocols like fttp://, mailto:, javascript: etc.
    for href in hrefs:
      if len(href) <= 0:
        continue
      if href[0] == "#":
        continue
      if re.search("^[a-zA-Z]+:", href) is not None:
        # url has a protocol at the beginning, remove if not http or https
        if len(href) >= 5 and href[:4] != "http" and href[:5] != "https":
          continue
      urls.append(href)

    # only return urls that are valid and not in blacklist
    valid_urls = []
    for url in urls:
      # check if url is valid url
      if not self.is_valid(url):
        # if not, it might be a relative url
        url = self.relative_to_absolute_url(url, crawled_url)
        # check again if now valid
        if not self.is_valid(url):
          # still not valid, so skip this one
          continue

      # check if url is blacklisted
      if self.is_on_blacklist(url):
        # url is on blacklist, skip this one
        continue

      # all checks went through, url is valid and not on blacklist
      valid_urls.append(url)

    # return list without duplicates
    return list(dict.fromkeys(valid_urls))

  def extract(self) -> None:
    """extracts the urls from the next html document in line

    Returns:
      None
    """
    # get next html page
    crawled_url, is_seed, html_document = self.unprocessed_html_database.get_entry(
    )

    if crawled_url is None:
      return

    self.logger.log_info(self.name, "processing: " + crawled_url)

    # parse the document
    parsed_html_document = BeautifulSoup(html_document, "lxml")

    # classify document
    classification_result = self.classifier.is_relevant(crawled_url,
                                                        html_document)

    # if page is not relevant we don't extract urls
    if (not classification_result["relevant"] and
        not is_seed) or self.nofollow_tag_present(crawled_url,
                                                  parsed_html_document):
      self.html_database.add_html_document(
          crawled_url, html_document, classification_result["relevant"], [],
          classification_result["distances"],
          classification_result["relative_distances"],
          classification_result["guessed_category"])
    # if page is relevant but has a nofollow tag we save it as relevant but
    # dont extract urls
    elif self.nofollow_tag_present(crawled_url, parsed_html_document):
      self.html_database.add_html_document(
          crawled_url, html_document, classification_result["relevant"], [],
          classification_result["distances"],
          classification_result["relative_distances"],
          classification_result["guessed_category"])
    # page is relevant or seed and doesn't contain nofollow tag -> extract urls
    else:
      extracted_urls = self.extract_urls(parsed_html_document, crawled_url)
      self.html_database.add_html_document(
          crawled_url, html_document, classification_result["relevant"],
          extracted_urls, classification_result["distances"],
          classification_result["relative_distances"],
          classification_result["guessed_category"])
      # add extracted urls to url map
      for exracted_url in extracted_urls:
        self.url_map.add_url_path(crawled_url, exracted_url)

      # add to urls queue but only if not already crawled and only if
      # retrievers are still running
      if not self.crawled_urls.crawl_limit_reached():
        for extracted_url in extracted_urls:
          if extracted_url not in self.crawled_urls.crawled_urls:
            self.url_queue.add_url(extracted_url)

  def start_extractor(self) -> None:
    """Starts the extractor

    Returns:
      None
    """
    while self.state != monitoring.ThreadState.STOPPED:

      # check if extractor state needs to be changed

      # 1. crawl limit reached and no unprocessed htmls left -> stop extractor
      if self.crawled_urls.crawl_limit_reached(
      ) and self.unprocessed_html_database.is_empty(
      ) and self.monitor.retrievers_all_idle_or_stopped():
        self.stop_extractor("Crawl limit reached")
        continue

      # 2. url queue empty + all extractors stopped/idle
      # + all retrievers stopped/idle + unprocessed htmls is empty
      # -> stop extractor
      if self.url_queue.is_empty() and self.unprocessed_html_database.is_empty(
      ) and self.monitor.retrievers_all_idle_or_stopped(
      ) and self.monitor.extractors_all_idle_or_stopped():
        self.stop_extractor(
            "url queue empty, html queue empty and no reciever or extractor running"
        )
        continue

      # 3. html database empty -> idle thread
      if self.unprocessed_html_database.is_empty():
        self.idle_extractor("crawled urls database is empty")
        time.sleep(0.1)
        continue
      else:
        self.continue_extractor()
      self.extract()

    self.logger.log_info(self.name, "stopped")

  def continue_extractor(self) -> None:
    """Puts extractor back in running mode

    Returns:
      None
    """
    self.logger.log_debug(self.name, "putting extractor into running")
    self.monitor.extractor_continue(self.state)
    self.state = monitoring.ThreadState.RUNNING

  def idle_extractor(self, message: str) -> None:
    """Puts extractor into idle

    Arg:
      message: string why the extractor is put into idle

    Returns:
      None
    """
    self.logger.log_debug(self.name,
                          "putting extractor into idle (" + message + ")")
    self.monitor.extractor_idle(self.state)
    self.state = monitoring.ThreadState.IDLE

  def stop_extractor(self, message: str) -> None:
    """Stops the execution of the extractor

    Arg:
      message: string why the extractor is stopped

    Returns:
      None
    """
    self.logger.log_info(self.name, "stopping (" + message + ")")
    self.monitor.extractor_stop(self.state)
    self.state = monitoring.ThreadState.STOPPED
