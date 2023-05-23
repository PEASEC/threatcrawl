"""Module for monitoring thread states in a global context to check for
stopping conditions
"""
from enum import Enum

from src.crawler_bot.config import NUM_EXTRACTOR_THREADS, NUM_RETRIEVER_THREADS
from src.crawler_bot import custom_logging


class ThreadState(Enum):
  """Enum to define the thread state
"""
  RUNNING = 1
  STOPPED = 2
  IDLE = 3


class GlobalMonitor:
  """Monitors all thread states, all threads need to report to this controller

  Attributes:
    retrievers_running: amount of retreivers that are running
    retrievers_idle: amount of retrievers that are idle
    retrievers_stopped: amount of retrievers that are stopped
    extractors_running: amount of extractors that are running
    extractors_idle: amount of extractors that are idle
    extractors_stopped: amount of extractors that are stopped
"""

  def __init__(self, logger: custom_logging.Logger):
    """Inits GlobalMonitor

    """
    self.retrievers_running = NUM_RETRIEVER_THREADS
    self.retrievers_idle = 0
    self.retrievers_stopped = 0
    self.extractors_running = NUM_EXTRACTOR_THREADS
    self.extractors_idle = 0
    self.extractors_stopped = 0
    self.logger = logger
    self.extractor_threads = []
    self.retriever_threads = []

    self.logger.log_info("Global Monitor", "initialized")

  def retriever_idle(self, previous_state: ThreadState) -> None:
    """Function for retrievers to signal that they are idle

    Arg:
      previous_state: state of retriever before changing state

    Returns:
      None
    """
    # only act if retriever was running
    if previous_state == ThreadState.RUNNING:
      self.retrievers_running -= 1
      self.retrievers_idle += 1

  def register_extractor_thread(self, extractor_thread) -> None:
    """Registers the actual thread in the monitor

    Args:
      extractor_thread: an instance of the extractor in its own thread

    Returns:
      None
    """
    self.extractor_threads.append(extractor_thread)
    self.logger.log_debug(self.name, "extractor registered")

  def register_retriever_thread(self, retriever_thread) -> None:
    """Registers the actual thread in the monitor

    Args:
      retriever_thread: an instance of the retriever in its own thread

    Returns:
      None
    """
    self.retriever_threads.append(retriever_thread)
    self.logger.log_debug(self.name, "retriever registered")

  def retriever_continue(self, previous_state: ThreadState) -> None:
    """Function for retrievers to signal that they are continuing

    Arg:
      previous_state: state of retriever before changing state

    Returns:
      None
    """
    # only act if retriever was idle
    if previous_state == ThreadState.IDLE:
      self.retrievers_running += 1
      self.retrievers_idle -= 1

  def retriever_stop(self, previous_state: ThreadState) -> None:
    """Function for retrievers to signal that they have stopped

    Arg:
      previous_state: state of retriever before changing state

    Returns:
      None
    """
    # act accordingly to previous state
    if previous_state == ThreadState.RUNNING:
      self.retrievers_running -= 1
    else:  # -> he was idle
      self.retrievers_idle -= 1
    self.retrievers_stopped += 1

  def retrievers_all_idle_or_stopped(self) -> bool:
    """Checks if all retrievers are idle or stopped

    Returns:
      boolean indicating if all retrievers are idle or stopped
    """
    return (self.retrievers_stopped +
            self.retrievers_idle) == NUM_RETRIEVER_THREADS

  def extractor_idle(self, previous_state: ThreadState) -> None:
    """Function for extractors to signal that they are idle

    Arg:
      previous_state: state of extractor before changing state

    Returns:
      None
    """
    # only act if extractor was running
    if previous_state == ThreadState.RUNNING:
      self.extractors_running -= 1
      self.extractors_idle += 1

  def extractor_continue(self, previous_state: ThreadState) -> None:
    """Function for extractors to signal that they are continuing

    Arg:
      previous_state: state of extractor before changing state

    Returns:
      None
    """
    # only act if extractor was idle
    if previous_state == ThreadState.IDLE:
      self.extractors_running += 1
      self.extractors_idle -= 1

  def extractor_stop(self, previous_state: ThreadState) -> None:
    """Function for extractors to signal that they have stopped

    Arg:
      previous_state: state of extractor before changing state

    Returns:
      None
    """
    # act accordingly to previous state
    if previous_state == ThreadState.RUNNING:
      self.extractors_running -= 1
    else:  #-> extractor was idle
      self.extractors_idle -= 1
    self.extractors_stopped += 1

  def extractors_all_idle_or_stopped(self) -> bool:
    """Checks if all extractors are either idle or stopped

    Returns:
      bool that shows if all extractors are idle/stopped
    """
    return (self.extractors_idle +
            self.extractors_stopped) == NUM_EXTRACTOR_THREADS

  def stop_everything(self, reason: str) -> None:
    """Stopps the execution of all threads

    Args:
      reason: reason for stopping the whole program

    Returns:
      None
    """
    self.logger.log_critical(self.name, "Stopping everything (" + reason + ")")
    for thread in self.extractor_threads:
      thread.stop_extractor(reason)
    for thread in self.retriever_threads:
      thread.stop_retriever(reason)
