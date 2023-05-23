"""Evaluation of the classifier module
"""
import json
import random
from math import floor

from src.crawler_bot.custom_logging import Logger, LogLevel
from src.crawler_bot.classification import Classifier
import timeit

################################################################################
dataset_filename = "assets/20221211_033449_dataset.json"
max_amount_of_sentences = 12
use_adaptive_amount_of_sentences = False  # if True, overwrites max_amount_of_sentences
allowed_distance_average = False  # use average or maximum for distance to ground truth vectors
ignore_categories = False
################################################################################


def cut_dataset(input_dataset: dict, amount_slices: int) -> list[dict]:
  """Cuts the dataset in amount_slices equally parts per category

  Args:
    input_dataset: the whole dataset (urls grouped by category)
    amount_slices: the amount of parts that should be returned

  Returns:
    a list of amount_slices dictionaries
  """
  result_dataset_slices = []

  # generate k dictionaries
  for _ in range(amount_slices):
    result_dataset_slices.append({})

  # iterate through all categories
  for category, documents in input_dataset.items():

    # shuffle each list first
    random.shuffle(documents)

    # calc length of each slice for that category
    len_part = floor(len(documents) / amount_slices)

    # cut list of documents and add them into the according slice
    for index in range(k):
      if index < k - 1:
        result_dataset_slices[index][category] = documents[index *
                                                           len_part:(index +
                                                                     1) *
                                                           len_part]
      else:
        # last slice gets the remaining objects (so might have up to k-1 more than the other slices)
        result_dataset_slices[index][category] = documents[index * len_part:]

  return result_dataset_slices


def merge_datasets(set1: dict, set2: dict) -> dict:
  """merges two datasets by combining the lists for each key to one list

  Args:
    set1: dict with dataset items for each category
    set2: dict with dataset items for each category

  Returns:
    one combined dict
  """
  output_result = {}

  for key, item in set1.items():
    output_result[key] = item.copy()
  for key, item in set2.items():
    if key in output_result:
      output_result[key].extend(item.copy())
    else:
      output_result[key] = item.copy()

  return output_result


def create_metrics(classification_results: dict) -> dict:
  """creates Precision, Recall and F1 Score for the result

  Args:
    result: list of categoriezed entries

  Returns:
    dictionary of all metrics for each category
  """
  # P = TP/(TP+FP), R = TP/(TP+FN), F1 = (2*R*P)/(R+P)
  # measure TP, FP, TN, FN for each category + for relevant
  resulting_metrics = {}

  for category in classification_results.keys():
    resulting_metrics[category] = {"TP": 0, "FP": 0, "TN": 0, "FN": 0}

  # iterate through the results
  for category, entries in classification_results.items():
    for entry in entries:
      # category is correct -> TP for that category, TN for all others
      if entry["classification_result"]["guessed_category"] == category:
        for inner_category in classification_results.keys():
          if inner_category == category:
            resulting_metrics[inner_category]["TP"] += 1
          else:
            resulting_metrics[inner_category]["TN"] += 1
      # category is incorrect -> FN for the category, FP for the guessed category, and TN for all others
      else:
        for inner_category in classification_results.keys():
          if inner_category == category:
            resulting_metrics[inner_category]["FN"] += 1
          elif inner_category == entry["classification_result"][
              "guessed_category"]:
            resulting_metrics[inner_category]["FP"] += 1
          else:
            resulting_metrics[inner_category]["TN"] += 1

  # create values for relevant by switching values of not_relevant
  resulting_metrics["relevant"] = {}
  resulting_metrics["relevant"]["TP"] = resulting_metrics["not_relevant"]["TN"]
  resulting_metrics["relevant"]["TN"] = resulting_metrics["not_relevant"]["TP"]
  resulting_metrics["relevant"]["FP"] = resulting_metrics["not_relevant"]["FN"]
  resulting_metrics["relevant"]["FN"] = resulting_metrics["not_relevant"]["FP"]

  # remove not_relevant counters
  del resulting_metrics["not_relevant"]

  # calculate precision, recall and f1 score
  for category, counters in resulting_metrics.items():
    if (counters["TP"] + counters["FP"]) != 0:
      cat_precision = counters["TP"] / (counters["TP"] + counters["FP"])
    else:
      cat_precision = 0
    if (counters["TP"] + counters["FN"]) != 0:
      cat_recall = counters["TP"] / (counters["TP"] + counters["FN"])
    else:
      cat_recall = 0
    if cat_precision + cat_recall != 0:
      cat_f1 = (2 * cat_precision * cat_recall) / (cat_precision + cat_recall)
    else:
      cat_f1 = 0
    counters["precision"] = cat_precision
    counters["recall"] = cat_recall
    counters["f1"] = cat_f1

  return resulting_metrics


# set k
k = 5

# set seed
random.seed(1)

# set up the logger and classifier
logger = Logger(LogLevel.DEBUG, "evaluation")
classifier = Classifier(1, logger)

results_per_fold = {}
ground_truth_vectors_per_fold = []
ground_truth_gradients_per_fold = []
sentence_gradients_per_fold = []

# load dataset (or download it first using tools.download_dataset)
with open(dataset_filename, encoding="utf-8") as f:
  data = json.load(f)

# save parameters
parameters = {}
parameters["dataset"] = data["parameters"]
parameters["ignore_categories"] = ignore_categories
parameters["max_amount_of_sentences"] = max_amount_of_sentences
parameters["dataset_filename"] = dataset_filename
parameters["use_adaptive_amount_of_sentences"] = str(
    use_adaptive_amount_of_sentences)
parameters["allowed_distance_average"] = str(allowed_distance_average)
dataset = data["dataset"]

# cut dataset into slices
dataset_slices = cut_dataset(dataset, k)

# start timer
start = timeit.default_timer()

# go through each fold
for fold_number in range(k):
  print("--- Fold number: " + str(fold_number + 1) + "/" + str(k) + " ---")

  # train on all but fold_number
  # evaluate on fold_number

  #create train_dataset
  train_dataset = {}
  for i in range(len(dataset_slices)):
    if i != fold_number:
      train_dataset = merge_datasets(train_dataset, dataset_slices[i])

  #create evaluation_dataset
  evaluation_dataset = dataset_slices[fold_number]

  # train/generate ground truth with train_dataset
  amount_urls = 0
  for cat, urls in train_dataset.items():
    amount_urls += len(urls)

  # if needed, generate ideal_amount_of_sentences_first
  if use_adaptive_amount_of_sentences:
    print("Calculating ideal max amount of sentences")
    max_amount_of_sentences, sentence_gradients = classifier.calculate_ideal_amount_of_sentences(
        train_dataset, ignore_categories)
    sentence_gradients_per_fold.append(sentence_gradients)

  print("Creating ground truth vectors on " + str(amount_urls) + " urls...")
  result = classifier.generate_ground_truth_vectors(train_dataset,
                                                    ignore_categories,
                                                    max_amount_of_sentences,
                                                    allowed_distance_average,
                                                    False)
  ground_truth_vectors = result["ground_truth_vectors"]
  ground_truth_gradients = result["ground_truth_gradients"]
  ground_truth_vectors_per_fold.append(ground_truth_vectors)
  ground_truth_gradients_per_fold.append(ground_truth_gradients)

  # evaluate with evaluation dataset
  amount_urls = 0
  for cat, urls in evaluation_dataset.items():
    amount_urls += len(urls)
  print("Evaluating on " + str(amount_urls) + " urls...")
  classifier.set_parameters(ground_truth_vectors, max_amount_of_sentences)
  classifying_result = classifier.classify_bulk(evaluation_dataset)

  # create metrics
  metrics_result = create_metrics(classifying_result)

  # save results
  results_per_fold["fold " + str(fold_number + 1)] = {
      "classifying_result": classifying_result,
      "metrics": metrics_result,
      "max_amount_of_sentences": max_amount_of_sentences
  }

# generate overall metrics
overall_metrics = {}

# iterate through the metrics of all folds and add them up
for fold, outputs in results_per_fold.items():
  for category, values in outputs["metrics"].items():
    if category in overall_metrics:
      overall_metrics[category]["precision"] += values["precision"]
      overall_metrics[category]["recall"] += values["recall"]
      overall_metrics[category]["f1"] += values["f1"]
    else:
      overall_metrics[category] = {
          "precision": values["precision"],
          "recall": values["recall"],
          "f1": values["f1"]
      }

# devide by k to get average values
for category, values in overall_metrics.items():
  values["precision"] = values["precision"] / k
  values["recall"] = values["recall"] / k
  values["f1"] = values["f1"] / k

final_result = {
    "results_per_fold": results_per_fold,
    "overall_metrics": overall_metrics
}

with open("assets/" + logger.file_prefix + "_evaluation_result.json",
          "x",
          encoding="utf-8") as f:
  f.write(json.dumps({"parameters": parameters, "results": final_result}))

with open("assets/" + logger.file_prefix +
          "_evaluation_ground_truth_vectors_per_fold.json",
          "x",
          encoding="utf-8") as f:
  f.write(
      json.dumps({
          "parameters": parameters,
          "ground_truth_vectors_per_fold": ground_truth_vectors_per_fold
      }))

with open("assets/" + logger.file_prefix +
          "_evaluation_ground_truth_gradients_per_fold.json",
          "x",
          encoding="utf-8") as f:
  f.write(
      json.dumps({
          "parameters": parameters,
          "ground_truth_gradients_per_fold": ground_truth_gradients_per_fold
      }))

if use_adaptive_amount_of_sentences:
  with open("assets/" + logger.file_prefix +
            "_sentence_gradients_per_fold.json",
            "x",
            encoding="utf-8") as f:
    f.write(
        json.dumps({
            "parameters": parameters,
            "sentence_gradients_per_fold": sentence_gradients_per_fold
        }))

# measure time
stop = timeit.default_timer()
runtime = round(stop - start)
print("Runtime: " + str(runtime) + "s")
logger.log_info("MAIN", "Runtime: " + str(runtime) + "s")
