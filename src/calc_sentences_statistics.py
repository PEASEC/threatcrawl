"""A script to calculate sentence statistics for the dataset
    Input needs to be the output of get_amount_sentences_per_document.py
"""

from time import strftime, gmtime
import json
from math import floor

################################################################################
sentences_input_file = "assets/20221204_234532_amount_sentences_per_document.json"
output_file = "assets/" + strftime("%Y%m%d_%H%M%S",
                                   gmtime()) + "_sentence_statistics.json"
################################################################################

# load the sentences per document file
with open(sentences_input_file, encoding="utf-8") as f:
  data = json.load(f)

amount_sentences = data["amount_sentences"]

stats = {}

# iterate through all categories
for cat, entries in amount_sentences.items():
  lowest = 99999999
  highest = 0
  summe = 0
  median_list = []
  median = 0
  # iterate through all sentences
  for entry in entries:
    # create a list of sentence lengths to create median
    median_list.append(entry["amount_sentences"])
    # create sum for average
    summe += entry["amount_sentences"]
    # remember highest and lowest values
    if lowest > entry["amount_sentences"]:
      lowest = entry["amount_sentences"]
    if highest < entry["amount_sentences"]:
      highest = entry["amount_sentences"]
  # calculate median (middle if uneven amount, average of middle two if even)
  median_list.sort()
  if len(median_list) % 2 != 0:
    median = median_list[floor(len(median_list) / 2)]
  else:
    median = (median_list[floor(len(median_list) / 2)] +
              median_list[floor((len(median_list) / 2) - 1)]) / 2

  # save values for category
  stats[cat] = {
      "lowest": lowest,
      "highest": highest,
      "average": summe / len(entries),
      "median": median
  }

result = {}
result["parameters"] = data["parameters"]
result["parameters"]["amount_sentences_filename"] = sentences_input_file
result["statistics"] = stats

# save values
with open(output_file, "x", encoding="utf-8") as f:
  f.write(json.dumps(result))
