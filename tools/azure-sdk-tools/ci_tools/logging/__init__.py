import logging
from logging import Logger
from ci_tools.variables import get_log_directory, in_ci
import os
import datetime
from subprocess import run

LOGLEVEL = getattr(logging, os.environ.get("LOGLEVEL", "INFO").upper())


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
        logdirectory = os.path.join(get_log_directory(), path)
        if not os.path.exists(logdirectory):
            os.makedirs(logdirectory)
        logfile = os.path.abspath(os.path.join(logdirectory, f"{now()}.log"))
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

    return logger


def get_log_file(prefix: str = "") -> str:
    """
    Used to retrieve a file pointer that can be used by subprocess.run
    """
    logdirectory = os.path.join(get_log_directory(), prefix)
    logfile = os.path.abspath(os.path.join(logdirectory, f"{now()}.log"))
    if not os.path.exists(logdirectory):
        os.makedirs(logdirectory)

    return logfile


def run_logged(*args, prefix="", **kwargs):
    logfile = get_log_file(prefix)

    with open(logfile, "w") as log_output:
        run(*args, **kwargs, stdout=log_output, stderr=log_output)


__all__ = ["initialize_logger", "run_logged"]
