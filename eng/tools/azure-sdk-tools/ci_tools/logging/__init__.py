import logging
from logging import Logger
from ci_tools.variables import get_log_directory, in_ci
import os
import datetime
from subprocess import run
import argparse

LOGLEVEL = getattr(logging, os.environ.get("LOGLEVEL", "INFO").upper())

logger = logging.getLogger("azure-sdk-tools")

def configure_logging(
    args: argparse.Namespace,
    level: str = "INFO",
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
) -> None:
    """
    Configures the shared logger. Should be called **once** at startup.
    """
    
    numeric_level = getattr(logging, level.upper(), None)

    # parse cli arg
    if args.quiet:
        numeric_level = logging.ERROR
    elif args.verbose:
        numeric_level = logging.DEBUG

    # use log level environment variable
    if not args.log_level:
        numeric_level = getattr(logging, LOGLEVEL.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logger.setLevel(numeric_level)

    # Propagate logger config globally if needed
    logging.basicConfig(level=numeric_level, format=fmt)


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
