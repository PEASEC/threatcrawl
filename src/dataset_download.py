"""Example of how to download a url list to create a dataset

This is NOT needed for running the crawler but rather for creating new ground
  truth vectors or evaluating the classifier

The url list has to be a csv file (url, category), first line will be ignored

"""
import timeit
from time import strftime, gmtime
from crawler_bot.tools import load_url_list, download_url_list
import json

################################################################################
url_list_input_file = "assets/20221204_url_list.csv"
dataset_output_file = "assets/" + strftime("%Y%m%d_%H%M%S",
                                           gmtime()) + "_dataset.json"
################################################################################

# start timer
start = timeit.default_timer()

# load the url list
url_list = load_url_list(url_list_input_file)

# download the url list
dataset = download_url_list(url_list)

# extract dataset properties as parameters
urls_per_category = {}
for category, entries in dataset.items():
  urls_per_category[category] = len(entries)
parameters = {
    "urls_per_category": urls_per_category,
    "url_list_filename": url_list_input_file
}
result = {"parameters": parameters, "dataset": dataset}

# save the dataset
with open(dataset_output_file, "x", encoding="utf-8") as f:
  f.write(json.dumps(result))

# measure time
stop = timeit.default_timer()
runtime = round(stop - start)
print("Runtime: " + str(runtime) + "s")
