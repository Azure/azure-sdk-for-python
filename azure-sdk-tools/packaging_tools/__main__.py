import argparse
import logging

from . import build_packaging

parser = argparse.ArgumentParser(
    description='Packaging tools for Azure SDK for Python',
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('--output', '-o',
                    dest='output', default='.',
                    help='Output dir, should be SDK repo folder. [default: %(default)s]')
parser.add_argument("--debug",
                    dest="debug", action="store_true",
                    help="Verbosity in DEBUG mode")
parser.add_argument('package_name', help='The package name.')

args = parser.parse_args()

main_logger = logging.getLogger()
logging.basicConfig()
main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

build_packaging(args.package_name, args.output)