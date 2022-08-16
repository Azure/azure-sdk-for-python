import argparse
import logging
import os
import sys

from . import build_packaging

_LOGGER = logging.getLogger(__name__)

_epilog = """This script will automatically build the TOML configuration file with default value if it doesn't exist.
"""

parser = argparse.ArgumentParser(
    description="Packaging tools for Azure SDK for Python",
    formatter_class=argparse.RawTextHelpFormatter,
    epilog=_epilog,
)
parser.add_argument(
    "--output",
    "-o",
    dest="output",
    default=".",
    help="Output dir, should be SDK repo folder. [default: %(default)s]",
)
parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")
parser.add_argument(
    "--build-conf",
    dest="build_conf",
    action="store_true",
    help="Build a default TOML file, with package name, fake pretty name, as beta package and no doc page. Do nothing if the file exists, remove manually the file if needed.",
)
parser.add_argument(
    "--jenkins",
    dest="jenkins",
    action="store_true",
    help="In Jenkins mode, try to find what to generate from Jenkins env variables. Package names are then optional.",
)
parser.add_argument("package_names", nargs="*", help="The package name.")

args = parser.parse_args()

main_logger = logging.getLogger()
logging.basicConfig()
main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

if not args.package_names and not args.jenkins:
    raise ValueError("At least one package name or Jenkins mode is required")

try:
    build_packaging(
        args.output,
        os.environ.get("GH_TOKEN", None),
        args.jenkins,
        args.package_names,
        build_conf=args.build_conf,
    )
except Exception as err:
    if args.debug:
        _LOGGER.exception(err)
    else:
        _LOGGER.critical(err)
    sys.exit(1)
