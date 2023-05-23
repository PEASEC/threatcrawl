Module cybersecurity-crawler.src.crawler_bot.retriever
======================================================
This module contains all classes to retrieve websites

Classes
-------

`Retriever(id_number: int, logger: src.crawler_bot.custom_logging.Logger, url_queue: src.crawler_bot.storage.URLQueue, crawled_urls: src.crawler_bot.storage.CrawledURLs, unprocessed_html_database: src.crawler_bot.storage.UnprocessedHTMLDatabase, domain_timers: src.crawler_bot.storage.DomainTimers, robots_txt_database: src.crawler_bot.storage.RobotsTXTDatabase, monitor: src.crawler_bot.monitoring.GlobalMonitor)`
:   The class to retrieve websites
    
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
    
    Inits Retriever
    
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

    ### Methods

    `continue_retriever(self) ‑> None`
    :   Puts retriever into running
        
        Returns:
          None

    `idle_retriever(self, message: str) ‑> None`
    :   Puts the retriever into idle
        
        Arg:
          message: string why the extractor is put into idle
        
        
        Returns:
          None

    `retrieve(self) ‑> None`
    :   Retrieves one URL and processes it
        
        Returns:
          None

    `start_retriever(self) ‑> None`
    :   starts the retriever
        
        Returns:
          None

    `stop_retriever(self, message: str) ‑> None`
    :   Stops the execution of the retriever
        
        Arg:
          message: string why the extractor is stopped
        
        Returns:
          None