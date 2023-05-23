"""Contains different constants to control certain aspects of the crawler
"""
# seconds that need to pass before another request is made to a resource of a
# single domain
DEFAULT_CRAWL_DELAY = 0.5
# number of retriever threads
NUM_RETRIEVER_THREADS = 1
# number of extractor threads
NUM_EXTRACTOR_THREADS = 1
# custom user agent
CUSTOM_USER_AGENT = "https://peasec.de/peasec-crawlbot/"
# number of urls that should be crawled
CRAWLING_LIMIT = 100
# max length for url names in the url map diagram
DIAGRAMM_MAX_URL_LENGTH = 30
# filename of ground truth vectors
GROUND_TRUTH_VECTORS_FILE = "assets/20221207_223612_ground_truth_vectors.json"
# filename of seed file
SEED_FILE = "assets/20221204_233927_seed.csv"