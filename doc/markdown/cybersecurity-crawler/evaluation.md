Module cybersecurity-crawler.evaluation
=======================================
Evaluation of the classifier module

Functions
---------

    
`create_metrics(classification_results: dict) ‑> dict`
:   creates Precision, Recall and F1 Score for the result
    
    Args:
      result: list of categoriezed entries
    
    Returns:
      dictionary of all metrics for each category

    
`cut_dataset(input_dataset: dict, amount_slices: int) ‑> list[dict]`
:   Cuts the dataset in amount_slices equally parts per category
    
    Args:
      input_dataset: the whole dataset (urls grouped by category)
      amount_slices: the amount of parts that should be returned
    
    Returns:
      a list of amount_slices dictionaries

    
`merge_datasets(set1: dict, set2: dict) ‑> dict`
:   merges two datasets by combining the lists for each key to one list
    
    Args:
      set1: dict with dataset items for each category
      set2: dict with dataset items for each category
    
    Returns:
      one combined dict