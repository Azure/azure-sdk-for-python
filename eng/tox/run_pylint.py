from subprocess import check_call
import argparse
import os
import logging
import sys

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
rcFileLocation = os.path.join(root_dir, "pylintrc")
lint_plugin_path = os.path.join(root_dir, "scripts/pylint_custom_plugin")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run pylint against target folder. Add a local custom plugin to the path prior to execution."
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_module",
        help="The target module on disk.",
        required=True,
    )

    args = parser.parse_args()

    # sys.path.insert(0, os.path.abspath(lint_plugin_path))


    # logging.info(os.path.abspath(lint_plugin_path))
    # logging.info(sys.path)
    # exit(1)

    check_call(
        [sys.executable, "-m", "pylint", "--rcfile={}".format(rcFileLocation), "--output-format=parseable", os.path.join(args.target_module, "azure")]
    )
