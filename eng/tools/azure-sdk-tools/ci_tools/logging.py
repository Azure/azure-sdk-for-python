import logging
import argparse
import os

logger = logging.getLogger("azure-sdk-tools")

def configure_logging(
    level: str = "INFO",
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
) -> None:
    """
    Configures the shared logger. Should be called **once** at startup.
    """
    
    numeric_level = getattr(logging, level.upper(), None)

    # parse cli arg, and compare to numeric level?
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", default=False, help="Enable quiet mode (only shows ERROR logs)")
    parser.add_argument("--verbose", default=False, help="Enable verbose mode (shows DEBUG logs)")
    parser.add_argument("--log-level", default="INFO", help="Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    
    args = parser.parse_args()
    if args.log_level:
        numeric_level = getattr(logging, args.log_level.upper(), None)

    # parse LOG_LEVEL environment variable
    log_level_env = os.getenv("LOG_LEVEL")
    if log_level_env:
        numeric_level = getattr(logging, log_level_env.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logger.setLevel(numeric_level)

    # Propagate logger config globally if needed
    logging.basicConfig(level=numeric_level, format=fmt)
