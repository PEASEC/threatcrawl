"""A script to extract the amount of sentences per document in the dataset
"""

import json
import trafilatura
from re import split
from time import strftime, gmtime

################################################################################
dataset_file = "assets/20221204_233927_dataset.json"
output_file = "assets/" + strftime(
    "%Y%m%d_%H%M%S", gmtime()) + "_amount_sentences_per_document.json"
################################################################################

# load the dataset
with open(dataset_file, encoding="utf-8") as f:
  data = json.load(f)

dataset = data["dataset"]

amount_sentences = {}

# iterate through all categories
for cat, entries in dataset.items():

  # iterate through all documents
  for entry in entries:
    # extract main content using trafilatura
    main_content = trafilatura.extract(entry["document"])

    # split the main content into single sentences by splitting at
    # newline or sentence ending signs
    uncleaned_sentences = split(r"\n|!|\.|\?", main_content)

    sentences = []

    # remove empty sentences and sentences that only consist of single words
    for sentence in uncleaned_sentences:
      if sentence.strip() == "":
        continue
      if len(sentence.strip()) <= 1:
        continue
      sentences.append(sentence.strip())

    # save amount of sentences per document
    if cat in amount_sentences:
      amount_sentences[cat].append({
          "url": entry["url"],
          "amount_sentences": len(sentences)
      })
    else:
      amount_sentences[cat] = [{
          "url": entry["url"],
          "amount_sentences": len(sentences)
      }]

# save parameters
parameters = {}
parameters["dataset_filename"] = dataset_file
parameters["dataset"] = data["parameters"]

# create result object
result = {}
result["parameters"] = parameters
result["amount_sentences"] = amount_sentences

# save result
with open(output_file, "x", encoding="utf-8") as f:
  f.write(json.dumps(result))
