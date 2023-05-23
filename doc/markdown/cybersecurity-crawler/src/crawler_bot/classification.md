Module cybersecurity-crawler.src.crawler_bot.classification
===========================================================
The module that handles all classification related tasks

Classes
-------

`Classifier(id_number: int, logger: src.crawler_bot.custom_logging.Logger)`
:   Handles the classification of websites using CyBert
    
    Attributes:
      id_number: id of this specific instance of classifier
      name: name of this specific instance of classifier for logging
      logger: instance of the logging module
      model: the used model for classifying
      tokenizer: the used tokenizer
      myconfig: specific config for trafilatura
      ground_truth_vectors: the used ground_truth_vectors to compare against
      max_amount_of_sentences: max amount of used sentences of each document
    
    Inits Classifier
    
    Args:
      id_number: the id of the classifier
      logger: instance of the custom logging module

    ### Methods

    `calculate_ideal_amount_of_sentences(self, dataset: dict, ignore_categories: bool) ‑> (<class 'int'>, <class 'dict'>)`
    :   Calculates the ideal amount of sentences per document for classifiying
          them
        
        Args:
          dataset: the dataset as dictionary
          ignore_categories: decides if categories are used or only one vector is
                              created
        
        Returns:
          the calculated amount of sentences that should be used and the sentence
          gradients so they can be saved

    `classify_bulk(self, dataset: dict) ‑> str`
    :   Classifies the given dataset and returns metrics
        
        Args:
          dataset: a dict of a dataset
        
        Returns:
          metrics

    `create_token_vectors(self, tokens_tensor: <built-in method tensor of type object at 0x7ff1fba2f9a0>, segments_tensor: <built-in method tensor of type object at 0x7ff1fba2f9a0>) ‑> list[float]`
    :   Creates the token vectors for each token in a sentence
        
        Args:
          tokens_tensor: a tensor containing the tokens of a sentence
          segments_tensor: a tensor containing the segment tensor
        
        Returns:
          a list of vectors, one for each word of the input sentence

    `generate_ground_truth_vectors(self, dataset: dict, ignore_categories: bool = False, max_amount_of_sentences: int = 0, allowed_distance_average: bool = False, get_most_important_sentences: bool = False) ‑> dict`
    :   Generates new ground truth vectors from a csv file
            category not_relevant will be ignored
        
        Args:
          dataset_filename: filename of the csv file
          ignore_categories: decides if categories are used or only one vector is
                              created
          max_amount_of_sentences: amount of sentences considered for
                                    classification (0=all)
          allowed_distance_average: decides if allowed_distance is calculated as
            average distance of each datapoint from ground truth vector or as the
            maximum distance from all points (per category)
          get_most_important_sentences: additionally returns dict of most important
            sentence per document
        
        Returns:
          a dict containing the generated vectors and one containing the gradients
            for each step and optionally the most important sentences

    `get_sentence_vector(self, sentence) ‑> list[float]`
    :   Creates a embedding vector for the input sentence
        
        Args:
          sentence: a string for which an embedding is needed
        
        Returns:
          a vector which is an embedding of the input sentence

    `get_text_vector(self, html: str, max_sentences: int = 0, generate_sentence_gradients: bool = False, get_most_important_sentence: bool = False) ‑> dict`
    :   Creates an embedding vector for a whole document
        
        Args:
          html: the document for which an embedding is needed
          max_sentences: amount of sentences that should be considered, 0 = all
          generate_sentence_gradients: if True, a gradient of the document vector
            after every sentence is calculated and returned
          get_most_important_sentence: returns the most informative sentence
            (sentence with least difference to overall embedding)
        
        Returns:
          a dict with text_vector and the sentence_gradients list if requested

    `is_relevant(self, url: str, html_document: str) ‑> dict`
    :   Calculates the differences of the input document and decides if it is
            relevant or not
        
        Args:
          url: url of the html document
          html_document: the html document to be classified
        
        Returns:
          a dict containing "relevant" (bool), distances (to each category vector),
          relative distances (to each category vector) and guessed_category

    `load_parameters_from_file(self, filename: str) ‑> None`
    :   Loads the ground truth vectors and max_amount_of_sentences from the given
            file
        
        Args:
          filename: name of the file which holds the ground truth vectors
        
        Returns:
          None

    `pre_process_sentence(self, sentence) ‑> tuple[torch._VariableFunctionsClass.tensor, torch._VariableFunctionsClass.tensor]`
    :   Preprocesses the given sentence to use it as input for a BERT classifier
        
        Args:
          sentence: string of a sentence to be prepared
        
        Returns:
          a tuple of tensors to be used as input for a BERT classifier

    `set_parameters(self, ground_truth_vectors: dict, max_amount_of_sentences: int) ‑> None`
    :   Sets new ground truth vectors and the amount of sentences to be used for
            classification
        
        Args:
          ground_truth_vectors: a dict containing the new ground truth vectors
          max_sentences: defines the max amount of sentences
        
        Returns:
          None