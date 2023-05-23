"""This module contains all functionalities for logging
"""
from enum import Enum
from time import strftime, gmtime
from contextlib import ExitStack

import os


class LogLevel(Enum):
  """Enum to define different log levels
"""
  DEBUG = 1
  INFO = 2
  WARNING = 3
  ERROR = 4
  CRITICAL = 5


class Logger(ExitStack):
  """Controlls the logging for the Crawler

  Attributes:
    log_level: sets the level of the logging which then decides what statements
                get printed in the logfile
"""

  def __init__(self, log_level: LogLevel, filename: str):
    """Inits Logger

    Args:
      log_level: sets the level of the logging which then decides what
                  statements get printed in the logfile
    """
    super().__init__()
    self.log_level = log_level
    self.filename = filename
    self.file_prefix = strftime("%Y%m%d_%H%M%S", gmtime())

    if not os.path.isdir('logs'):
      os.makedirs('logs')

    self.logfile = self.enter_context(
        open("logs/" + self.file_prefix + "_" + self.filename + ".log",
             mode="w",
             encoding="utf-8"))
    self.log_info("Logging Module", "initialized")

  def _get_log_prefix(self) -> str:
    """Creates the log prefix

    Returns:
      a log prefix looking like [2020-06-24 10:13:43]
    """
    return "[" + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "]"

  def log_debug(self, caller: str, log_string: str) -> None:
    """Writes a log with debug log level

    Args:
      caller: string/name of the caller object, gets printed before the message
      log_string: the string that needs to be logged

    Returns:
      None
    """
    if self.log_level.value <= LogLevel.DEBUG.value:
      self.logfile.write(self._get_log_prefix() + " DEBUG " + caller + " " +
                         log_string + "\n")
      self.logfile.flush()

  def log_info(self, caller: str, log_string: str) -> None:
    """Writes a log with info log level

    Args:
      caller: string/name of the caller object, gets printed before the message
      log_string: the string that needs to be logged

    Returns:
      None
    """
    if self.log_level.value <= LogLevel.INFO.value:
      self.logfile.write(self._get_log_prefix() + " INFO " + caller + " " +
                         log_string + "\n")
      self.logfile.flush()

  def log_warning(self, caller: str, log_string: str) -> None:
    """Writes a log with warning log level

    Args:
      caller: string/name of the caller object, gets printed before the message
      log_string: the string that needs to be logged

    Returns:
      None
    """
    if self.log_level.value <= LogLevel.WARNING.value:
      self.logfile.write(self._get_log_prefix() + " WARNING " + caller + " " +
                         log_string + "\n")
      self.logfile.flush()

  def log_error(self, caller: str, log_string: str) -> None:
    """Writes a log with error log level

    Args:
      caller: string/name of the caller object, gets printed before the message
      log_string: the string that needs to be logged

    Returns:
      None
    """
    if self.log_level.value <= LogLevel.ERROR.value:
      self.logfile.write(self._get_log_prefix() + " ERROR " + caller + " " +
                         log_string + "\n")
      self.logfile.flush()

  def log_critical(self, caller: str, log_string: str) -> None:
    """Writes a log with critical log level

    Args:
      caller: string/name of the caller object, gets printed before the message
      log_string: the string that needs to be logged

    Returns:
      None
    """
    if self.log_level.value <= LogLevel.CRITICAL.value:
      self.logfile.write(self._get_log_prefix() + " CRITICAL " + caller + " " +
                         log_string + "\n")
      self.logfile.flush()
