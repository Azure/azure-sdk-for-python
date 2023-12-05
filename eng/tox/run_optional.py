import argparse
from ci_tools.scenario.generation import prepare_and_test_optional


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""This entrypoint provides automatic invocation of the 'optional' requirements for a given package. View the pyproject.toml within the targeted package folder to see configuration.""",
    )

    parser.add_argument("-t", "--target", dest="target", help="The target package path", required=True)

    parser.add_argument(
        "-o",
        "--optional",
        dest="optional",
        help="The target environment. If not provided, all optional environments will be run.",
        required=False,
    )

    parser.add_argument(
        "--temp",
        dest="temp_dir",
        help="The temp directory this script will work in.",
        required=False,
    )

    args, _ = parser.parse_known_args()
    exit(prepare_and_test_optional(mapped_args=args))