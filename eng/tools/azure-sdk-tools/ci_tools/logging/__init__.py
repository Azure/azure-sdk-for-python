import os
import datetime
import subprocess
import argparse
import logging

from logging import Logger

from ci_tools.variables import get_log_directory, in_ci

LOGLEVEL = getattr(logging, os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger("azure-sdk-tools")


def configure_logging(args: argparse.Namespace, fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s") -> None:
    """
    Configures the shared logger. Should be called **once** at startup.
    """
    # use cli arg > log level arg > env var

    if hasattr(args, "quiet") and args.quiet:
        numeric_level = logging.ERROR
    elif hasattr(args, "verbose") and args.verbose:
        numeric_level = logging.DEBUG
    elif not getattr(args, "log_level", None):
        numeric_level = getattr(logging, os.environ.get("LOGLEVEL", "INFO").upper())
    else:
        numeric_level = getattr(logging, args.log_level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {numeric_level}")
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


def run_logged_to_file(*args, prefix="", **kwargs):
    logfile = get_log_file(prefix)

    with open(logfile, "w") as log_output:
        subprocess.run(*args, **kwargs, stdout=log_output, stderr=log_output)


def run_logged(cmd: list[str], cwd: str, check: bool, should_stream_to_console: bool):
    """
    Runs a command, logging output to subprocess.PIPE or streaming live to console based on log level.

    Regardless of `should_stream_to_console`, if the command fails, the captured output will be logged.
    """
    try:
        if should_stream_to_console:
            # Stream live, no capturing
            return subprocess.run(cmd, cwd=cwd, check=check, text=True, stderr=subprocess.STDOUT)
        else:
            # Capture merged output but don't print unless there's a failure
            return subprocess.run(
                cmd, cwd=cwd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}")
        if e.stdout:
            logger.error(f"\n{e.stdout.strip()}")
        raise


__all__ = ["initialize_logger", "run_logged_to_file", "run_logged"]
