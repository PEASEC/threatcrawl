Module cybersecurity-crawler.src.crawler_bot.extractor
======================================================
Contains classes for the extraction process

Classes
-------

`Extractor(id_number: int, logger: src.crawler_bot.custom_logging.Logger, html_database: src.crawler_bot.storage.HTMLDatabase, unprocessed_html_database: src.crawler_bot.storage.UnprocessedHTMLDatabase, url_queue: src.crawler_bot.storage.URLQueue, crawled_urls: src.crawler_bot.storage.CrawledURLs, url_map: src.crawler_bot.storage.URLMap, monitor: src.crawler_bot.monitoring.GlobalMonitor)`
:   Decides if websites are relevant and extracts the URLs out of it
    
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
    
    Inits Extractor
    
    Args:
      id_number: id of this specific instance of extractor
      logger: instance of the logging module
      html_database: instance of the html database
      unprocessed_html_database: instance of the unprocessed html database
      url_queue: instance of the url queue
      crawled_urls: instance of the list of crawled urls
      url_map: instance of the url map
      monitor: the global monitor to check stop requirements

    ### Methods

    `continue_extractor(self) ‑> None`
    :   Puts extractor back in running mode
        
        Returns:
          None

    `extract(self) ‑> None`
    :   extracts the urls from the next html document in line
        
        Returns:
          None

    `extract_urls(self, parsed_html_document: bs4.BeautifulSoup, crawled_url: str) ‑> list[str]`
    :   Extracts all urls out of a given html document
        
        Args:
          parsed_html_document: BeautifulSoup object where urls should be extracted
          crawled_url: string of the url the html document belongs to
        
        Returns:
          a list of extracted urls

    `idle_extractor(self, message: str) ‑> None`
    :   Puts extractor into idle
        
        Arg:
          message: string why the extractor is put into idle
        
        Returns:
          None

    `is_on_blacklist(self, url: str) ‑> bool`
    :   Checks if URL or parts of it is on blacklist
        
        Args:
          url: string of the url to check
        
        Returns:
          bool that indicates if url is on blacklist

    `is_valid(self, url: str) ‑> bool`
    :   Checks if the given url is valid
        
        https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
        
        Args:
          url: string that needs to be checked
        
        Returns:
          bool that shows if given url is valid

    `nofollow_tag_present(self, crawled_url: str, parsed_html_document: bs4.BeautifulSoup) ‑> bool`
    :   Checks if there is a nofollow robots meta tag in the given document
        
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

    `relative_to_absolute_url(self, relative_url: str, parent_url: str) ‑> str`
    :   Attempts to transform a relative url to an absolute url
        
        Args:
          relative_url: the url that needs to be transformed
          parent_url: the url of the website that contained url
        
        Returns:
          an attempt of an absolute url, not nessecarily a valid url
        
        Example:
          parent_url = https://www.google.com/testpath/test.html?myparameter=1
        
          /mytest.html => https://www.google.com/mytest.html
          mytest.html => https://www.google.com/testpath/mytest.html

    `start_extractor(self) ‑> None`
    :   Starts the extractor
        
        Returns:
          None

    `stop_extractor(self, message: str) ‑> None`
    :   Stops the execution of the extractor
        
        Arg:
          message: string why the extractor is stopped
        
        Returns:
          None