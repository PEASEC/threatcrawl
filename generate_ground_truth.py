"""Example on how to create new ground truth vectors

"""

from src.crawler_bot.custom_logging import Logger, LogLevel
from src.crawler_bot.classification import Classifier
from src.crawler_bot.tools import load_dataset
import timeit
import json

################################################################################
dataset_filename = "assets/20221211_033449_dataset.json"
ignore_categories = False
max_amount_of_sentences = 50
use_adaptive_amount_of_sentences = False  # if True, overwrites max_amount_of_sentences
get_most_important_sentences = False
allowed_distance_average = True  # use average or maximum for distance to ground truth vectors
################################################################################

# start timer
start = timeit.default_timer()

# set up logger and classifier
logger = Logger(LogLevel.DEBUG, "generate_ground_truth")
classifier = Classifier(1, logger)

# load dataset from file
# (can also be generated directly from a url list by combining load_url_list
#  and download_url_list)
data = load_dataset(dataset_filename)
dataset = data["dataset"]

# if needed, generate ideal_amount_of_sentences_first
if use_adaptive_amount_of_sentences:
  print("Calculating ideal max amount of sentences")
  max_amount_of_sentences, sentence_gradients = classifier.calculate_ideal_amount_of_sentences(
      dataset, ignore_categories)

# save parameters
parameters = {}
parameters["dataset"] = data["parameters"]
parameters["ignore_categories"] = ignore_categories
parameters["max_amount_of_sentences"] = max_amount_of_sentences
parameters["dataset_filename"] = dataset_filename
parameters["use_adaptive_amount_of_sentences"] = str(
    use_adaptive_amount_of_sentences)
parameters["get_most_important_sentences"] = str(get_most_important_sentences)
parameters["allowed_distance_average"] = str(allowed_distance_average)

# generate ground truth vectors
print("Generating ground truth vectors")
result = classifier.generate_ground_truth_vectors(dataset, ignore_categories,
                                                  max_amount_of_sentences,
                                                  allowed_distance_average,
                                                  get_most_important_sentences)

# measure time
stop = timeit.default_timer()
runtime = round(stop - start)
print("Runtime: " + str(runtime) + "s")
logger.log_info("MAIN", "Runtime: " + str(runtime) + "s")

# save ground truth vectors to file
with open("assets/" + logger.file_prefix + "_ground_truth_vectors.json",
          "w",
          encoding="utf-8") as f:
  json.dump(
      {
          "parameters": parameters,
          "ground_truth_vectors": result["ground_truth_vectors"]
      }, f)

# save gradients to file
with open("assets/" + logger.file_prefix + "_ground_truth_gradients.json",
          "w",
          encoding="utf-8") as f:
  json.dump(
      {
          "parameters": parameters,
          "ground_truth_gradients": result["ground_truth_gradients"]
      }, f)

# if available, save sentence_gradients to file
if use_adaptive_amount_of_sentences:
  with open("assets/" + logger.file_prefix + "_sentence_gradients.json",
            "w",
            encoding="utf-8") as f:
    json.dump(
        {
            "parameters": parameters,
            "sentence_gradients": sentence_gradients
        }, f)
# if available save most important sentences to file
if get_most_important_sentences:
  with open("assets/" + logger.file_prefix + "_most_important_sentences.json",
            "w",
            encoding="utf-8") as f:
    json.dump(
        {
            "parameters": parameters,
            "most_important_sentences": result["most_important_sentences"]
        }, f)
