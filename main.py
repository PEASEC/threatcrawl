"""The main module
"""
from threading import Thread
from time import strftime, gmtime
import timeit

from src.crawler_bot import config, custom_logging, extractor, monitoring, retriever, storage

# load seed, remove linebreak and empty lines
with open(config.SEED_FILE, encoding="utf-8") as f:
  seed = f.readlines()
  seed = [a.replace("\n", "") for a in seed if a != ""]

# setting up the logger
logger = custom_logging.Logger(custom_logging.LogLevel.DEBUG, "logfile")
logger.log_info("MAIN", "START")

# setting up the databases
html_database = storage.HTMLDatabase(logger)
crawled_urls = storage.CrawledURLs(logger, config.CRAWLING_LIMIT)
domain_timers = storage.DomainTimers(logger)
robots_txt_database = storage.RobotsTXTDatabase(logger)
url_queue = storage.URLQueue(logger, seed)
unprocessed_html_database = storage.UnprocessedHTMLDatabase(logger)
url_map = storage.URLMap(logger)

# setting up the global monitor
monitor = monitoring.GlobalMonitor(logger)

# setting up the retrievers
retrievers = []
for i in range(config.NUM_RETRIEVER_THREADS):
  my_retriever = retriever.Retriever(i, logger, url_queue, crawled_urls,
                                     unprocessed_html_database, domain_timers,
                                     robots_txt_database, monitor)
  retrievers.append(my_retriever)

# setting up the extractors
extractors = []

for i in range(config.NUM_EXTRACTOR_THREADS):
  my_extractor = extractor.Extractor(i, logger, html_database,
                                     unprocessed_html_database, url_queue,
                                     crawled_urls, url_map, monitor)
  extractors.append(my_extractor)

# start timer
start = timeit.default_timer()

# putting all retrievers and extractors in seperate threads
threads = []
for single_retriever in retrievers:
  t = Thread(target=single_retriever.start_retriever, args=())
  threads.append(t)
  t.start()

for single_extractor in extractors:
  t = Thread(target=single_extractor.start_extractor, args=())
  threads.append(t)
  t.start()

try:
  # wait for all threads to end
  for t in threads:
    t.join()
finally:
  # sort list after relevance
  html_database.sort_after_relevance()
  relevant_urls = html_database.get_list_of_relevant_urls()

  # measure time
  stop = timeit.default_timer()
  runtime = round(stop - start)

  logger.log_info("MAIN", "DONE")
  logger.log_info("MAIN", "Runtime: " + str(runtime) + "s")
  print("Runtime: " + str(runtime) + "s")

  # print information
  print("len crawled urls: ", str(len(crawled_urls.crawled_urls)))
  print("len unprocessed html database: ",
        str(len(unprocessed_html_database.database)))
  print("len html database: ", str(len(html_database.database)))
  print("len relevant urls: ", str(len(relevant_urls)))

  # safe results
  filename = strftime("%Y%m%d_%H%M%S", gmtime())

  with open("assets/" + logger.file_prefix + "_html_database.json",
            "x",
            encoding="utf-8") as a:
    a.write(html_database.to_json())

  with open("assets/" + logger.file_prefix + "_unprocessed_html_database.json",
            "x",
            encoding="utf-8") as a:
    a.write(unprocessed_html_database.to_json())

  with open("assets/" + logger.file_prefix + "_crawled_urls.json",
            "x",
            encoding="utf-8") as a:
    a.write(crawled_urls.to_json())

  with open("assets/" + logger.file_prefix + "_url_map.json",
            "x",
            encoding="utf-8") as a:
    a.write(url_map.to_json())

  with open("assets/" + logger.file_prefix + "_robotstxt.json",
            "x",
            encoding="utf-8") as a:
    a.write(robots_txt_database.to_json())

  with open("assets/" + logger.file_prefix + "_relevant_urls.csv",
            "x",
            encoding="utf-8") as a:
    for url in relevant_urls:
      a.writelines(url + "\n")

# create url map, only works with very few fetched urls!!
#url_map.draw_map("logs/" + logger.file_prefix + "_url_map")
