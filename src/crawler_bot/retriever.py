"""This module contains all classes to retrieve websites
"""
from urllib3.exceptions import MaxRetryError, NewConnectionError
import time
import requests

from src.crawler_bot import config, custom_logging, monitoring, storage, tools


class Retriever:
  """The class to retrieve websites

  Attributes:
    id_number: id of this specific instance of extractor
    name: name of this specific instance of extractor for logging
    user_agent: the custom user-agent of the retriever
    state: describes the state of the thread (running, stopped, idle)
    url_queue: instance of the url queue
    headers: the custom headers that will be sent with every request
    logger: instance of the logging module
    unprocessed_html_database: instance of the unprocessed html database
    crawled_urls: instance of the list of crawled urls
    domain_timers: database of timers of requests to each domain
    robots_txt_database: the database that contains timestamps of requests to
                          the domains
    monitor: the global monitor to check stop requirements
"""

  def __init__(self, id_number: int, logger: custom_logging.Logger,
               url_queue: storage.URLQueue, crawled_urls: storage.CrawledURLs,
               unprocessed_html_database: storage.UnprocessedHTMLDatabase,
               domain_timers: storage.DomainTimers,
               robots_txt_database: storage.RobotsTXTDatabase,
               monitor: monitoring.GlobalMonitor):
    """Inits Retriever

        Args:
          id_number: id of the retriever
          logger: the custom logging module
          url_queue: the url queue that contains the urls to crawl
          crawled_urls: the database that contains the list of crawled urls
          unprocessed_html_database: the database that contains the unprocessed
                                      crawled web pages
          domain_timers: the database that contains timestamps of requests to
                          the domains
          robots_txt_database: database with entries for the robots.txt files
          monitor: the global monitor to check stop requirements
    """
    self.id_number = id_number
    self.name = "Retriever#" + str(self.id_number)
    self.user_agent = config.CUSTOM_USER_AGENT
    self.state = monitoring.ThreadState.RUNNING
    self.url_queue = url_queue
    self.headers = {"User-Agent": config.CUSTOM_USER_AGENT}
    self.logger = logger
    self.unprocessed_html_database = unprocessed_html_database
    self.crawled_urls = crawled_urls
    self.domain_timers = domain_timers
    self.robots_txt_database = robots_txt_database
    self.monitor = monitor

    self.logger.log_info(self.name, "initialized")

  def retrieve(self) -> None:
    """Retrieves one URL and processes it

    Returns:
      None
    """
    # get next url
    url, is_seed = self.url_queue.get_url()

    self.logger.log_info(self.name, "Starting  " + url)

    # add to list of crawled urls
    self.crawled_urls.add_crawled_url(url)

    # check if request is allowed by robots.txt
    if not self.robots_txt_database.can_fetch(url):
      self.logger.log_debug(self.name, "robots txt forbids access to " + url)
      return

    # make request
    try:
      # check if we need to wait first
      domain = tools.extract_main_domain_plus_tld(url)
      crawl_delay = self.robots_txt_database.get_crawl_delay(url)
      time_to_wait = self.domain_timers.time_until_next_request(
          domain, crawl_delay)
      if time_to_wait > 0:
        self.logger.log_debug(
            self.name, "sleeping for " + str(time_to_wait) +
            " seconds for domain " + domain)
        time.sleep(time_to_wait)
      x = requests.get(url, headers=self.headers, timeout=5)
      # save timestamp of request
      self.domain_timers.set_timer(domain)
    except NewConnectionError:
      self.logger.log_error(self.name,
                            "NewConnectionError when crawling " + url)
      return
    except MaxRetryError:
      self.logger.log_error(self.name, "MaxRetryError when crawling " + url)
      return
    except ConnectionError:
      self.logger.log_error(self.name, "ConnectionError when crawling " + url)
      return
    except:
      self.logger.log_error(self.name, "SOME error when crawling " + url)
      return

    # add url and html to unprocessed html database
    self.unprocessed_html_database.add_entry(url, is_seed, x.text)

  def start_retriever(self) -> None:
    """starts the retriever

    Returns:
      None
    """
    while self.state != monitoring.ThreadState.STOPPED:

      # check if retriever state needs to be changed

      # 1. crawl limit reached -> stop retriever
      if self.crawled_urls.crawl_limit_reached():
        self.stop_retriever("Crawl limit reached")
        continue

      # 2. url queue empty + all extractors stopped/idle
      # + all retrievers stopped/idle + unprocessed htmls is empty
      # -> stop retriever
      if self.url_queue.is_empty() and self.unprocessed_html_database.is_empty(
      ) and self.monitor.retrievers_all_idle_or_stopped(
      ) and self.monitor.extractors_all_idle_or_stopped():
        self.stop_retriever(
            "url queue empty, html queue empty and no reciever or extractor running"
        )
        continue

      # 3. url queue is empty -> idle retriever
      if self.url_queue.is_empty():
        self.idle_retriever("url queue empty")
        time.sleep(0.1)
        continue
      else:
        self.continue_retriever()

      # retriever is supposed to run, retrieve one url
      self.retrieve()

    self.logger.log_info(self.name, "retriever is stopped")

  def continue_retriever(self) -> None:
    """Puts retriever into running

    Returns:
      None
    """
    self.logger.log_debug(self.name, "putting retriever into running")
    self.monitor.retriever_continue(self.state)
    self.state = monitoring.ThreadState.RUNNING

  def idle_retriever(self, message: str) -> None:
    """Puts the retriever into idle

    Arg:
      message: string why the extractor is put into idle


    Returns:
      None
    """
    self.logger.log_debug(self.name,
                          "putting retriever into idle (" + message + ")")
    self.monitor.retriever_idle(self.state)
    self.state = monitoring.ThreadState.IDLE

  def stop_retriever(self, message: str) -> None:
    """Stops the execution of the retriever

    Arg:
      message: string why the extractor is stopped

    Returns:
      None
    """
    self.logger.log_info(self.name, "stopping retriever (" + message + ")")
    self.monitor.retriever_stop(self.state)
    self.state = monitoring.ThreadState.STOPPED