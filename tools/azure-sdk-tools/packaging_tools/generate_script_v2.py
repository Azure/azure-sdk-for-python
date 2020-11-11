import argparse
import json
import logging
from pathlib import Path
import tempfile

from .swaggertosdk.SwaggerToSdkCore import (
    CONFIG_FILE,
)
from .generate_sdk import generate

_LOGGER = logging.getLogger(__name__)


def main(generate_input, generate_output):
    with open(generate_input, "r") as reader:
        data = json.load(reader)

    spec_folder = data['specFolder']
    input_readme = data["relatedReadmeMdFiles"][0]

    relative_path_readme = str(Path(spec_folder, input_readme))

    generate(
        CONFIG_FILE,
        ".",
        [],
        relative_path_readme,
        spec_folder,
        force_generation=True
    )

    result = {}
    with open(generate_output, "w") as writer:
        json.dump(result, writer)

def generate_main():
    """Main method"""

    parser = argparse.ArgumentParser(
        description='Build SDK using Autorest, offline version.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('generate_input',
                        help='Generate input file path')
    parser.add_argument('generate_output',
                        help='Generate output file path')
    parser.add_argument("-v", "--verbose",
                        dest="verbose", action="store_true",
                        help="Verbosity in INFO mode")
    parser.add_argument("--debug",
                        dest="debug", action="store_true",
                        help="Verbosity in DEBUG mode")

    args = parser.parse_args()
    main_logger = logging.getLogger()
    if args.verbose or args.debug:
        logging.basicConfig()
        main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    main(args.generate_input, args.generate_output)

if __name__ == "__main__":
    generate_main()
