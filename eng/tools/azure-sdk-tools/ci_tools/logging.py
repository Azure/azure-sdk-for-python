import logging
import argparse
import os

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

    # parse LOG_LEVEL environment variable
    log_level_env = os.getenv("LOG_LEVEL")
    if not args.log_level and log_level_env:
        numeric_level = getattr(logging, log_level_env.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logger.setLevel(numeric_level)

    # Propagate logger config globally if needed
    logging.basicConfig(level=numeric_level, format=fmt)
