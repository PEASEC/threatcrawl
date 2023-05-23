Module cybersecurity-crawler.src.crawler_bot.storage
====================================================
Module that holds all the classes for storing information

Functions
---------

    
`get_relative_distance(single_entry: cybersecurity-crawler.src.crawler_bot.storage.HTMLDatabaseEntry) ‑> float`
:   Returns the relative_distance value of a single entry of the category
        the entry was classified as
    
    Returns:
      float of the relative_distance, 0 if entry was classified as not relevant

Classes
-------

`CrawledURLs(logger: src.crawler_bot.custom_logging.Logger, crawl_limit: int = 0)`
:   Contains all the already crawled URLs
    
    Attributes:
      name: name of this instance for logging
      crawled_urls: list of all already crawled urls
      logger: the custom_logging module to log all kinds of messages
      crawl_limit: amount of urls that should be crawled
    
    Inits CrawledURLs
    
    Args:
      logger: the custom logging module
      crawl_limit: amount of urls that will be crawled, 0 = no limit

    ### Methods

    `add_crawled_url(self, url: str) ‑> None`
    :   Adds the given URL to the list of already crawled URLs
        
        Args:
          url: string of the URL that needs to be added
        
        Returns:
          None

    `crawl_limit_reached(self) ‑> bool`
    :   Checks if the crawl limit is reached
        
        Returns:
          bool that shows if the crawl limit is reached

    `to_json(self) ‑> str`
    :   Returns the database in JSON format so it can be safed
        
        Returns:
          string of the database in JSON format

`DomainTimers(logger: src.crawler_bot.custom_logging.Logger)`
:   Contains and manages all timers for crawled domains
    
    Attributes:
      name: name of this instance for logging
      domain_timers: list of all domain timers
      logger: the custom_logging module to log all kinds of messages
    
    Inits DomainTimers
    
    Args:
      logger: the custom logging module

    ### Methods

    `set_timer(self, domain: str) ‑> None`
    :   Creates a new timer for a specific domain or
            resets the already existing one
        
        Args:
          domain: the domain a timer needs to be set up for
        
        Returns:
          None

    `time_until_next_request(self, domain: str, crawl_delay: float) ‑> int`
    :   Calculates how much time needs to be waited until next request to domain
        
        Args:
          domain: the domain that needs to be checked
          crawl_delay: the delay between requests to the urls domain
        
        Returns:
          seconds that need to be waited until next request to this domain

    `to_json(self) ‑> str`
    :   Returns the database in JSON format so it can be safed
        
        Returns:
          string of the database in JSON format

`HTMLDatabase(logger: src.crawler_bot.custom_logging.Logger)`
:   class that stores all the HTML content
    
    Attributes:
      name: name of the class for logging
      database: list that contains all the HTML content
      logger: the custom_logging module to log all kinds of messages
    
    Inits HTMLDatabase
    
    Args:
      logger: instance of the custom logging module

    ### Methods

    `add_html_document(self, url: str, html_document: str, relevant: bool, extracted_urls: list[str], distances: dict, relative_distances: dict, guessed_category: str) ‑> None`
    :   Stores the given HTML document in the database
        
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

    `get_list_of_relevant_urls(self) ‑> list[str]`
    :   Returns the url of all entries that are relevant
        
        Returns:
          list of urls

    `is_empty(self) ‑> bool`
    :   Checks if html database is empty
        
        Returns:
          boolean that shows if database is empty

    `sort_after_relevance(self) ‑> None`
    :   Sorts the database using the relative_distances
        
        Returns:
          None

    `to_json(self) ‑> str`
    :   Returns the database in JSON format so it can be safed
        
        Returns:
          string of the database in JSON format

`HTMLDatabaseEntry(url: str, html: str, extracted_urls: list[str], relevant: bool, distances: dict, relative_distances: dict, guessed_category: str)`
:   Class to safe a single HTML database entry
    
    Attributes:
      url: url of the html page
      html: the html of the page
      extracted_urls: list of extracted urls
      relevant: bool that shows if entry is relevant or not
      distances: dictionary with all distances from the document to the
                  possible categories
      guessed_category: the guessed category by the classifier
    
    Inits HTMLDatabaseEntry
    
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

`RobotsTXTDatabase(logger: src.crawler_bot.custom_logging.Logger)`
:   Contains the dictionary of robotparsers for each domain
        There are empty entries for all domains that don't have robot files
    
        Standard: https://datatracker.ietf.org/doc/html/draft-koster-rep
    
    Attributes:
      database: the dictionary with robotparsers
      logger: the custom_logging module to log all kinds of messages
    
    Inits RobotsTXTDatabase
    
    Args:
      logger: the custom logging module

    ### Methods

    `can_fetch(self, url: str) ‑> bool`
    :   Checks if the given url is allowed to crawl
        
        Args:
          url: url to check
        
        Returns:
          bool that shows if it is allowed to crawl the url

    `get_crawl_delay(self, url: str) ‑> float`
    :   Extracts the crawl delay if it exists for the according domain
        
        Args:
          url: the url where we need the crawl delay of the domain
        
        Returns:
          the crawl delay, default one if none is available

    `retrieve_robots_txt(self, url: str) ‑> None`
    :   Retrieves the robots txt for the domain of the given url
        
        Args:
          url: the url of a website of a domain where we want to get the robots.txt
        
        Returns:
          None

    `to_json(self) ‑> str`
    :   Returns the database in JSON format so it can be safed
        
        Returns:
          string of the keys of the database as json

`SetQueue()`
:   Variation of the Queue that avoids duplicate entries
    
    https://stackoverflow.com/questions/16506429/check-if-element-is-already-in-a-queue
    By doing that, the queue is not sorted anymore!!!
    
    Inits SetQueue

    ### Ancestors (in MRO)

    * queue.Queue

`URLMap(logger: src.crawler_bot.custom_logging.Logger)`
:   Database to save the chain of crawled URLs
    
    Attributes:
      name: name of this instance for logging
      url_map: the list of url paths
      logger: instance of the custom logging module
    
    Inits URLMap
    
    Args:
      logger: instance of the custom logging module

    ### Methods

    `add_url_path(self, url_from: str, url_to: str) ‑> None`
    :   Adds a new path to the url map
        
        Args:
          url_from: the url which was analized
          url_to: the url which was extracted from url_from
        
        Returns:
          None

    `draw_map(self, filename: str) ‑> None`
    :   Draws the map of all URL conections, the png file is stored in the
            local directory
        
        Args:
          filename: name of the output file
        
        Returns:
          None

    `to_json(self) ‑> str`
    :   Returns the database in JSON format so it can be safed
        
        Returns:
          string of the database in JSON format

`URLQueue(logger: src.crawler_bot.custom_logging.Logger, seed: [<class 'str'>])`
:   Contains the URLs that need to be crawled
    
    Attributes:
      queue: the queue of URLs that will be crawled
      logger: the custom_logging module to log all kinds of messages
    
    Inits URLQueue
    
    Args:
      logger: the custom logging module
      seed: list of urls that define the seed

    ### Methods

    `add_url(self, url: str) ‑> None`
    :   Adds an URL to the queue but only if its not already in there
        
        Since we are using a SetQueue we can add entries without checking
        for duplicates
        
        Args:
          url: url that needs to be added
        
        Returns:
          None

    `get_url(self) ‑> str`
    :   Returns a new URL from the queue
        
        Returns:
          A new URL from the queue

    `is_empty(self) ‑> bool`
    :   Checks if queue is empty
        
        Returns:
          bool representing if queue is empty

`UnprocessedHTMLDatabase(logger: src.crawler_bot.custom_logging.Logger)`
:   Keeps a list of unprocessed HTML documents
    
    Attributes:
      database: contains the list of touples (url, html content)
      logger: the custom_logging module to log all kinds of messages
      name: name of the instance for logging
    
    Inits UnprocessedHtmlDatabase
    
    Args:
      logger: instance of the custom logging module

    ### Methods

    `add_entry(self, url: str, is_seed: bool, html_document: str) ‑> None`
    :   Adds a new touple of url and html document to the database
        
        Args:
          url: string of the crawled page
          is_seed: is url seed?
          html_document: string of the recieved html document
        
        Returns:
          None

    `get_entry(self) ‑> (<class 'str'>, <class 'bool'>, <class 'str'>)`
    :   Returns an entry from the database
        
        Returns:
          triple of (url, is_seed,html document)

    `is_empty(self) ‑> bool`
    :   Checks if database is empty
        
        Returns:
          bool that shows if database is empty

    `to_json(self) ‑> str`
    :   Returns the database in JSON format so it can be safed
        
        Returns:
          string of the database in JSON format