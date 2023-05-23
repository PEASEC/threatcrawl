Module cybersecurity-crawler.src.crawler_bot.custom_logging
===========================================================
This module contains all functionalities for logging

Classes
-------

`LogLevel(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Enum to define different log levels

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CRITICAL`
    :

    `DEBUG`
    :

    `ERROR`
    :

    `INFO`
    :

    `WARNING`
    :

`Logger(log_level: cybersecurity-crawler.src.crawler_bot.custom_logging.LogLevel, filename: str)`
:   Controlls the logging for the Crawler
    
    Attributes:
      log_level: sets the level of the logging which then decides what statements
                  get printed in the logfile
    
    Inits Logger
    
    Args:
      log_level: sets the level of the logging which then decides what
                  statements get printed in the logfile

    ### Ancestors (in MRO)

    * contextlib.ExitStack
    * contextlib._BaseExitStack
    * contextlib.AbstractContextManager
    * abc.ABC

    ### Methods

    `log_critical(self, caller: str, log_string: str) ‑> None`
    :   Writes a log with critical log level
        
        Args:
          caller: string/name of the caller object, gets printed before the message
          log_string: the string that needs to be logged
        
        Returns:
          None

    `log_debug(self, caller: str, log_string: str) ‑> None`
    :   Writes a log with debug log level
        
        Args:
          caller: string/name of the caller object, gets printed before the message
          log_string: the string that needs to be logged
        
        Returns:
          None

    `log_error(self, caller: str, log_string: str) ‑> None`
    :   Writes a log with error log level
        
        Args:
          caller: string/name of the caller object, gets printed before the message
          log_string: the string that needs to be logged
        
        Returns:
          None

    `log_info(self, caller: str, log_string: str) ‑> None`
    :   Writes a log with info log level
        
        Args:
          caller: string/name of the caller object, gets printed before the message
          log_string: the string that needs to be logged
        
        Returns:
          None

    `log_warning(self, caller: str, log_string: str) ‑> None`
    :   Writes a log with warning log level
        
        Args:
          caller: string/name of the caller object, gets printed before the message
          log_string: the string that needs to be logged
        
        Returns:
          None