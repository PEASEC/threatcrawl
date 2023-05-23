Module cybersecurity-crawler.src.crawler_bot.monitoring
=======================================================
Module for monitoring thread states in a global context to check for
stopping conditions

Classes
-------

`GlobalMonitor(logger: src.crawler_bot.custom_logging.Logger)`
:   Monitors all thread states, all threads need to report to this controller
    
    Attributes:
      retrievers_running: amount of retreivers that are running
      retrievers_idle: amount of retrievers that are idle
      retrievers_stopped: amount of retrievers that are stopped
      extractors_running: amount of extractors that are running
      extractors_idle: amount of extractors that are idle
      extractors_stopped: amount of extractors that are stopped
    
    Inits GlobalMonitor

    ### Methods

    `extractor_continue(self, previous_state: cybersecurity-crawler.src.crawler_bot.monitoring.ThreadState) ‑> None`
    :   Function for extractors to signal that they are continuing
        
        Arg:
          previous_state: state of extractor before changing state
        
        Returns:
          None

    `extractor_idle(self, previous_state: cybersecurity-crawler.src.crawler_bot.monitoring.ThreadState) ‑> None`
    :   Function for extractors to signal that they are idle
        
        Arg:
          previous_state: state of extractor before changing state
        
        Returns:
          None

    `extractor_stop(self, previous_state: cybersecurity-crawler.src.crawler_bot.monitoring.ThreadState) ‑> None`
    :   Function for extractors to signal that they have stopped
        
        Arg:
          previous_state: state of extractor before changing state
        
        Returns:
          None

    `extractors_all_idle_or_stopped(self) ‑> bool`
    :   Checks if all extractors are either idle or stopped
        
        Returns:
          bool that shows if all extractors are idle/stopped

    `register_extractor_thread(self, extractor_thread) ‑> None`
    :   Registers the actual thread in the monitor
        
        Args:
          extractor_thread: an instance of the extractor in its own thread
        
        Returns:
          None

    `register_retriever_thread(self, retriever_thread) ‑> None`
    :   Registers the actual thread in the monitor
        
        Args:
          retriever_thread: an instance of the retriever in its own thread
        
        Returns:
          None

    `retriever_continue(self, previous_state: cybersecurity-crawler.src.crawler_bot.monitoring.ThreadState) ‑> None`
    :   Function for retrievers to signal that they are continuing
        
        Arg:
          previous_state: state of retriever before changing state
        
        Returns:
          None

    `retriever_idle(self, previous_state: cybersecurity-crawler.src.crawler_bot.monitoring.ThreadState) ‑> None`
    :   Function for retrievers to signal that they are idle
        
        Arg:
          previous_state: state of retriever before changing state
        
        Returns:
          None

    `retriever_stop(self, previous_state: cybersecurity-crawler.src.crawler_bot.monitoring.ThreadState) ‑> None`
    :   Function for retrievers to signal that they have stopped
        
        Arg:
          previous_state: state of retriever before changing state
        
        Returns:
          None

    `retrievers_all_idle_or_stopped(self) ‑> bool`
    :   Checks if all retrievers are idle or stopped
        
        Returns:
          boolean indicating if all retrievers are idle or stopped

    `stop_everything(self, reason: str) ‑> None`
    :   Stopps the execution of all threads
        
        Args:
          reason: reason for stopping the whole program
        
        Returns:
          None

`ThreadState(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Enum to define the thread state

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `IDLE`
    :

    `RUNNING`
    :

    `STOPPED`
    :