Module cybersecurity-crawler.src.crawler_bot.tools
==================================================
A collection of useful tools

Functions
---------

    
`angle_between(v1, v2) ‑> float`
:   Calculates the angle between two vectors
    
    Args:
      v1: first vector as list[float]
      v2: second vector as list[float]
    
    Returns:
      a float number, representing the angle between v1 and v2

    
`download_url_list(url_list: dict) ‑> dict`
:   Downloads a given url_list and returns a dataset
    
    
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

    
`extract_main_domain(url: str) ‑> str`
:   Extracts the domain out of an URL
        Example: www.google.de -> google
    
    Args:
      url: string of the url
    
    Returns:
      domain as string

    
`extract_main_domain_plus_tld(url: str) ‑> str`
:   Extracts the domain plus TLD from an URL
        Example: www.google.de -> google.de
    
    Args:
      url: string of the url
    
    Returns:
      domain plus TLD as string

    
`load_dataset(filename: str) ‑> dict`
:   loads a dataset from file (like the one created by download_url_list)
    
    Args:
      filename: name of the csv file containing the dataset
    
    Returns:
      a dict of the dataset

    
`load_url_list(filename: str, ignore_categories: bool = False) ‑> (<class 'dict'>, <class 'int'>)`
:   loads the url list from a csv file into a dict
    
    Args:
      filename: the name of the csv file
    
    Returns:
      a dict with the url list (urls per category)

    
`print_progress_bar(current_step: int, total_steps: int) ‑> None`
:   Prints a progress bar into the command line
    
    Args:
      current_step: how much is done
      total_steps: what is the amount of total steps to do
    
    Returns:
      None

    
`unit_vector(vector)`
:   Transforms a vector into its unit vector
    
    Args:
      vector: list of vector components
    
    Returns:
      a numpy array of the unit vector