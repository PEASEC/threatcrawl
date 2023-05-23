"""A collection of useful tools
"""
import re
from urllib.parse import urlparse
import numpy as np
import requests
import json
from math import floor

DOMAIN_PLUS_TLD_FORMAT = re.compile(r"[^.]+\.[^.]+$")
MAIN_DOMAIN_ONLY_FORMAT = re.compile(r"([^.]+)\.[^.]+$")


def extract_main_domain(url: str) -> str:
  """Extracts the domain out of an URL
      Example: www.google.de -> google

  Args:
    url: string of the url

  Returns:
    domain as string
  """
  netloc = urlparse(url).netloc
  x = re.search(MAIN_DOMAIN_ONLY_FORMAT, netloc)
  try:
    result = x.group(1)
    return result
  except:
    print("problem with " + str(url))
    return None


def extract_main_domain_plus_tld(url: str) -> str:
  """Extracts the domain plus TLD from an URL
      Example: www.google.de -> google.de

  Args:
    url: string of the url

  Returns:
    domain plus TLD as string
  """
  netloc = urlparse(url).netloc
  x = re.search(DOMAIN_PLUS_TLD_FORMAT, netloc)
  try:
    result = x.group()
    return result
  except:
    print("problem with " + str(url))
    return None


def unit_vector(vector):
  """Transforms a vector into its unit vector

  Args:
    vector: list of vector components

  Returns:
    a numpy array of the unit vector
  """
  return vector / np.linalg.norm(vector)


def angle_between(v1, v2) -> float:
  """Calculates the angle between two vectors

  Args:
    v1: first vector as list[float]
    v2: second vector as list[float]

  Returns:
    a float number, representing the angle between v1 and v2
    """
  return np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))


def print_progress_bar(current_step: int, total_steps: int) -> None:
  """Prints a progress bar into the command line

  Args:
    current_step: how much is done
    total_steps: what is the amount of total steps to do

  Returns:
    None
  """
  progress = floor((current_step / total_steps) * 100)
  progress_bar = "#" * progress
  print(f"\r [{progress_bar}] {progress}%", end="")


def load_url_list(filename: str,
                  ignore_categories: bool = False) -> (dict, int):
  """loads the url list from a csv file into a dict

  Args:
    filename: the name of the csv file

  Returns:
    a dict with the url list (urls per category)
  """
  if filename is None:
    print("filename is empty")
    return None

  # read csv into dictionary
  with open(filename, encoding="utf-8") as x:
    # remove first line
    csv_content = x.readline()
    csv_content = x.readlines()

  urls_per_category = {}

  for entry in csv_content:
    url, category = [a.strip() for a in entry.split(",")]
    if ignore_categories:
      category = "ground_truth"
    if category in urls_per_category:
      urls_per_category[category].append(url)
    else:
      urls_per_category[category] = [url]

  return urls_per_category


def download_url_list(url_list: dict) -> dict:
  """Downloads a given url_list and returns a dataset


  Args:
    url_list: dict of the url_list with urls per category

  Returns:
    a dict with all downloaded documents like:
      {"category1": [{"url": url1, "document": document1},
                      {"url": url2, "document", document2},
                    ...],
        "category2": [{"url": url4, "document": document4},
                        {"url": url5, "document": document5},
                      ...]
      }
  """
  if url_list is None:
    print("empty url list")
    return None

  result = {}
  amount_urls = 0

  for category, urls in url_list.items():
    amount_urls += len(urls)

  print("downloading " + str(amount_urls) + " urls...")

  i = 0

  for category, urls in url_list.items():
    for url in urls:
      i += 1
      try:
        print_progress_bar(i, amount_urls)

        x = requests.get(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"
            },
            timeout=5)
        if x.status_code != 200:
          print("error with url", url, "status code is " + str(x.status_code))
          continue
        if category in result:
          result[category].append({"url": url, "document": x.text})
        else:
          result[category] = [{"url": url, "document": x.text}]
      except Exception as e:
        print("\nerror with url", url, "(" + str(e) + ")")
        continue

  print("\n")
  return result


def load_dataset(filename: str) -> dict:
  """loads a dataset from file (like the one created by download_url_list)

  Args:
    filename: name of the csv file containing the dataset

  Returns:
    a dict of the dataset
  """
  with open(filename, encoding="utf-8") as f:
    dataset = json.load(f)

  return dataset
