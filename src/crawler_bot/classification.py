"""The module that handles all classification related tasks
"""

from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
import trafilatura
from trafilatura.settings import use_config
from re import split
import json
from math import ceil

from src.crawler_bot.tools import unit_vector, angle_between, print_progress_bar
from src.crawler_bot.custom_logging import Logger

ML_MODEL = "bert-base-uncased"  # or "CySecBERT" or "all-mpnet-base-v2" (SentenceBERT)


class Classifier:
  """Handles the classification of websites using CyBert

  Attributes:
    id_number: id of this specific instance of classifier
    name: name of this specific instance of classifier for logging
    logger: instance of the logging module
    model: the used model for classifying
    tokenizer: the used tokenizer
    myconfig: specific config for trafilatura
    ground_truth_vectors: the used ground_truth_vectors to compare against
    max_amount_of_sentences: max amount of used sentences of each document
"""

  def __init__(self, id_number: int, logger: Logger):
    """Inits Classifier

    Args:
      id_number: the id of the classifier
      logger: instance of the custom logging module
    """
    self.id_number = id_number
    self.name = "Classifier#" + str(self.id_number)
    self.logger = logger

    if ML_MODEL == "CySecBERT":
      self.model = BertModel.from_pretrained("markusbayer/CySecBERT", output_hidden_states=True)
      self.tokenizer = AutoTokenizer.from_pretrained("markusbayer/CySecBERT")

    elif ML_MODEL == "bert-base-uncased":
      self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
      self.model = AutoModel.from_pretrained("bert-base-uncased",
                                             output_hidden_states=True)
    elif ML_MODEL == "all-mpnet-base-v2":
      self.model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    self.myconfig = use_config("src/crawler_bot/custom_trafilatura_config.cfg")
    self.logger.log_debug(self.name, "initialized")

  def pre_process_sentence(self, sentence) -> tuple[torch.tensor, torch.tensor]:
    """Preprocesses the given sentence to use it as input for a BERT classifier

    Args:
      sentence: string of a sentence to be prepared

    Returns:
      a tuple of tensors to be used as input for a BERT classifier
    """
    # add start token and seperator token at the end
    marked_text = "[CLS] " + sentence + " [SEP]"
    # tokenize the text
    tokenized_text = self.tokenizer.tokenize(marked_text)

    # cut away everything over 512 tokens (while keeping last token)
    if len(tokenized_text) > 512:
      tokenized_text = tokenized_text[0:511] + [tokenized_text[-1]]

    # transform into ids
    indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokenized_text)
    # create segment ids, we only have 1 sentence -> only one vector with ones
    segments_ids = [1] * len(indexed_tokens)

    self.logger.log_debug(self.name,
                          "amount of tokens: " + str(len(segments_ids)))

    # create torch tensors
    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensor = torch.tensor([segments_ids])

    return tokens_tensor, segments_tensor

  def create_token_vectors(self, tokens_tensor: torch.tensor,
                           segments_tensor: torch.tensor) -> list[float]:
    """Creates the token vectors for each token in a sentence

    Args:
      tokens_tensor: a tensor containing the tokens of a sentence
      segments_tensor: a tensor containing the segment tensor

    Returns:
      a list of vectors, one for each word of the input sentence
    """
    # freeze model
    with torch.no_grad():
      outputs = self.model(tokens_tensor, segments_tensor)
      # first layer is just input layer -> remove it
      hidden_states = outputs[2]  #[1:]

    # extract the embeddings by concatenating the last 4 layers
    token_embeddings = hidden_states[-1]
    token_embeddings = torch.cat([hidden_states[i] for i in [-1, -2, -3, -4]],
                                 dim=-1)
    # converting torchtensors to lists
    token_vectors = [token_embed.tolist() for token_embed in token_embeddings]

    return token_vectors[0]

  def get_sentence_vector(self, sentence) -> list[float]:
    """Creates a embedding vector for the input sentence

    Args:
      sentence: a string for which an embedding is needed

    Returns:
      a vector which is an embedding of the input sentence
    """

    if ML_MODEL == "all-mpnet-base-v2":
      return self.model.encode(sentence)

    tokens_tensor, segments_tensor = self.pre_process_sentence(sentence)
    token_vectors = self.create_token_vectors(tokens_tensor, segments_tensor)
    # create sentence vector from token vectors
    sentence_vector = []
    for index in range(len(token_vectors[0])):
      vector_element = 0
      for token_vector in token_vectors:
        vector_element += token_vector[index]
      sentence_vector.append(vector_element)

    return sentence_vector

  def get_text_vector(self,
                      html: str,
                      max_sentences: int = 0,
                      generate_sentence_gradients: bool = False,
                      get_most_important_sentence: bool = False) -> dict:
    """Creates an embedding vector for a whole document

    Args:
      html: the document for which an embedding is needed
      max_sentences: amount of sentences that should be considered, 0 = all
      generate_sentence_gradients: if True, a gradient of the document vector
        after every sentence is calculated and returned
      get_most_important_sentence: returns the most informative sentence
        (sentence with least difference to overall embedding)

    Returns:
      a dict with text_vector and the sentence_gradients list if requested
    """
    # use trafilatura to extract main content
    main_content = trafilatura.extract(html, config=self.myconfig)

    if main_content is None:
      self.logger.log_warning(
          self.name, "Trafilatura was not able to extract the main content")
      return None

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

    self.logger.log_debug(self.name,
                          "split into " + str(len(sentences)) + " sentences")

    if len(sentences) < 1:
      return None

    # cut away unwanted sentences if too long
    if len(sentences) > max_sentences > 0:
      sentences = sentences[:max_sentences + 1]
      self.logger.log_debug(
          self.name, "only " + str(max_sentences) + " sentences are used")

    sentence_vectors = []
    # generate a vector for every sentence
    i = 0
    for sentence in sentences:
      i += 1
      self.logger.log_debug(
          self.name, "embedding sentence " + str(i) + "/" + str(len(sentences)))
      sentence_vectors.append(self.get_sentence_vector(sentence))

    # create a whole vector by adding all sentence vectors
    text_vector = []
    # create 0 vector with correct length
    text_vector = [0 for _ in sentence_vectors[0]]

    if generate_sentence_gradients:
      sentence_gradients = []
      first = True
      # add up all sentences and create gradient after each step
      for sentence_vector in sentence_vectors:
        if first:
          text_vector = sentence_vector
          first = False
        else:
          old_text_vector = text_vector
          text_vector = [sum(i) for i in zip(text_vector, sentence_vector)]
          gradient = angle_between(unit_vector(old_text_vector),
                                   unit_vector(text_vector))
          sentence_gradients.append(gradient)

      result = {
          "text_vector": text_vector,
          "sentence_gradients": sentence_gradients
      }
    else:
      # just add up all sentence vectors
      for sentence_vector in sentence_vectors:
        text_vector = [sum(i) for i in zip(text_vector, sentence_vector)]
      result = {"text_vector": text_vector}

    if get_most_important_sentence:
      index_min = len(sentence_vectors) - 1
      min_diff = 99999
      for index, sentence_vector in enumerate(sentence_vectors):
        current_diff = angle_between(unit_vector(sentence_vector),
                                     unit_vector(result["text_vector"]))
        if current_diff < min_diff:
          min_diff = current_diff
          index_min = index
      result["most_important_sentence"] = sentences[index_min]

    return result

  def load_parameters_from_file(self, filename: str) -> None:
    """Loads the ground truth vectors and max_amount_of_sentences from the given
        file

    Args:
      filename: name of the file which holds the ground truth vectors

    Returns:
      None
    """
    with open(filename, encoding="utf-8") as x:
      data = json.load(x)
    self.ground_truth_vectors = data["ground_truth_vectors"]
    self.max_amount_of_sentences = data["parameters"]["max_amount_of_sentences"]

  def set_parameters(self, ground_truth_vectors: dict,
                     max_amount_of_sentences: int) -> None:
    """Sets new ground truth vectors and the amount of sentences to be used for
        classification

    Args:
      ground_truth_vectors: a dict containing the new ground truth vectors
      max_sentences: defines the max amount of sentences

    Returns:
      None

    """
    self.ground_truth_vectors = ground_truth_vectors
    self.max_amount_of_sentences = max_amount_of_sentences

  def is_relevant(self, url: str, html_document: str) -> dict:
    """Calculates the differences of the input document and decides if it is
        relevant or not

    Args:
      url: url of the html document
      html_document: the html document to be classified

    Returns:
      a dict containing "relevant" (bool), distances (to each category vector),
      relative distances (to each category vector) and guessed_category
    """
    error_result = {
        "relevant": False,
        "distances": {},
        "relative_distances": {},
        "guessed_category": "not_relevant"
    }

    if not hasattr(self, "ground_truth_vectors"):
      self.logger.log_critical(self.name, "Ground truth vectors not loaded")
      self.monitor.stop_everything("Ground truth vectors not loaded")
      return error_result
    if not hasattr(self, "max_amount_of_sentences"):
      self.logger.log_critical(self.name, "Max amount of sentences not set")
      self.monitor.stop_everything("Max amount of sentences not set")
      return error_result

    if html_document == "" or url == "":
      return error_result

    # get embedding
    embedding_result = self.get_text_vector(html_document,
                                            self.max_amount_of_sentences, False,
                                            False)

    if embedding_result is None:
      self.logger.log_error(self.name, "cant get embedding for " + url)
      return error_result

    # create unitvector
    embedding = unit_vector(embedding_result["text_vector"])

    distances = {}
    relative_distances = {}
    relevant = False
    guessed_category = "not_relevant"
    smallest_distance = 99999

    # calculate distance and relative distance for every category
    for category, ground_truth in self.ground_truth_vectors.items():
      distance = angle_between(embedding, ground_truth["embedding"])
      distances[category] = distance
      relative_distances[category] = distance / ground_truth["allowed_distance"]
      # document is relevant, now check to which cat it has the lowest relative distance
      if distance <= ground_truth["allowed_distance"]:
        relevant = True
        if relative_distances[category] < smallest_distance:
          smallest_distance = relative_distances[category]
          guessed_category = category

    result = {
        "relevant": relevant,
        "distances": distances,
        "relative_distances": relative_distances,
        "guessed_category": guessed_category
    }

    return result

  def calculate_ideal_amount_of_sentences(
      self, dataset: dict, ignore_categories: bool) -> (int, dict):
    """Calculates the ideal amount of sentences per document for classifiying
      them

    Args:
      dataset: the dataset as dictionary
      ignore_categories: decides if categories are used or only one vector is
                          created

    Returns:
      the calculated amount of sentences that should be used and the sentence
      gradients so they can be saved
    """

    amount_documents = 0
    sentence_gradients = {}
    gradient_limit = 0.02
    counter = 1

    self.logger.log_info(self.name, "calculating ideal amount of sentences")

    # get amount of all relevant documents
    for category, items in dataset.items():
      if category != "not_relevant":
        amount_documents += len(items)

    # iterate through all relevant documents and retrieve the sentence gradients
    for category, items in dataset.items():
      if category == "not_relevant":
        continue
      # if we ignore labels, every label other than not_relevant is relevant
      if ignore_categories:
        category = "relevant"

      sentence_gradients[category] = []
      # get embedding and gradients for each document with max. amount of
      # sentences
      for item in items:
        print_progress_bar(counter, amount_documents)
        embedding_result = self.get_text_vector(item["document"], 0, True,
                                                False)
        sentence_gradients[category].append({
            "url": item["url"],
            "sentence_gradients": embedding_result["sentence_gradients"]
        })
        counter += 1

    # calculate the ideal amount of sentences by averaging the amount of
    # sentences where gradient < gradient_limit
    indices_gradient_limit_reached = []
    for category, items in sentence_gradients.items():
      for item in items:
        # set searched index to last element
        index_gradient_limit_reached = len(item["sentence_gradients"]) - 1
        # look for index where gradient gets below gradient limit
        for index, value in enumerate(item["sentence_gradients"]):
          if value <= gradient_limit:
            index_gradient_limit_reached = index
            break
        indices_gradient_limit_reached.append(index_gradient_limit_reached)

    # get ideal value by averaging the ideal amount of sentences of each
    # document
    ideal_amount_of_sentences = ceil(
        sum(indices_gradient_limit_reached) /
        len(indices_gradient_limit_reached))

    return ideal_amount_of_sentences, sentence_gradients

  def generate_ground_truth_vectors(
      self,
      dataset: dict,
      ignore_categories: bool = False,
      max_amount_of_sentences: int = 0,
      allowed_distance_average: bool = False,
      get_most_important_sentences: bool = False) -> dict:
    """Generates new ground truth vectors from a csv file
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
    """

    # generate embedding for every url (still grouped by category)
    ground_truth_vectors = {}
    single_embeddings = {}
    ground_truth_gradient = {}
    result = {}

    counter = 1
    amount_documents = 0

    # get amount of all relevant documents
    for category, items in dataset.items():
      if category != "not_relevant":
        amount_documents += len(items)

    if get_most_important_sentences:
      most_important_sentences = {}

    # process all documents: generate embedding and add it to the category
    # embedding
    for category, items in dataset.items():
      if category == "not_relevant":
        continue
      # if categories should be ignored, replace category with one big
      # one (ground_truth)
      if ignore_categories:
        category = "ground_truth"
      for item in items:
        print_progress_bar(counter, amount_documents)
        self.logger.log_debug(
            self.name, "generating embedding " + str(counter) + "/" +
            str(amount_documents) + " (" + item["url"] + ")")
        try:
          # get embedding
          embedding_result = self.get_text_vector(item["document"],
                                                  max_amount_of_sentences,
                                                  False,
                                                  get_most_important_sentences)

          # add new vector to the existing one to generate category embedding
          if category in ground_truth_vectors:
            old_ground_truth = ground_truth_vectors[category]
            new_ground_truth = [
                sum(i)
                for i in zip(embedding_result["text_vector"], old_ground_truth)
            ]
            ground_truth_vectors[category] = new_ground_truth

            # calculate the gradient to see how much the vector changed
            gradient = angle_between(unit_vector(old_ground_truth),
                                     unit_vector(new_ground_truth))
            if category in ground_truth_gradient:
              ground_truth_gradient[category].append(gradient)
            else:
              ground_truth_gradient[category] = [gradient]

          else:
            ground_truth_vectors[category] = embedding_result["text_vector"]

          # create the unit vector and save the single document embedding to
          # calculate allowed_distance later
          embedding = unit_vector(embedding_result["text_vector"])
          if category in single_embeddings:
            single_embeddings[category].append({
                "url": item["url"],
                "embedding": embedding
            })
          else:
            single_embeddings[category] = [{
                "url": item["url"],
                "embedding": embedding
            }]
          # add most important sentences to result if requested
          if get_most_important_sentences:
            self.logger.log_debug(self.name, "adding most important sentences")
            if category in most_important_sentences:
              most_important_sentences[category].append({
                  "url":
                      item["url"],
                  "most_important_sentence":
                      embedding_result["most_important_sentence"]
              })
            else:
              most_important_sentences[category] = [{
                  "url":
                      item["url"],
                  "most_important_sentence":
                      embedding_result["most_important_sentence"]
              }]
        except Exception as e:
          self.logger.log_warning(
              self.name, "problem with " + item["url"] + "(" + str(e) + ")")

        counter += 1
    print("\n")

    if get_most_important_sentences:
      result["most_important_sentences"] = most_important_sentences

    self.logger.log_debug(self.name, "ground truth vectors generated")

    # normalize all vectors for easier processing
    for category, vector in ground_truth_vectors.items():
      ground_truth_vectors[category] = {
          "embedding": unit_vector(vector).tolist()
      }

    self.logger.log_debug(self.name, "ground truth vectors normalized")

    # calculate allowed distance for each url from the calculated ground truth
    # vectors per category
    allowed_distances = {}

    if allowed_distance_average:
      # allowed distance is calculated as average distance from ground truth
      for category, entries in single_embeddings.items():
        allowed_distances[category] = 0
        # add up all distances per category
        for entry in entries:
          distance = angle_between(entry["embedding"],
                                   ground_truth_vectors[category]["embedding"])
          allowed_distances[category] += distance

        # devide by amount of documents
        if len(entries) > 0:
          allowed_distances[category] = allowed_distances[category] / len(
              entries)
        else:
          allowed_distances[category] = 0
    else:
      # allowed distance is calculated as max distance from ground truth
      for category, entries in single_embeddings.items():
        allowed_distances[category] = 0
        for entry in entries:
          distance = angle_between(entry["embedding"],
                                   ground_truth_vectors[category]["embedding"])
          # remember the greatest seen distance
          if distance > allowed_distances[category]:
            allowed_distances[category] = distance

    # save in ground truth vectors
    for category, allowed_distance in allowed_distances.items():
      ground_truth_vectors[category]["allowed_distance"] = allowed_distance

    result["ground_truth_vectors"] = ground_truth_vectors
    result["ground_truth_gradients"] = ground_truth_gradient

    return result

  def classify_bulk(self, dataset: dict) -> str:
    """Classifies the given dataset and returns metrics

    Args:
      dataset: a dict of a dataset

    Returns:
      metrics

    """
    result = {}
    self.logger.log_debug(self.name, "starting to classify bulk")

    amount_documents = 0
    counter = 0

    for category, items in dataset.items():
      amount_documents += len(items)

    if amount_documents == 0:
      return {}

    # iterate through all items
    for category, items in dataset.items():
      for item in items:
        counter += 1
        self.logger.log_debug(self.name, "classifiying " + item["url"])
        print_progress_bar(counter, amount_documents)

        # calculate distances for the document
        classification_result = self.is_relevant(item["url"], item["document"])

        if category in result:
          result[category].append({
              "url": item["url"],
              "classification_result": classification_result
          })
        else:
          result[category] = [{
              "url": item["url"],
              "classification_result": classification_result
          }]
    print("\n")
    return result
