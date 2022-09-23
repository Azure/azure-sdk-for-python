import imp
import logging
from logging import Logger
from ci_tools.variables import get_log_directory, in_ci
import os
import datetime
from subprocess import run

from requests import Session

LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO').upper())


def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%dT%H.%M.%S")


def initialize_logger(path: str) -> Logger:
    """
    Used to initialize a logger for external use. This method results in a logger that will automatically
    save a copy of the log into the .log directory.
    """
    logger = logging.getLogger(path)
    logger.setLevel(level=LOGLEVEL)

    # create file handler which will generate additional logging uploadable by CI
    if in_ci():
        logfile = os.path.abspath(os.path.join(get_log_directory(), path + f"{now()}.log"))
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        
    return logger

def get_log_file(prefix: str = "") -> str:
    """
    Used to retrieve a file pointer that can be used by subprocess.run
    """
    logdirectory = get_log_directory()
    logfile = os.path.abspath(os.path.join(logdirectory, prefix + f"{now()}.log"))
    if not os.path.exists(logdirectory):
        os.mkdir(logdirectory)
    
    return logfile


def run_logged(*args, prefix="", **kwargs):
    logfile = get_log_file(prefix)
        
    with open(logfile, 'w') as log_output:
        run(*args, **kwargs, stdout=log_output)


__all__ = [
    "initialize_logger",
    "run_logged"
]

# class SessionLogger:
#     def __init__(self):
#         pass

#     def initialize_logger(self, path: str) -> Logger:
#         logfile = os.path.abspath(os.path.join(get_log_directory(), path, f"{datetime.datetime.now().isoformat()}"))
#         logger = logging.getLogger(path)
#         logger.setLevel(logging.DEBUG)

#         # create file handler which logs even debug messages
#         fh = logging.FileHandler(logfile)
#         fh.setLevel(logging.DEBUG)
#         logger.addHandler(fh)
        
#         return logger